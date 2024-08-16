from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from functools import partial
from itertools import repeat
from queue import Empty, Full, Queue
from threading import Thread
from typing import Callable

import grpc

from ._base import _EntityProvider, _HasStub, _PlayerProvider
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._types import DIRECTION
from ._util import ThreadSafeSingeltonCache
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

MAX_QUEUE_SIZE: int = 100  # maximum number of backlogged events per event type

WARN_DROPPED_INTERVAL: int = (
    30  # the interval in which a warning should be printed on dropped events
)

# TODO: make events frozen? <-- almost 2.5x slower than non-frozen events (use slots?)
# TODO: make tests for events
# also, put direction in utils?


@dataclass(
    frozen=True, slots=True, order=True
)  # TODO: order does not work between different Type of events?
class Event:
    timestamp: float = field(
        init=False, repr=False, compare=True, hash=False, default_factory=time.time
    )  #: The timestamp when the event was received. Will be used for sorting events by default


@dataclass(frozen=True, slots=True)
class PlayerJoinEvent(Event):
    player: Player  #: The :class:`Player` who connected to the server


@dataclass(frozen=True, slots=True)
class PlayerLeaveEvent(Event):
    player: Player  #: The :class:`Player` who disconnected from the server


@dataclass(frozen=True, slots=True)
class PlayerDeathEvent(Event):
    player: Player  #: The :class:`Player` who died
    deathMessage: str  #: The death message the player received


@dataclass(frozen=True, slots=True)
class ChatEvent(Event):
    player: Player  #: The :class:`Player` who sent the chat message
    message: str  #: The message sent in chat


@dataclass(frozen=True, slots=True)
class BlockHitEvent(Event):
    player: Player  #: The :class:`Player` who clicked on a block
    right_hand: bool  #: Whether the player used their right hand instead of their left
    held_item: str  #: The item held in that players hand that clicked the block
    pos: Vec3  #: The :class:`Vec3` position of the block that was clicked
    face: DIRECTION  #: The face/side of the block that was clicked


@dataclass(frozen=True, slots=True)
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


class _EventPoller:
    def __init__(self, handler: _EventHandler, key: int) -> None:
        self.handler = handler
        self.key = key
        self.stream: grpc.Future = handler._stub.getEventStream(
            pb.EventStreamRequest(eventType=key)
        )
        self.events: Queue[Event] = Queue(MAX_QUEUE_SIZE)
        self.event_drop_time = 0.0
        self.callbacks: list[Callable[[Event], None]] = []
        self.thread = Thread(
            target=self._poll, name=f"EventPoller-EventType-{self.key}", daemon=True
        )
        self.thread_cancelled = False
        logging.debug(f"_EventPoller: __init__: Starting thread poller for key {key}")
        self.thread.start()

    def _cleanup(self) -> None:
        logging.debug("EventPoller: _cleanup: cancelling stream...")
        self.thread_cancelled = True
        self.stream.cancel()
        logging.debug("EventPoller: _cleanup: joining thread...")
        self.thread.join()
        logging.debug("EventPoller: _cleanup: joined thread")

    def _poll(self) -> None:
        logging.debug("EventPoller: _poll: started polling")
        try:
            for rpc_event in self.stream:
                if self.thread_cancelled:
                    logging.info("EventPoller: _poll: stream was cancelled via variable")
                    return
                event = self._parse_to_event(rpc_event)
                if self.callbacks:
                    for callback in self.callbacks:
                        logging.debug(f"EventPoller: _poll: callback with event: {rpc_event}")
                        callback(event)
                else:
                    logging.debug(f"EventPoller: _poll: putting event in queue: {rpc_event}")
                    try:
                        self.events.put(event, block=False, timeout=None)
                    except Full:
                        if self.event_drop_time + WARN_DROPPED_INTERVAL < time.time():
                            logging.warn(
                                f"EventPoller: _poll: dropping events due to backlog in queue for key {self.key}"
                            )
                            self.event_drop_time = time.time()
        except grpc.RpcError as e:
            if hasattr(e, "code") and callable(e.code) and e.code() == grpc.StatusCode.CANCELLED:
                if self.thread_cancelled:
                    logging.debug("EventPoller: _poll: stream was cancelled")
                else:
                    logging.error("EventPoller: _poll: stream was cancelled, but NOT via cleanup!")
                    raise e
            else:
                logging.error(f"EventPoller: _poll: stream was closed by RpcError: {e}")
                raise e

    def _parse_to_event(self, res: pb.Event) -> Event:
        event: Event | None = None
        if res.type != self.key:
            raise ValueError(
                f"Received event type was not of type {self.key}, was {res.type} instead"
            )
        match res.type:
            case pb.EVENT_PLAYER_JOIN:
                event = PlayerJoinEvent(
                    self.handler._get_or_create_player(res.playerMsg.trigger.name)
                )
            case pb.EVENT_PLAYER_LEAVE:
                event = PlayerLeaveEvent(
                    self.handler._get_or_create_player(res.playerMsg.trigger.name)
                )
            case pb.EVENT_PLAYER_DEATH:
                event = PlayerDeathEvent(
                    self.handler._get_or_create_player(res.playerMsg.trigger.name),
                    res.playerMsg.message,
                )
            case pb.EVENT_CHAT_MESSAGE:
                event = ChatEvent(
                    self.handler._get_or_create_player(res.playerMsg.trigger.name),
                    res.playerMsg.message,
                )
            case pb.EVENT_BLOCK_HIT:
                event = BlockHitEvent(
                    self.handler._get_or_create_player(res.blockHit.trigger.name),
                    res.blockHit.right_hand,
                    res.blockHit.item_type,
                    Vec3(res.blockHit.pos.x, res.blockHit.pos.y, res.blockHit.pos.z),
                    res.blockHit.face,
                )
            case pb.EVENT_PROJECTILE_HIT:
                target = (
                    self.handler._get_or_create_player(res.projectileHit.player.name)
                    if res.projectileHit.HasField("player")
                    else (
                        self.handler._get_or_create_entity(res.projectileHit.entity.id)
                        if res.projectileHit.HasField("entity")
                        else res.projectileHit.block
                    )
                )
                if isinstance(target, Entity):
                    target._type = res.projectileHit.entity.type
                event = ProjectileHitEvent(
                    self.handler._get_or_create_player(res.projectileHit.trigger.name),
                    target,
                    res.projectileHit.projectile,
                    Vec3(
                        res.projectileHit.pos.x,
                        res.projectileHit.pos.y,
                        res.projectileHit.pos.z,
                    ),
                    res.projectileHit.face if res.projectileHit.face else None,
                )
            case _:
                logging.error(str(res))
                raise NotImplementedError(f"Event with code {res.type} is not supported yet")
        return event


class _EventHandler(_HasStub, _EntityProvider, _PlayerProvider):
    """Certain events that happen on the server can be captured and reacted to.

    These events are:

    - :class:`PlayerJoinEvent` triggers whenever a player connects to the server

    - :class:`PlayerLeaveEvent` triggers whenever a player disconnects from the server

    - :class:`PlayerDeathEvent` triggers whenever a player dies

    - :class:`ChatEvent` triggers whenever someone writes in the chat.
      This does *not* trigger for ``/``-commands, :func:`postToChat`, direct console messages or other server logs.

    - :class:`BlockHitEvent` triggers whenever a player clicks on a block with either the left or right mouse button.
      It does *not* matter whether the click had any in game effect as long as the block was reachable for the player.

    - :class:`ProjectileHitEvent` triggers whenever a player hits *anything* with a projectile.
      This does *not* trigger for projectiles that were not fired by the player, such as by dispensers or skeletons.

    There are two mutually exclusive ways how to receive events:

    - **Polling:**

      The corresponding poll*EventName* function can be called to receive the events of that type since the last call to that poll function.

      .. code-block:: python

         for event in mc.pollProjectileHitEvents():
             if event.target_player:
                 mc.postToChat(f"Player {event.player} hit player {event.target_player} with {event.projectile_type}")

    - **Register Callback:**

      The corresponding registerCallback*EventName* function can register another function as a callback.
      That function is then called for each event as it arrives with the event as the argument to the callback function.
      Multiple functions can be registered for the same event, in which case the functions are called in order they were registered in.

      .. code-block:: python

         def myfunc(event):
             if event.target_player:
                 mc.postToChat(f"Player {event.player} hit player {event.target_player} with {event.projectile_type}")

         mc.registerCallbackProjectileHitEvent(myfunc)

    These methods of receiving events are mutually exclusive *for the same event type* because registering a function will also consume the events.
    Calling the poll-function for an event type where a function is registered as callback will raise a RuntimeException.

    .. note::

       In both cases, events will only be captured *after the first call* of either poll*EventName* or registerCallback*EventName*
       and indefinitly afterwards until :func:`stopEventPollingAndClearCallbacks` is called.

    """

    def __init__(self, stub: MinecraftStub) -> None:
        super().__init__(stub)
        self._poller = ThreadSafeSingeltonCache(None)  # of type dict[int, _EventPoller]

    def _cleanup(self) -> None:
        logging.debug("EventHandler: _cleanup: called...")
        for key, poller in self._poller.items():
            logging.debug(f"EventHandler: _cleanup: calling cleanup in poller with key {key}")
            poller._cleanup()
        self._poller.clear()
        logging.debug("EventHandler: _cleanup: done")

    def _get_or_create_poller(self, key: int) -> _EventPoller:
        return self._poller.get_or_create(key, partial(_EventPoller, self))

    def _poll_upto(self, key: int, max_events: int | None) -> list[Event]:
        poller = self._get_or_create_poller(key)
        if poller.callbacks:
            raise RuntimeError(f"Trying to poll key {key} while callback is registered")
        events = []
        _range = repeat(None) if max_events is None else range(max_events)
        try:
            for _ in _range:
                events.append(poller.events.get_nowait())
        except Empty:
            pass
        return events

    def pollPlayerJoinEvents(self, maximum: int | None = POLL_DEFAULT) -> list[PlayerJoinEvent]:
        """
        :param maximum: the maxmimum number of events to return, if None return all events
        :type maximum: int | None, optional
        :return: a list of events of that type since last poll, oldest first
        :rtype: list[PlayerJoinEvent]
        """
        return self._poll_upto(pb.EVENT_PLAYER_JOIN, maximum)  # type: ignore

    def pollPlayerLeaveEvents(self, maximum: int | None = POLL_DEFAULT) -> list[PlayerLeaveEvent]:
        """
        :param maximum: the maxmimum number of events to return, if None return all events
        :type maximum: int | None, optional
        :return: a list of events of that type since last poll, oldest first
        :rtype: list[PlayerLeaveEvent]
        """
        return self._poll_upto(pb.EVENT_PLAYER_LEAVE, maximum)  # type: ignore

    def pollPlayerDeathEvents(self, maximum: int | None = POLL_DEFAULT) -> list[PlayerDeathEvent]:
        """
        :param maximum: the maxmimum number of events to return, if None return all events
        :type maximum: int | None, optional
        :return: a list of events of that type since last poll, oldest first
        :rtype: list[PlayerDeathEvent]
        """
        return self._poll_upto(pb.EVENT_PLAYER_DEATH, maximum)  # type: ignore

    def pollChatEvents(self, maximum: int | None = POLL_DEFAULT) -> list[ChatEvent]:
        """
        :param maximum: the maxmimum number of events to return, if None return all events
        :type maximum: int | None, optional
        :return: a list of events of that type since last poll, oldest first
        :rtype: list[ChatEvent]
        """
        return self._poll_upto(pb.EVENT_CHAT_MESSAGE, maximum)  # type: ignore

    def pollBlockHitEvents(self, maximum: int | None = POLL_DEFAULT) -> list[BlockHitEvent]:
        """
        :param maximum: the maxmimum number of events to return, if None return all events
        :type maximum: int | None, optional
        :return: a list of events of that type since last poll, oldest first
        :rtype: list[BlockHitEvent]
        """
        return self._poll_upto(pb.EVENT_BLOCK_HIT, maximum)  # type: ignore

    def pollProjectileHitEvents(
        self, maximum: int | None = POLL_DEFAULT
    ) -> list[ProjectileHitEvent]:
        """
        :param maximum: the maxmimum number of events to return, if None return all events
        :type maximum: int | None, optional
        :return: a list of events of that type since last poll, oldest first
        :rtype: list[ProjectileHitEvent]
        """
        return self._poll_upto(pb.EVENT_PROJECTILE_HIT, maximum)  # type: ignore

    def registerCallbackPlayerJoinEvent(self, callback: Callable[[PlayerJoinEvent], None]) -> None:
        """
        :param callback: the function that should be called with the event as argument for each event of that type
        :type callback: Callable[[PlayerJoinEvent], None]
        """
        self._get_or_create_poller(pb.EVENT_PLAYER_JOIN).callbacks.append(callback)  # type: ignore

    def registerCallbackPlayerLeaveEvent(
        self, callback: Callable[[PlayerLeaveEvent], None]
    ) -> None:
        """
        :param callback: the function that should be called with the event as argument for each event of that type
        :type callback: Callable[[PlayerLeaveEvent], None]
        """
        self._get_or_create_poller(pb.EVENT_PLAYER_LEAVE).callbacks.append(callback)  # type: ignore

    def registerCallbackPlayerDeathEvents(
        self, callback: Callable[[PlayerDeathEvent], None]
    ) -> None:
        """
        :param callback: the function that should be called with the event as argument for each event of that type
        :type callback: Callable[[PlayerDeathEvent], None]
        """
        self._get_or_create_poller(pb.EVENT_PLAYER_DEATH).callbacks.append(callback)  # type: ignore

    def registerCallbackChatEvent(self, callback: Callable[[ChatEvent], None]) -> None:
        """
        :param callback: the function that should be called with the event as argument for each event of that type
        :type callback: Callable[[ChatEvent], None]
        """
        self._get_or_create_poller(pb.EVENT_CHAT_MESSAGE).callbacks.append(callback)  # type: ignore

    def registerCallbackBlockHitEvent(self, callback: Callable[[BlockHitEvent], None]) -> None:
        """
        :param callback: the function that should be called with the event as argument for each event of that type
        :type callback: Callable[[BlockHitEvent], None]
        """
        self._get_or_create_poller(pb.EVENT_BLOCK_HIT).callbacks.append(callback)  # type: ignore

    def registerCallbackProjectileHitEvent(
        self, callback: Callable[[ProjectileHitEvent], None]
    ) -> None:
        """
        :param callback: the function that should be called with the event as argument for each event of that type
        :type callback: Callable[[ProjectileHitEvent], None]
        """
        self._get_or_create_poller(pb.EVENT_PROJECTILE_HIT).callbacks.append(callback)  # type: ignore

    def stopEventPollingAndClearCallbacks(self) -> None:
        """Stops all active event capturing and clears event backlogs and registered callback functions.
        Calling a polling function or registering a callback afterwards, will start capturing events anew.
        """
        old_cache = self._poller
        self._poller = ThreadSafeSingeltonCache(None)
        logging.debug("EventHandler: clearEventsAndEventCallbacks: called")
        for key, poller in old_cache.items():
            logging.debug(
                f"EventHandler: clearEventsAndEventCallbacks: calling cleanup in poller with key {key}"
            )
            poller._cleanup()
        old_cache.clear()
        logging.debug("EventHandler: clearEventsAndEventCallbacks: done")
