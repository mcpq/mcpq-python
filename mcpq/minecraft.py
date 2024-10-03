from __future__ import annotations

import logging
import re

import grpc

from ._base import _HasServer, _SharedBase
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._server import _Server
from ._util import deprecated
from .entity import Entity
from .entitytype import EntityType
from .events import EventHandler
from .exception import raise_on_error
from .material import Material
from .player import Player
from .world import World, _DefaultWorld

__all__ = ["Minecraft"]

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
# logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


class Minecraft(_DefaultWorld, _SharedBase, _HasServer):
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


    The :class:`Minecraft` instance is also the default :class:`World` and can be used to query :class:`Entity`, :class:`Player` and :class:`Event` objects from the server.
    Checkout the corresponding classes for more information.
    """

    def __init__(self, host: str = "localhost", port: int = 1789) -> None:
        self._addr = (host, port)
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        server = _Server(MinecraftStub(self._channel))
        super().__init__(server)
        self._event_handler = EventHandler(server)

        # deprecated functions
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
        response = self._server.stub.postToChat(
            pb.ChatPostRequest(message=sep.join(map(str, objects)))
        )
        raise_on_error(response)

    def getEntityById(self, entity_id: str) -> Entity:
        """Get an entity with a certain `entity_id`, even if it is not loaded.

        Normally the `entity_id` is not known ahead of time.
        Prefer using :func:`getEntities`, :func:`getEntitiesAround` and :func:`spawnEntity`, which all return entities.

        :param entity_id: the unique entity identified
        :type entity_id: str
        :return: the corresponding entity with that id, even if not loaded
        :rtype: Entity
        """
        entity = self._server.get_or_create_entity(entity_id)
        entity._update_on_check()
        return entity

    def getOfflinePlayer(self, name: str) -> Player:
        """Get the :class:`Player` with the given `name` no matter if the player is online or not.
        Does not raise any errors if the player is offline.

        :param name: player name/id
        :type name: str
        :return: the player with the given `name`
        :rtype: Player
        """
        return self._server.get_or_create_player(name)

    def getPlayers(self, names: list[str] | None = None) -> list[Player]:
        """Get all currently online players on the entire server.
        If `names` is provided get all players with the given names only if they are online.
        Will raise an error if `names` is provided and at least one player with given name is offline.

        :param names: if given return only players with given names or error if one of the given players is offline, otherwise if `names` is `None` will return all currently online players, defaults to None
        :type names: list[str] | None, optional
        :return: the list of all currently online players, or if `names` is provided, only those online players
        :rtype: list[Player]
        """
        if names is None:
            response = self._server.stub.getPlayers(pb.PlayerRequest())
        else:
            response = self._server.stub.getPlayers(pb.PlayerRequest(names=names))
        raise_on_error(response.status)
        return [self._server.get_or_create_player(player.name) for player in response.players]

    def getPlayerNames(self) -> list[str]:
        """Equivalent to :func:`getPlayers` but only return their names instead.

        :return: list of all currently online :class:`Player` names
        :rtype: list[str]
        """
        return [player.name for player in self.getPlayers()]

    def getPlayer(self, name: str | None = None) -> Player:
        """Get any currently online player or get the online player with given `name`.
        Will raise an error if either no player is online, or if the player with given `name` is not online.

        If you want to check for any currently online players, use :func:`getPlayers` instead.

        .. note::

           There is no guarantee that the player returned will be the same across multiple calls of this function. It may change depending on the order the players joined the server or the implementation of the server.

        :param name: name of the online :class:`Player` that should be returned, or None if any online player will do, defaults to None
        :type name: str | None, optional
        :return: the player with `name` if name is given, else any online player
        :rtype: Player
        """
        if name is None:
            players = self.getPlayers()
            if players:
                return players[0]
            else:
                raise_on_error(pb.Status(code=pb.PLAYER_NOT_FOUND))
                return None  # type: ignore
        players = self.getPlayers([name])
        if players:
            return players[0]
        return None  # type: ignore

    @property
    def worlds(self) -> tuple[World, ...]:
        """Give a tuple of all worlds loaded on the server.
        Does not automatically call :func:`refreshWorlds`.

        :return: A tuple of all worlds loaded on the server
        :rtype: tuple[World, ...]
        """
        return self._server.get_worlds()

    @property
    def overworld(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:overworld"``.

        :return: The overworld world :class:`World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:overworld")

    @property
    def nether(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:the_nether"``.

        :return: The nether world :class:`World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:the_nether")

    @property
    def end(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:the_end"``.

        :return: The end world :class:`World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:the_end")

    def getWorldByKey(self, key: str) -> World:
        """The `key` of a world is the dimensions internal name/id.
        Typically a regular server has the following worlds/keys:

        - ``"minecraft:overworld"``

        - ``"minecraft:the_nether"``

        - ``"minecraft:the_end"``

        The ``"minecraft:"`` prefix may be omitted, e.g., ``"the_nether"``.

        If the given `key` does not exist an exception is raised.

        :param key: Internal name/id of the world, such as ``"minecraft:the_nether"`` or ``"the_nether"``
        :type key: str
        :return: The corresponding :class:`World` object
        :rtype: World
        """
        return self._server.get_world_by_key(key)

    def getWorldByName(self, name: str) -> World:
        """The `name` of a world is the folder or namespace the world resides in.
        The setting for the world the server opens is found in ``server.properties``.
        A typical, unmodified PaperMC_ server will save the worlds in the following folders:

        .. _PaperMC: https://papermc.io/

        - ``"world"``, for the overworld

        - ``"world_nether"``, for the nether

        - ``"world_the_end"``, for the end

        The name of the overworld (default ``world``) is used as the prefix for the other folders.

        If the given `name` does not exist an exception is raised.

        :param name: Foldername the world is saved in, such as ``world``
        :type name: str
        :return: The corresponding :class:`World` object
        :rtype: World
        """
        return self._server.get_world_by_name(name)

    def refreshWorlds(self) -> None:
        """Fetches the currently loaded worlds from server and updates the world objects.
        This should only be called if the loaded worlds on the server change, for example, with the Multiverse Core Plugin.
        By default, the worlds will be refreshed on first use only.
        """
        self._server.update_worlds()

    def getBlockTypes(self) -> list[str]:
        """The list of all block-types that can be set with :func:`setBlock`"""
        return [m.key for m in self._server.get_materials(lambda m: m.is_block)]

    def getEntityTypes(self) -> list[EntityType]:
        return list(self._server.get_entity_types())

    def getItemTypes(self) -> list[str]:
        """The list of all obtainable items"""
        return [m.key for m in self._server.get_materials(lambda m: m.is_item)]

    def getMaterials(self) -> list[Material]:
        return list(self._server.get_materials())

    def getMinecraftVersion(self) -> str | None:
        """The Minecraft version of the server this instance is connected to or None if the version cannot be identified."""
        response = self._server.stub.getServerInfo(pb.ServerInfoRequest())
        raise_on_error(response.status)
        full_version: str = response.mcVersion
        # spigottest = "4226-Spigot-146439e-2889b3a (MC: 1.21)"
        # papertest = "git-Paper-196 (MC: 1.20.1)"
        # TODO: write unit test for this
        m = re.findall("\\(MC: (.*)\\)", full_version)
        if m and len(m):
            return m[-1]
        logging.warning(f"Minecraft version could not be parsed from '{full_version}'")
        return None

    def getMinecraftVersionTuple(self) -> tuple[int, ...] | None:
        """The Minecraft version of the server this instance is connected to as a integer tuple or None if the version cannot be identified (e.g. from non-release candidate servers)."""
        versionstr = self.getMinecraftVersion()
        if versionstr is not None:
            numsstr = versionstr.split(".")
            try:
                nums = [int(n) for n in numsstr]
                return tuple(nums)
            except ValueError:
                logging.warning(
                    f"Minecraft version '{versionstr}' could not be parsed to tuple of integers"
                )
        return None

    def getPluginVersion(self) -> str:
        """The MCPQ Plugin version running on the server this instance is connected to."""
        response = self._server.stub.getServerInfo(pb.ServerInfoRequest())
        raise_on_error(response.status)
        return response.mcpqVersion

    def getServerVersion(self) -> str:
        """The full name and version of the server this instance is connected to."""
        response = self._server.stub.getServerInfo(pb.ServerInfoRequest())
        raise_on_error(response.status)
        return response.mcVersion

    def getSpawnableEntities(self) -> list[str]:
        """The list of all entity-types that can be spawned with :func:`spawnEntity`"""
        return [e.key for e in self._server.get_entity_types(lambda e: e.is_spawnable)]
