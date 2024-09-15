from __future__ import annotations

import logging

import grpc

from ._base import _HasStub
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._util import deprecated
from .entity import _EntityCache
from .events import EventHandler
from .exception import raise_on_error
from .player import _PlayerCache
from .world import _DefaultWorld, _WorldHub

__all__ = ["Minecraft"]

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
# logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


class Minecraft(_DefaultWorld, _PlayerCache, _EntityCache, _WorldHub, _HasStub):
    """:class:`Minecraft` is the main object of interacting with Minecraft servers that have the mcpq-plugin_.
    When constructing the class, a ``host`` and ``port`` of the server should be provided to which a connection will be built. They default to ``"localhost"`` and ``1789`` respectively.
    All other worlds, events, entities and more are then received via the methods of that instance.

    .. _mcpq-plugin: https://github.com/mcpq/mcpq-plugin

    .. code-block:: python

       from mcpq import Minecraft
       mc = Minecraft()  # connect to localhost
       mc.postToChat("Hello Minecraft")  # send  message in chat

    .. note::

       Generally, it is sufficient to construct one :class:`Minecraft` instance per server or active connection, as this connection is thread-safe and reusable.
       However, it is also possible to connect with multiple instances from the same or different hosts at the same time.

    .. caution::

       The connection used by the server is not encrypted or otherwise secured, meaning that any man-in-the-middle can read and modify any information sent between the program and the Minecraft server.
       For security reasons it is recommended to connect from the same host as the server is running on. By default, the plugin does only allow connections from ``localhost`` to prevent access from third parties.


    The :class:`Minecraft` instance is also an *event handler*, the default :class:`World` and can be used to query :class:`Entity` and :class:`Player` objects from the server.
    Checkout the corresponding classes for more information.
    """

    def __init__(self, host: str = "localhost", port: int = 1789) -> None:
        self._addr = (host, port)
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        stub = MinecraftStub(self._channel)
        super().__init__(stub)
        self._event_handler = EventHandler(stub, self)

        # deprecated event functions
        # stop event polling is now unsafe as the underlying SingleEventHandlers were exposed (might still be around)
        self.stopEventPollingAndClearCallbacks = deprecated(
            "Call to deprecated function stopEventPollingAndClearCallbacks. Use events.stopEventPollingAndClearCallbacks instead."
        )(self.events.stopEventPollingAndClearCallbacks)
        self.pollPlayerJoinEvents = deprecated(
            "Call to deprecated function pollPlayerJoinEvents. Use events.player_join.poll instead."
        )(self.events.player_join.poll)
        self.pollPlayerLeaveEvents = deprecated(
            "Call to deprecated function pollPlayerLeaveEvents. Use events.player_leave.poll instead."
        )(self.events.player_leave.poll)
        self.pollPlayerDeathEvents = deprecated(
            "Call to deprecated function pollPlayerDeathEvents. Use events.player_death.poll instead."
        )(self.events.player_death.poll)
        self.pollChatEvents = deprecated(
            "Call to deprecated function pollChatEvents. Use events.chat.poll instead."
        )(self.events.chat.poll)
        self.pollBlockHitEvents = deprecated(
            "Call to deprecated function pollBlockHitEvents. Use events.block_hit.poll instead."
        )(self.events.block_hit.poll)
        self.pollProjectileHitEvents = deprecated(
            "Call to deprecated function pollProjectileHitEvents. Use events.projectile_hit.poll instead."
        )(self.events.projectile_hit.poll)
        self.registerCallbackPlayerJoinEvent = deprecated(
            "Call to deprecated function registerCallbackPlayerJoinEvent. Use events.player_join.register instead."
        )(self.events.player_join.register)
        self.registerCallbackPlayerLeaveEvent = deprecated(
            "Call to deprecated function registerCallbackPlayerLeaveEvent. Use events.player_leave.register instead."
        )(self.events.player_leave.register)
        self.registerCallbackPlayerDeathEvents = deprecated(
            "Call to deprecated function registerCallbackPlayerDeathEvents. Use events.player_death.register instead."
        )(self.events.player_death.register)
        self.registerCallbackChatEvent = deprecated(
            "Call to deprecated function registerCallbackChatEvent. Use events.chat.register instead."
        )(self.events.chat.register)
        self.registerCallbackBlockHitEvent = deprecated(
            "Call to deprecated function registerCallbackBlockHitEvent. Use events.block_hit.register instead."
        )(self.events.block_hit.register)
        self.registerCallbackProjectileHitEvent = deprecated(
            "Call to deprecated function registerCallbackProjectileHitEvent. Use events.projectile_hit.register instead."
        )(self.events.projectile_hit.register)

    def __repr__(self) -> str:
        host, port = self._addr
        return f"{self.__class__.__name__}({host=}, {port=})"

    def _cleanup(self) -> None:
        logging.debug("Minecraft: _cleanup: called, closing channel...")
        old_handler, self._event_handler = self._event_handler, None
        old_handler._cleanup()
        self._channel.close()
        logging.debug("Minecraft: _cleanup: done")

    def __del__(self) -> None:
        logging.debug("Minecraft: __del__: called")
        self._cleanup()

    @property
    def events(self) -> EventHandler:
        """The :class:`EventHandler` for receiving events from the server.
        Checkout the :class:`EventHandler` class for examples for receiving events."""
        return self._event_handler

    @property
    def host(self) -> str:
        """The Minecraft server host address this instance is connected to."""
        return self._addr[0]

    @property
    def port(self) -> int:
        """The Minecraft server port this instance is connected to."""
        return self._addr[1]

    def postToChat(self, *objects, sep: str = " ") -> None:
        """Print `objects` in chat separated by `sep`.
        All objects are converted to strings using :func:`str()` first.

        .. code-block:: python

           mc.postToChat("Hello Minecraft")
           mc.postToChat("Players online:", mc.getPlayers())

        You can also use the module `mcpq.text` to color or markup your chat messages.

        .. code-block:: python

           from mcpq.text import *  # RED, BLUE, BOLD, RESET ...
           mc.postToChat(RED + BOLD + "super " + RESET + BLUE + "cool!")
           # prints "super cool!", where "super" is red and bold, and "cool!" is blue

           # or alternatively, in order to not mix up your namespaces (especially `mcpq.colors`)
           from mcpq import text
           mc.postToChat(text.RED + text.BOLD + "super " + text.RESET + text.BLUE + "cool!")

        :param sep: the separated between each object, defaults to " "
        :type sep: str, optional
        """
        response = self._stub.postToChat(pb.ChatPostRequest(message=sep.join(map(str, objects))))
        raise_on_error(response)
