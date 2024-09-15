from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from functools import partial
from itertools import repeat
from queue import Empty, Full, Queue
from threading import Thread
from typing import Callable, Generic, TypeVar

import grpc

from ._base import _EntityProvider, _PlayerProvider
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._types import DIRECTION
from ._util import ReentrantRWLock, ThreadSafeSingeltonCache
from .entity import Entity
from .player import Player
from .vec3 import Vec3

__all__ = [
    "Event",
    "PlayerJoinEvent",
    "PlayerLeaveEvent",
    "PlayerDeathEvent",
    "ChatEvent",
    "BlockHitEvent",
    "ProjectileHitEvent",
]

POLL_DEFAULT: int | None = 10  # default maximum event chunk size to return from polling functions

MAX_QUEUE_SIZE: int = 100  # maximum number of backlogged events per event type (must be set before initializing EventHandler)

WARN_DROPPED_INTERVAL: int = (
    30  # the interval in seconds after which a warning should be printed on dropped events
)

TIMEOUT_CHECK_INTERVAL: int = 3  # the interval in which :func:`get` should check the connection to the server to potentially wake up

EventType = TypeVar("EventType")


@dataclass(
    frozen=True, slots=True, order=True
)  # TODO: order does not work between different Type of events?
class Event:
    timestamp: float = field(
        init=False, repr=False, compare=True, hash=False, default_factory=time.time
    )  #: The timestamp when the event was received. Used for sorting events of same type

    @classmethod
    def _build(cls, provider: _EntityProvider | _PlayerProvider, event: pb.Event):
        raise NotImplementedError("Build is only implemented for super classes")


@dataclass(frozen=True, slots=True, order=True)
class PlayerJoinEvent(Event):
    player: Player  #: The :class:`Player` who connected to the server

    @classmethod
    def _build(cls, provider: _EntityProvider | _PlayerProvider, event: pb.Event):
        return cls(provider._get_or_create_player(event.playerMsg.trigger.name))


@dataclass(frozen=True, slots=True, order=True)
class PlayerLeaveEvent(Event):
    player: Player  #: The :class:`Player` who disconnected from the server

    @classmethod
    def _build(cls, provider: _EntityProvider | _PlayerProvider, event: pb.Event):
        return cls(provider._get_or_create_player(event.playerMsg.trigger.name))


@dataclass(frozen=True, slots=True, order=True)
class PlayerDeathEvent(Event):
    player: Player  #: The :class:`Player` who died
    deathMessage: str  #: The death message the player received

    @classmethod
    def _build(cls, provider: _EntityProvider | _PlayerProvider, event: pb.Event):
        return cls(
            provider._get_or_create_player(event.playerMsg.trigger.name),
            event.playerMsg.message,
        )


@dataclass(frozen=True, slots=True, order=True)
class ChatEvent(Event):
    player: Player  #: The :class:`Player` who sent the chat message
    message: str  #: The message sent in chat

    @classmethod
    def _build(cls, provider: _EntityProvider | _PlayerProvider, event: pb.Event):
        return cls(
            provider._get_or_create_player(event.playerMsg.trigger.name),
            event.playerMsg.message,
        )


@dataclass(frozen=True, slots=True, order=True)
class BlockHitEvent(Event):
    player: Player  #: The :class:`Player` who clicked on a block
    right_hand: bool  #: Whether the player used their right hand instead of their left
    held_item: str  #: The item held in that players hand that clicked the block
    pos: Vec3  #: The :class:`Vec3` position of the block that was clicked
    face: DIRECTION  #: The face/side of the block that was clicked

    @classmethod
    def _build(cls, provider: _EntityProvider | _PlayerProvider, event: pb.Event):
        return cls(
            provider._get_or_create_player(event.blockHit.trigger.name),
            event.blockHit.right_hand,
            event.blockHit.item_type,
            Vec3(event.blockHit.pos.x, event.blockHit.pos.y, event.blockHit.pos.z),
            event.blockHit.face,
        )


@dataclass(frozen=True, slots=True, order=True)
class ProjectileHitEvent(Event):
    player: Player  #: The :class:`Player` that shot/used the projectile
    target: (
        Player | Entity | str
    )  #: The target hit, use `target_block`, `target_entity` and `target_player` for details what was hit
    projectile_type: str  #: The type of projectile that was used
    pos: Vec3  #: The :class:`Vec3` position where the projectile hit something. In case a block was hit, this is the block position that was hit
    face: (
        DIRECTION | None
    )  #: The face/side of the block hit, None if an entity or player was hit instead

    @property
    def target_player(self) -> Player | None:
        "The target :class:`Player` if a player was hit, None otherwise"
        if isinstance(self.target, Player):
            # assert self.face is None
            return self.target
        return None

    @property
    def target_entity(self) -> Entity | None:
        "The target :class:`Entity` if a *non-player* entity was hit, None otherwise"
        if isinstance(self.target, Entity) and self.target_player is None:
            # assert self.face is None
            return self.target
        return None

    @property
    def target_block(self) -> str | None:
        "The target block id if a block was hit, None otherwise"
        if isinstance(self.target, str):
            # assert self.face is not None
            return self.target
        return None

    @classmethod
    def _build(cls, provider: _EntityProvider | _PlayerProvider, event: pb.Event):
        target = (
            provider._get_or_create_player(event.projectileHit.player.name)
            if event.projectileHit.HasField("player")
            else (
                provider._get_or_create_entity(event.projectileHit.entity.id)
                if event.projectileHit.HasField("entity")
                else event.projectileHit.block
            )
        )
        if event.projectileHit.HasField("entity"):
            target._type = event.projectileHit.entity.type
        return cls(
            provider._get_or_create_player(event.projectileHit.trigger.name),
            target,
            event.projectileHit.projectile,
            Vec3(
                event.projectileHit.pos.x,
                event.projectileHit.pos.y,
                event.projectileHit.pos.z,
            ),
            event.projectileHit.face if event.projectileHit.face else None,
        )


class SingleEventHandler(Generic[EventType]):
    """The specific event handler responsible for receiving a certain type of event in different ways."""

    def __init__(
        self,
        stub: MinecraftStub,
        provider: _EntityProvider | _PlayerProvider,
        cls: type[Event],
        key: int,
    ) -> None:
        self._stub = stub
        self._provider = provider
        self._cls = cls
        self._key = key
        self._event_queue: Queue[EventType] = Queue(MAX_QUEUE_SIZE)
        self._event_drop_time = 0.0
        self._callbacks: list[Callable[[EventType], None]] = []
        self._logp = self.__repr__() + ": "
        self._thread_lock = ReentrantRWLock()
        # * the variables _thread and _stream must only be set together (something or None)
        # * must hold _thread_lock to write, must be not None while polling thread exists
        self._thread: Thread | None = None
        # * only thread may initialize thus with lock
        # * must hold _thread_lock to write, must be not None while polling thread exists
        self._stream: grpc.Future | None = None
        # * must only be set to False or None if polling thread does *not* exist
        self._thread_cancelled: bool | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self._cls.__name__}](key={self._key})"

    def _cleanup(self) -> None:
        logging.debug(self._logp + "_cleanup: cancelling stream...")
        with self._thread_lock.for_write():
            self._thread_cancelled = True
            if self._stream:
                self._stream.cancel()
            if self._thread:
                logging.debug(self._logp + "_cleanup: joining thread...")
                self._thread.join()
                logging.debug(self._logp + "_cleanup: joined thread")
            self._thread_cancelled, self._thread, self._stream = None, None, None

    def _have_thread(self) -> None:
        with self._thread_lock.for_read():
            if self._thread is None or self._thread_cancelled:
                with self._thread_lock.for_write():
                    if self._thread is None or self._thread_cancelled:
                        if self._thread is not None:  # then _thread_cancelled is True
                            self._cleanup()
                        assert (
                            self._thread is None
                        ), f"{self._logp}Either thread was set with held read lock or cleanup failed!"
                        assert (
                            self._thread_cancelled is None
                        ), f"{self._logp}Thread cancelled was {self._thread_cancelled} in _have_thread!"
                        self._thread_cancelled, self._thread, self._stream = (
                            False,
                            Thread(
                                target=self._poll,
                                name=f"EventPollingThread-{self._key}-{self._cls.__name__}",
                                daemon=True,
                            ),
                            self._stub.getEventStream(pb.EventStreamRequest(eventType=self._key)),
                        )
                        self._thread.start()

    def _poll(self) -> None:
        try:
            logging.debug(self._logp + "_poll: started polling")
            if self._thread_cancelled:
                logging.debug(self._logp + "_poll: stream was cancelled instantly")
                return
            for rpc_event in self._stream:
                if self._thread_cancelled:  # is only set to True once! (no lock required)
                    logging.debug(self._logp + "_poll: stream was cancelled via variable")
                    return
                event = self._cls._build(self._provider, rpc_event)
                if self._callbacks:
                    for callback in self._callbacks:
                        logging.debug(self._logp + f"_poll: callback with event: {rpc_event}")
                        try:
                            callback(event)
                        except Exception as e:
                            name = (
                                callback.__name__
                                if hasattr(callback, "__name__")
                                else str(callback)
                            )
                            logging.error(
                                self._logp
                                + f"callback {name}({event}) raised error: {type(e).__name__}{e.args}"
                            )
                            # TODO: potentially propagate error to main thread? (for now, continue)
                else:
                    logging.debug(self._logp + f"_poll: putting event in queue: {rpc_event}")
                    try:
                        self._event_queue.put(event, block=False, timeout=None)
                    except Full:
                        if self._event_drop_time + WARN_DROPPED_INTERVAL < time.time():
                            logging.warning(
                                self._logp + "_poll: dropping events due to backlog in queue"
                            )
                            self._event_drop_time = time.time()
        except grpc.RpcError as e:
            if hasattr(e, "code") and callable(e.code) and e.code() == grpc.StatusCode.CANCELLED:
                if self._thread_cancelled:  # is only set to True once! (no lock required)
                    logging.debug(self._logp + "_poll: stream was cancelled")
                else:
                    logging.error(self._logp + "_poll: stream was cancelled, but NOT via cleanup!")
                    raise e
            else:
                logging.error(self._logp + f"_poll: stream was closed by RpcError: {e}")
                raise e
        finally:
            self._thread_cancelled = True

    def get(self, timeout: int | None = None) -> EventType | None:
        """Get and potentially wait for at most `timeout` seconds for the next event that was not yet received
        with either :func:`poll` or :func:`get`.
        If `timeout` is None, wait potentially indefinitely for the next event
        or until :func:`stop` is called or the connection closes.

        .. note::

           This function checks periodically (every few seconds) if :func:`stop` was called and
           whether the connection was closed while waiting.
           If either of these checks is true, then eventually this function will stop waiting and return None.

        :param timeout: time in seconds to wait for at most for next event, if None may wait indefinitely, defaults to None
        :type timeout: int | None, optional
        :raises RuntimeError: if called while a callback is registered
        :return: the next event of that type since last poll, or None if not received within `timeout` seconds
        :rtype: EventType | None
        """
        if self._callbacks:
            raise RuntimeError(self._logp + "Trying to get event while callback is registered")
        _timeout = TIMEOUT_CHECK_INTERVAL
        self._have_thread()
        while True:
            if timeout is not None:
                _timeout = TIMEOUT_CHECK_INTERVAL if timeout > TIMEOUT_CHECK_INTERVAL else timeout
                timeout = timeout - _timeout
            try:
                return self._event_queue.get(block=True, timeout=_timeout)
            except Empty:
                pass
            if timeout is not None and timeout <= 0:
                break
            with self._thread_lock.for_read():
                if self._thread_cancelled or self._thread is None:
                    break
        return None

    def get_nowait(self) -> EventType | None:
        """Identical to :func:`get` with `timeout` of 0.
        This function does not block and returns immediately.

        :raises RuntimeError: if called while a callback is registered
        :return: the next event of that type if one has already been received since last poll, else None
        :rtype: EventType | None
        """
        if self._callbacks:
            raise RuntimeError(self._logp + "Trying to get event while callback is registered")
        self._have_thread()
        try:
            return self._event_queue.get_nowait()
        except Empty:
            return None

    def poll(self, maximum: int | None = POLL_DEFAULT) -> list[EventType]:
        """Poll up to `maximum` many events received since the last time :func:`poll` or
        :func:`get` was called, or all events received since then if `maxmimum` is None.
        This function does not block and returns immediately with the events not yet
        received with either :func:`poll` or :func:`get`.

        :param maximum: the maxmimum number of events to return, if None return all received events
        :type maximum: int | None, optional
        :raises RuntimeError: if called while a callback is registered
        :return: a list of events of that type since last poll, oldest first
        :rtype: list[EventType]
        """
        if self._callbacks:
            raise RuntimeError(self._logp + "Trying to poll events while callback is registered")
        events = []
        _range = repeat(None) if maximum is None else range(maximum)
        self._have_thread()
        try:
            for _ in _range:
                events.append(self._event_queue.get_nowait())
        except Empty:
            pass
        return events

    def register(self, callback: Callable[[EventType], None]) -> None:
        """Register a callback function to run whenever an event is received
        with the event as the argument to the callback function.
        Multiple functions can be registered for the same event,
        in which case the functions are called in order they were registered in.

        .. note::

           Registered callback functions consume the received events, therefore
           polling and registering at the same time is not possible and will result
           in a RuntimeException if using :func:`poll` or :func:`get` with registered callback.

        .. note::

           No other events can be received while a callback function is being run,
           so make your callback functions non-blocking and fast if possible.

        :param callback: the function called with the event as argument for each event of that type
        :type callback: Callable[[EventType], None]
        """
        self._have_thread()
        self._callbacks.append(callback)

    def stop(self) -> None:
        """Stop the receiving of this event type and clear all events and callbacks.
        Calling either :func:`poll`, :func:`get` or :func:`register` afterwards will start receiving events again.
        """
        with self._thread_lock.for_write():
            self._cleanup()
            time.sleep(0.0001)  # give chance for other threads to return from get/poll etc.
            try:
                while True:  # clear the queue
                    self._event_queue.get_nowait()
            except Empty:
                pass
            self._callbacks = []


class EventHandler:
    """Certain events that happen on the server can be captured and reacted to.

    These events are:

    - :class:`PlayerJoinEvent` triggers whenever a player connects to the server.

    - :class:`PlayerLeaveEvent` triggers whenever a player disconnects from the server.

    - :class:`PlayerDeathEvent` triggers whenever a player dies.

    - :class:`ChatEvent` triggers whenever someone writes in the chat.
      This does *not* trigger for ``/``-commands, :func:`postToChat`, direct console messages or other server logs.

    - :class:`BlockHitEvent` triggers whenever a player clicks on a block with either the left or right mouse button.
      It does *not* matter whether the click had any in game effect as long as the block was reachable for the player.

    - :class:`ProjectileHitEvent` triggers whenever a player hits *anything* with a projectile.
      This does *not* trigger for projectiles that were not fired by the player, such as by dispensers or skeletons.

    There are two mutually exclusive ways how to receive events:

    - **Polling:**

      The :func:`poll` function on the corresponding :class:`SingleEventHandler` can be called to receive the events
      of that type since the last call to that :func:`poll` or :func:`get` function.

      .. code-block:: python

         for event in mc.events.projectile_hit.poll():
             mc.postToChat(f"Player {event.player} hit {event.target}")

      Alternatively, the :func:`get` or :func:`get_nowait` functions on the corresponding :class:`SingleEventHandler`
      can be called to get (and potentially wait) for the next event of that type.

      .. code-block:: python

         event = mc.events.projectile_hit.get(timeout=5):
         if event is None:
             mc.postToChat("Did NOT get an event within 5 seconds")
         else:
             mc.postToChat(f"Got event {event} within 5 seconds")

    - **Register Callback:**

      The :func:`register` function on the corresponding :class:`SingleEventHandler` can register another function as a callback.
      That function is then called for each event as it arrives with the event as the argument to the callback function.
      Multiple functions can be registered for the same event, in which case the functions are called in order they were registered in.

      .. code-block:: python

         def myfunc(event):
             mc.postToChat(f"Player {event.player} hit {event.target}")

         mc.events.projectile_hit.register(myfunc)

    These methods of receiving events are mutually exclusive *for the same event type* because registering a function will also consume the events.
    Calling the poll function for an event type where a function is registered as callback will raise a RuntimeException.

    .. note::

       In both cases, events will only be captured *after the first call* to either :func:`poll`, :func:`get`, :func:`get_nowait` or :func:`register`
       and indefinitely afterwards until :func:`stop` is called.

    """

    def __init__(self, stub: MinecraftStub, provider: _EntityProvider | _PlayerProvider) -> None:
        self._stub = stub
        self._provider = provider
        self._poller = ThreadSafeSingeltonCache(None)  # of type dict[int, SingleEventHandler]

    def _cleanup(self) -> None:
        logging.debug("EventHandler: _cleanup: called...")
        old_cache, self._poller = self._poller, None
        for key, poller in old_cache.items():
            logging.debug(f"EventHandler: _cleanup: calling cleanup in poller with key {key}")
            poller._cleanup()
        old_cache.clear()
        logging.debug("EventHandler: _cleanup: done")

    def _get_or_create_poller(self, key: int, cls: EventType) -> SingleEventHandler:
        return self._poller.get_or_create(
            key, partial(SingleEventHandler, self._stub, self._provider, cls)
        )

    @property
    def player_join(self) -> SingleEventHandler[PlayerJoinEvent]:
        "Receive the :class:`SingleEventHandler` for the :class:`PlayerJoinEvent` event."
        return self._get_or_create_poller(pb.EVENT_PLAYER_JOIN, PlayerJoinEvent)

    @property
    def player_leave(self) -> SingleEventHandler[PlayerLeaveEvent]:
        "Receive the :class:`SingleEventHandler` for the :class:`PlayerLeaveEvent` event."
        return self._get_or_create_poller(pb.EVENT_PLAYER_LEAVE, PlayerLeaveEvent)

    @property
    def player_death(self) -> SingleEventHandler[PlayerDeathEvent]:
        "Receive the :class:`SingleEventHandler` for the :class:`PlayerDeathEvent` event."
        return self._get_or_create_poller(pb.EVENT_PLAYER_DEATH, PlayerDeathEvent)

    @property
    def chat(self) -> SingleEventHandler[ChatEvent]:
        "Receive the :class:`SingleEventHandler` for the :class:`ChatEvent` event."
        return self._get_or_create_poller(pb.EVENT_CHAT_MESSAGE, ChatEvent)

    @property
    def block_hit(self) -> SingleEventHandler[BlockHitEvent]:
        "Receive the :class:`SingleEventHandler` for the :class:`BlockHitEvent` event."
        return self._get_or_create_poller(pb.EVENT_BLOCK_HIT, BlockHitEvent)

    @property
    def projectile_hit(self) -> SingleEventHandler[ProjectileHitEvent]:
        "Receive the :class:`SingleEventHandler` for the :class:`ProjectileHitEvent` event."
        return self._get_or_create_poller(pb.EVENT_PROJECTILE_HIT, ProjectileHitEvent)

    def stopEventPollingAndClearCallbacks(self) -> None:
        """Stops all active event capturing and clears event backlogs and registered callback functions.
        Calling a polling function or registering a callback afterwards, will start capturing events anew.
        """
        for key, poller in self._poller.items():
            poller.stop()
