from __future__ import annotations

import time
from typing import Literal

from ._base import _HasServer, _SharedBase
from ._proto import minecraft_pb2 as pb
from .entity import Entity
from .exception import raise_on_error
from .nbt import NBT, Block, EntityType
from .vec3 import Vec3

CACHE_PLAYER_TIME = 0.2
ALLOW_OFFLINE_PLAYER_OPS = True


class Player(Entity, _SharedBase, _HasServer):
    """The :class:`Player` class represents a player on the server.
    It can be used to query information about the player or manipulate them, such as
    getting or setting their position, orientation, world, gamemode and more.

    .. important::

       The :class:`Player` is also an :class:`Entity` and can do everything :class:`Entity` can.

    Do not instantiate the :class:`Player` class directly but use one of the following methods instead:

    .. code-block:: python

       player = mc.getPlayer()  # get any single online player
       players = mc.getPlayerList()  # get list of all online players
       playerfoo = mc.getOfflinePlayer("foo")  # get player with name 'foo' even if offline

    Once you have your players you can use them in a multitude of ways:

    .. code-block:: python

       player.pos  # get the current position of player
       player.pos = Vec3(0, 0, 0)  # teleport player to origin
       player.world  # get current world the player is in
       player.world = mc.end  # teleport player into end
       player.facing  # get direction player is currently looking at as directional vector
       player.facing = Vec3().east()  # make player face straight east
       # use teleport if you want to set position, facing direction and/or world at once:
       player.teleport(pos=Vec3(0, 0, 0), world=mc.end)  # teleport player into origin in the end

       # other modifiers
       player.kill()  # kill player
       player.creative()  # change player gamemode to creative
       player.giveItems("snowball", 64)  # give player 64 snowballs into inventory
       player.giveEffect("glowing", 5)  # give player glowing for 5 seconds
       player.runCommand("clear")  # run command as player and clear player inventory
       ...

    .. note::

       Whether or not exceptions from operations on *offline* players are ignored is controlled by the global variable ``mcpq.player.ALLOW_OFFLINE_PLAYER_OPS``, which is True by default.
       Players can go offline at any time and even checking with :attr:`online` before every operation will not guarantee that the player is online by the time the operation is received by the server.
       To make life easier all PlayerNotFound exceptions will be caught and ignored if ``mcpq.player.ALLOW_OFFLINE_PLAYER_OPS`` is True.
       Note that this will make it look like the operation succeeded, even if the player was (already) offline.
       Instead, use :class:`PlayerJoinEvent`, :class:`PlayerLeaveEvent` or update your online players regularly with ``mc.getPlayerList()`` to control the state of your online players.

    .. note::

       The number of times the player data will be updated is controlled by the global variable ``mcpq.player.CACHE_PLAYER_TIME``, which is 0.2 by default.
       This means, using a player's position will initially query the position from the server but then use this position for 0.2 seconds before updating the position again (as long as the position is not set in the mean time). The same holds true for all other properties of the player.
       This improves performance but may also cause bugs or problems if the interval in which the up-to-date position is requred is lower than ``mcpq.player.CACHE_PLAYER_TIME``.
    """

    @property
    def name(self) -> str:
        "The name of this player, equivalent to :attr:`id`"
        return self._id

    @property
    def type(self) -> EntityType:
        """The :class:`~mcpq.nbt.EntityType` of the player, is always ``"player"``"""
        return EntityType("player")

    @property
    def online(self) -> bool:
        "Whether the player is currently online"
        if self._should_update():
            self._update(allow_offline=True)
            # TODO: online being True does not give any guarantees
        return self._loaded

    @property
    def loaded(self) -> bool:
        "Not applicable to player, use :attr:`online` instead"
        raise AttributeError("Loaded does not work on Players, use .online() instead")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

    def _should_update(self) -> bool:
        if time.time() - self._update_ts > CACHE_PLAYER_TIME:
            return True
        return False

    def _inject_update(self, pb_player: pb.Player) -> bool:
        assert pb_player.name == self.name
        self._world = self._server.get_world_by_name(pb_player.location.world.name)
        self._pos = Vec3(
            pb_player.location.pos.x, pb_player.location.pos.y, pb_player.location.pos.z
        )
        self._pitch = pb_player.location.orientation.pitch
        self._yaw = pb_player.location.orientation.yaw
        self._update_ts = time.time()
        self._loaded = True
        return True

    def _set_entity_loc(self, entity_loc: pb.EntityLocation) -> None:
        response = self._server.stub.setPlayer(
            pb.Player(
                name=self.name,
                location=entity_loc,
            )
        )
        if not ALLOW_OFFLINE_PLAYER_OPS or response.code != pb.PLAYER_NOT_FOUND:
            raise_on_error(response)

    def _update(self, allow_offline: bool = ALLOW_OFFLINE_PLAYER_OPS) -> bool:
        response = self._server.stub.getPlayers(
            pb.PlayerRequest(names=[self.name], withLocations=True)
        )
        if allow_offline and response.status.code == pb.PLAYER_NOT_FOUND:
            self._loaded = False  # do not update self._update_ts on purpose
            return False
        raise_on_error(response.status)
        if len(response.players) > 0:
            assert len(response.players) == 1
            p = response.players[0]
            return self._inject_update(p)
        else:
            raise RuntimeError("Player could not be updated and no error was raised by response")

    def _update_on_check(self, allow_offline: bool = ALLOW_OFFLINE_PLAYER_OPS) -> None:
        if self._should_update():
            self._update(allow_offline=allow_offline)

    # functions working on entity but not player
    def remove(self) -> None:
        "Not applicable to player, use :func:`kill` or :func:`kick` instead"
        raise AttributeError("Remove cannot be used on a Player")

    # functions only for players
    def gamemode(self, mode: Literal["adventure", "creative", "spectator", "survival"]) -> None:
        """Set the players gamemode to `mode`

        :param mode: the gamemode the player should be set to
        :type mode: Literal[&quot;adventure&quot;, &quot;creative&quot;, &quot;spectator&quot;, &quot;survival&quot;]
        """
        self.runCommand(f"gamemode {mode}")

    def adventure(self) -> None:
        """Equivalent to :func:`gamemode` with argument ``"adventure"``"""
        self.gamemode("adventure")

    def creative(self) -> None:
        """Equivalent to :func:`gamemode` with argument ``"creative"``"""
        self.gamemode("creative")

    def spectator(self) -> None:
        """Equivalent to :func:`gamemode` with argument ``"spectator"``"""
        self.gamemode("spectator")

    def survival(self) -> None:
        """Equivalent to :func:`gamemode` with argument ``"survival"``"""
        self.gamemode("survival")

    def giveItems(self, item: str | Block, amount: int = 1, *, nbt: NBT | None = None) -> None:
        """Put `amount` of certain `item` into the player's inventory.
        The item can be a string or a :class:`~mcpq.nbt.Block` with component data:

        .. code::

           mc.getPlayer().giveItems("snowball", 64)  # give player 64 snowballs (4 stacks of 16)
           sword = mc.Block("diamond_sword").withData({"enchantments": {"sharpness": 5}})
           # item can be given as is
           mc.getPlayer().giveItems(sword)  # give player enchanted sword
           # blocks have to be changed to block_state format
           b = mc.Block("acacia_stairs").withData({"waterlogged": True})
           mc.getPlayer().giveItems(b.asBlockStateForItem())  # give player already waterlogged stairs

        .. note::

           `nbt` is only used for servers prior to 1.20.5 and will be removed in the future. All more modern servers use :class:`~mcpq.nbt.ComponentData`, which can be set on the `item`.
        """
        if nbt is None:
            self.runCommand(f"give @s {item} {amount}")
        else:
            self.runCommand(f"give @s {item}{nbt} {amount}")

    def postToChat(self, *objects, sep: str = " ") -> None:
        """Print `objects` in chat separated by `sep` and *only visible to player*.
        All objects are converted to strings using :func:`str()` first.

        .. code-block:: python

           p = mc.getPlayer()
           p.postToChat(f"Hello {p.name}, only you can see this")

        You can also use the module `mcpq.text` to color or markup your chat messages.

        .. code-block:: python

           from mcpq import text
           p.postToChat(text.RED + text.BOLD + "super " + text.RESET + text.BLUE + "cool!")

        :param sep: the separator between each object, defaults to " "
        :type sep: str, optional
        """
        response = self._server.stub.postToChat(
            pb.ChatPostRequest(
                message=sep.join(map(str, objects)), player=pb.Player(name=self.name)
            )
        )
        if not ALLOW_OFFLINE_PLAYER_OPS or response.code != pb.PLAYER_NOT_FOUND:
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
        """Display a Minecraft title to one player and control
        fade-in, display time, fade-out, and text styling (color, bold, italic, etc.).

        .. code-block:: python

           # simple title for 5 seconds with 1s fade-in/out
           player.showTitle("Welcome to the server!")

           # subtitle in blue and bold, duration 3s
           player.showTitle(
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
        self.runCommand(f"title @s times {fade_in}s {duration}s {fade_out}s")
        self.runCommand(
            f'title @s {mode} {{"text":"{text}","color":"{color}","bold":{bold},"italic":{italic},"strikethrough":{strikethrough},"underlined":{underlined},"obfuscated":{obfuscated}}}'
        )

    def clearTitle(self) -> None:
        """Clear all currently displayed titles/subtitles/actionbars
        from one player.

        Useful to remove text early or to "reset" the screen before showing new titles.

        .. code-block:: python

           # clear everything before a new announcement
           player.clearTitle()
           player.showTitle("New Event at 8 PM!", mode="title", color="gold", bold=True)
        """
        self.runCommand("title @s clear")

    # server access commands cannot be executed via 'execute as ...'
    def kick(self) -> None:
        _SharedBase.runCommand(self, f"kick {self.name}")

    def ban(self) -> None:
        _SharedBase.runCommand(self, f"ban {self.name}")

    def pardon(self) -> None:
        _SharedBase.runCommand(self, f"pardon {self.name}")

    def op(self) -> None:
        _SharedBase.runCommand(self, f"op {self.name}")

    def deop(self) -> None:
        _SharedBase.runCommand(self, f"deop {self.name}")
