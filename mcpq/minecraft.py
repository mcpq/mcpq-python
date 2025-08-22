from __future__ import annotations

from typing import Literal

import grpc

from . import logger
from ._base import _HasServer, _SharedBase
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._server import _Server
from ._util import deprecated
from .entity import Entity
from .entitytype import EntityTypeFilter
from .events import EventHandler
from .exception import raise_on_error
from .material import MaterialFilter
from .nbt import NBT, Block, EntityType
from .player import Player
from .vec3 import Vec3
from .world import World, _DefaultWorld

__all__ = ["Minecraft"]


class Minecraft(_DefaultWorld, _SharedBase, _HasServer):
    """:class:`Minecraft` is the main object of interacting with Minecraft servers that have the mcpq-plugin_.
    When constructing the class, a ``host`` and ``port`` of the server should be provided to which a connection will be built. They default to ``"localhost"`` and ``1789`` respectively.
    All other worlds, events, entities and more are then received via the methods of that instance.

    .. _mcpq-plugin: https://github.com/mcpq/mcpq-plugin

    .. code-block:: python

       from mcpq import Minecraft
       mc = Minecraft()  # connect to localhost
       mc.postToChat("Hello Minecraft")  # send message in chat

    .. note::

       Generally, it is sufficient to construct one :class:`Minecraft` instance per server or active connection, as this connection is thread-safe and reusable.
       However, it is also possible to connect with multiple instances from the same or different hosts at the same time.

    .. caution::

       The connection used by the server is not encrypted or otherwise secured, meaning that any man-in-the-middle can read and modify any information sent between the program and the Minecraft server.
       For security reasons it is recommended to connect from the same host as the server is running on. By default, the plugin does only allow connections from ``localhost`` to prevent access from third parties.


    The :class:`Minecraft` instance is also the default :class:`~mcpq.world.World` and can be used to query :class:`~mcpq.entity.Entity`, :class:`~mcpq.player.Player` and :class:`Event <mcpq.events.EventHandler>` objects from the server.
    Checkout the corresponding classes for more information.

    .. code::

       from mcpq import Minecraft

       mc = Minecraft()  # connect to server on localhost with mcpq-plugin

       mc.postToChat("Players online:", mc.getPlayerList())  # show online players
       mc.events.block_hit.register(mc.postToChat)  # print whenever a player hits a block to chat
       mc.setBlock("obsidian", mc.Vec3(0, 0, 0))  # set obsidian block at origin
       pos = mc.getHighestPos(0, 0).up(1)  # get position above highest ground at 0 0
       stairs = mc.blocks.endswith("_stairs").choice()  # get random block ending in "_stairs"
       mc.setBlock(stairs.withData({"waterlogged": True}), pos)  # set waterlogged stairs above ground
       creeper = mc.spawnEntity("creeper", pos.up(1))  # spawn creeper on stairs
       creeper.giveEffect("invisibility")  # give creeper permanent invisibility effect
       creeper.pos = mc.getPlayer().pos  # teleport creeper to player position
       # and many more ...
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

        self.getPlayers = deprecated(
            "Call to deprecated function getPlayers. Use getPlayerList instead."
        )(self.getPlayerList)
        self.getPlayerNames = deprecated(
            "Call to deprecated function getPlayerNames. Use [player.name for player in self.getPlayerList()] instead."
        )(lambda: [player.name for player in self.getPlayerList()])

    def __repr__(self) -> str:
        host, port = self._addr
        return f"{self.__class__.__name__}({host=}, {port=})"

    def _cleanup(self) -> None:
        logger.debug("Minecraft: _cleanup: called, closing channel...")
        old_handler, self._event_handler = self._event_handler, None
        old_handler._cleanup()
        self._channel.close()
        logger.debug("Minecraft: _cleanup: done")

    def __del__(self) -> None:
        logger.debug("Minecraft: __del__: called")
        self._cleanup()

    @property
    def host(self) -> str:
        """The Minecraft server host address this instance is connected to, default is ``localhost``."""
        return self._addr[0]

    @property
    def port(self) -> int:
        """The Minecraft server port this instance is connected to, default is ``1789``."""
        return self._addr[1]

    @property
    def Block(self) -> type[Block]:
        """Alias for constructing :class:`~mcpq.nbt.Block`, e.g., ``mc.Block("acacia_stairs")``"""
        return Block

    @property
    def EntityType(self) -> type[EntityType]:
        """Alias for constructing :class:`~mcpq.nbt.EntityType`, e.g., ``mc.EntityType("creeper")``"""
        return EntityType

    @property
    def NBT(self) -> type[NBT]:
        """Alias for constructing :class:`~mcpq.nbt.NBT`, e.g., ``mc.NBT({"unbreakable": {}})``"""
        return NBT

    @property
    def Vec3(self) -> type[Vec3]:
        """Alias for constructing :class:`~mcpq.vec3.Vec3`, e.g., ``mc.Vec3(1, 2, 3)``"""
        return Vec3

    @property
    def vec(self) -> type[Vec3]:
        """Alias for constructing :class:`~mcpq.vec3.Vec3`, e.g., ``mc.vec(1, 2, 3)``"""
        return Vec3

    @property
    def events(self) -> EventHandler:
        """The :class:`~mcpq.events.EventHandler` for receiving events from the server.
        Checkout the :class:`~mcpq.events.EventHandler` class for examples for receiving events."""
        return self._event_handler

    @property
    def blocks(self) -> MaterialFilter:
        """The :class:`~mcpq.material.MaterialFilter` containing all types of blocks on the server.
        Equivalent to ``mc.materials.block()``.
        Checkout the :class:`~mcpq.material.MaterialFilter` class for examples on filtering.
        """
        return self.materials.block()

    @property
    def materials(self) -> MaterialFilter:
        """The :class:`~mcpq.material.MaterialFilter` containing all materials on the server, including types of blocks, items and more.
        Checkout the :class:`~mcpq.material.MaterialFilter` class for examples on filtering.
        """
        return MaterialFilter(self._server, [])

    @property
    def entity_types(self) -> EntityTypeFilter:
        """The :class:`~mcpq.entitytype.EntityTypeFilter` containing all entity-types on the server.
        Checkout the :class:`~mcpq.entitytype.EntityTypeFilter` class for examples on filtering.

        .. note::

           You probably want to use :attr:`.spawnables` to get spawnable entity-types only
        """
        return EntityTypeFilter(self._server, [])

    @property
    def spawnables(self) -> EntityTypeFilter:
        """The :class:`~mcpq.entitytype.EntityTypeFilter` containing all entity-types on the server that can be spawned with :func:`spawnEntity`.
        Equivalent to ``mc.entity_types.spawnable()``.
        Checkout the :class:`~mcpq.entitytype.EntityTypeFilter` class for examples on filtering.
        """
        return self.entity_types.spawnable()

    def postToChat(self, *objects, sep: str = " ") -> None:
        """Print `objects` in chat separated by `sep`.
        All objects are converted to strings using :func:`str()` first.

        .. code-block:: python

           mc.postToChat("Hello Minecraft")
           # print all only players
           mc.postToChat("Players online:", *mc.getPlayerList())
           # print every block hit event into chat (good for learning events)
           mc.events.block_hit.register(mc.postToChat)

        You can also use the module `mcpq.text` to color or markup your chat messages:

        .. code-block:: python

           from mcpq import Minecraft, text
           mc.postToChat(text.RED + text.BOLD + "super " + text.RESET + text.BLUE + "cool!")
           # prints "super cool!", where "super" is red and bold, and "cool!" is blue

        :param sep: the separator between each object, defaults to " "
        :type sep: str, optional
        """
        response = self._server.stub.postToChat(
            pb.ChatPostRequest(message=sep.join(map(str, objects)))
        )
        raise_on_error(response)

    def showTitle(
        self,
        text: str,
        *,
        mode: Literal["actionbar", "subtitle", "title"] = "title",
        color: Literal[
            "white",
            "black",
            "dark_blue",
            "dark_green",
            "dark_aqua",
            "dark_red",
            "dark_purple",
            "gold",
            "gray",
            "dark_gray",
            "blue",
            "green",
            "aqua",
            "red",
            "light_purple",
            "yellow",
        ] = "white",
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underlined: bool = False,
        obfuscated: bool = False,
        duration: int = 5,
        fade_in: int = 1,
        fade_out: int = 1,
    ) -> None:
        """Display a Minecraft title to all players and control
        fade-in, display time, fade-out, and text styling (color, bold, italic, etc.).

        .. code-block:: python

           # simple title for 5 seconds with 1s fade-in/out
           mc.showTitle("Welcome to the server!")

           # subtitle in blue and bold, duration 3s
           mc.showTitle(
               "Events starting soon...",
               mode="subtitle",
               color="blue",
               bold=True,
               duration=3
           )

        :param text: The text to display.
        :type text: str
        :param mode: Display target: ``"title"``, ``"subtitle"``, or ``"actionbar"``.
        :type mode: Literal["actionbar", "subtitle", "title"], optional
        :param color: Text color (Minecraft color name), defaults to ``"white"``.
        :type color: Literal[ "white", "black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold", "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow"], optional
        :param bold: Render text in bold.
        :type bold: bool, optional
        :param italic: Render text in italics.
        :type italic: bool, optional
        :param strikethrough: Render text with strikethrough.
        :type strikethrough: bool, optional
        :param underlined: Render text underlined.
        :type underlined: bool, optional
        :param obfuscated: Render text obfuscated (“magic” text).
        :type obfuscated: bool, optional
        :param duration: Display duration in seconds (not including fades), default ``5``.
        :type duration: int, optional
        :param fade_in: Fade-in time in seconds, default ``1``.
        :type fade_in: int, optional
        :param fade_out: Fade-out time in seconds, default ``1``.
        :type fade_out: int, optional
        """
        self.runCommand(f"title @a times {fade_in}s {duration}s {fade_out}s")
        self.runCommand(
            f'title @a {mode} {{"text":"{text}","color":"{color}","bold":{bold},"italic":{italic},"strikethrough":{strikethrough},"underlined":{underlined},"obfuscated":{obfuscated}}}'
        )

    def clearTitle(self) -> None:
        """Clear all currently displayed titles/subtitles/actionbars
        from all players.

        Useful to remove text early or to "reset" the screen before showing new titles.

        .. code-block:: python

           # clear everything before a new announcement
           mc.clearTitle()
           mc.showTitle("New Event at 8 PM!", mode="title", color="gold", bold=True)
        """
        self.runCommand("title @a clear")

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
        """Get the :class:`~mcpq.player.Player` with the given `name` no matter if the player is online or not.
        Does not raise any errors if the player is offline.

        :param name: player name/id
        :type name: str
        :return: the player with the given `name`
        :rtype: Player
        """
        return self._server.get_or_create_player(name)

    def getPlayer(self, name: str | None = None) -> Player:
        """Get any currently online player or get the online player with given `name`.
        Will raise an error if either no player is online, or if the player with given `name` is not online.

        If you want to check for any currently online players, use :func:`getPlayerList` instead.

        .. note::

           There is no guarantee that the player returned will be the same across multiple calls of this function. It may change depending on the order the players joined the server or the implementation of the server.

        :param name: name of the online :class:`~mcpq.player.Player` that should be returned, or None if any online player will do, defaults to None
        :type name: str | None, optional
        :return: the player with `name` if name is given, else any online player
        :rtype: Player
        """
        if name is None:
            players = self.getPlayerList()
            if players:
                return players[0]
            else:
                raise_on_error(pb.Status(code=pb.PLAYER_NOT_FOUND))
                return None  # type: ignore
        players = self.getPlayerList([name])
        if players:
            return players[0]
        return None  # type: ignore

    def getPlayerList(self, names: list[str] | None = None) -> list[Player]:
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

        :return: The overworld world :class:`~mcpq.world.World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:overworld")

    @property
    def nether(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:the_nether"``.

        :return: The nether world :class:`~mcpq.world.World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:the_nether")

    @property
    def end(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:the_end"``.

        :return: The end world :class:`~mcpq.world.World` object
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
        :return: The corresponding :class:`~mcpq.world.World` object
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
        :return: The corresponding :class:`~mcpq.world.World` object
        :rtype: World
        """
        return self._server.get_world_by_name(name)

    def refreshWorlds(self) -> None:
        """Fetches the currently loaded worlds from server and updates the world objects.
        This should only be called if the loaded worlds on the server change, for example, with the Multiverse Core Plugin.
        By default, the worlds will be refreshed on first use only.
        """
        self._server.world_by_name_cache(force_update=True)

    def getMinecraftVersion(self) -> str:
        """The Minecraft version of the server this instance is connected to or None if the version cannot be identified."""
        return self._server.get_mc_version_string()

    def getMinecraftVersionTuple(self) -> tuple[int, ...]:
        """The Minecraft version of the server this instance is connected to as a integer tuple or None if the version cannot be identified (e.g. from non-release candidate servers)."""
        return self._server.get_mc_version()

    def getPluginVersion(self) -> str:
        """The MCPQ Plugin version running on the server this instance is connected to."""
        return self._server.get_mcpq_version()

    def getServerVersion(self) -> str:
        """The full name and version of the server this instance is connected to."""
        return self._server.get_server_version()
