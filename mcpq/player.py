from __future__ import annotations

import time
from functools import partial
from typing import Literal

from ._base import _HasStub, _PlayerProvider
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._util import ThreadSafeSingeltonCache
from .entity import Entity
from .exception import raise_on_error
from .nbt import NBT
from .vec3 import Vec3
from .world import _WorldHub

CACHE_PLAYER_TIME = 0.2
ALLOW_OFFLINE_PLAYER_OPS = True


class Player(Entity, _HasStub):
    """The :class:`Player` class represents a player on the server.
    It can be used to query information about the player or manipulate them, such as
    getting or setting their position, orientation, world, gamemode and more.

    .. important::

       The :class:`Player` is also an :class:`Entity` and can do everything :class:`Entity` can.

    Do not instantiate the :class:`Player` class directly but use one of the following methods instead:

    .. code-block:: python

       player = mc.getPlayer()  # get any online "default" player
       players = mc.getPlayers()  # get list of all online players
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
       Use :class:`PlayerJoinEvent`, :class:`PlayerLeaveEvent` or update your online players regularly with ``mc.getPlayers()`` to control the state of your online players.

    .. note::

       The number of times the player data will be updated is controlled by the global variable ``mcpq.player.CACHE_PLAYER_TIME``, which is 0.2 by default.
       This means, using a player's position will initially query the position from the server but then use this position for 0.2 seconds before updating the position again (as long as the position is not set in the mean time). The same holds true for all other properties of the player.
       This improves performance but may also cause bugs or problems if the interval in which the up-to-date position is requred is lower than ``mcpq.player.CACHE_PLAYER_TIME``.
    """

    def __init__(self, stub: MinecraftStub, worldhub: _WorldHub, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("Player name must be of type str")
        super().__init__(stub, worldhub, name)

    @property
    def name(self) -> str:
        "The name of this player, equivalent to :attr:`id`"
        return self._id

    @property
    def type(self) -> str:
        """The type of the player, is always ``"player"``"""
        return "player"

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
        self._world = self._worldhub.getWorldByName(pb_player.location.world.name)
        self._pos = Vec3(
            pb_player.location.pos.x, pb_player.location.pos.y, pb_player.location.pos.z
        )
        self._pitch = pb_player.location.orientation.pitch
        self._yaw = pb_player.location.orientation.yaw
        self._update_ts = time.time()
        self._loaded = True
        return True

    def _set_entity_loc(self, entity_loc: pb.EntityLocation) -> None:
        response = self._stub.setPlayer(
            pb.Player(
                name=self.name,
                location=entity_loc,
            )
        )
        if not ALLOW_OFFLINE_PLAYER_OPS or response.code != pb.PLAYER_NOT_FOUND:
            raise_on_error(response)

    def _update(self, allow_offline: bool = ALLOW_OFFLINE_PLAYER_OPS) -> bool:
        response = self._stub.getPlayers(pb.PlayerRequest(names=[self.name], withLocations=True))
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

    def _update_on_check(self, allow_offline: bool = ALLOW_OFFLINE_PLAYER_OPS) -> bool:
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

    def giveItems(self, type: str, amount: int = 1, nbt: NBT | None = None) -> None:
        """Put items into the player's inventory

        :param type: id of item or block to receive
        :type type: str
        :param amount: amount of items to receive, defaults to 1
        :type amount: int, optional
        :param nbt: additional nbt data of items, defaults to None
        :type nbt: NBT | None, optional
        """
        if nbt is None:
            self.runCommand(f"give @s {type} {amount}")
        else:
            self.runCommand(f"give @s {type}{nbt} {amount}")

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

        :param sep: the separated between each object, defaults to " "
        :type sep: str, optional
        """
        response = self._stub.postToChat(
            pb.ChatPostRequest(
                message=sep.join(map(str, objects)), player=pb.Player(name=self.name)
            )
        )
        if not ALLOW_OFFLINE_PLAYER_OPS or response.code != pb.PLAYER_NOT_FOUND:
            raise_on_error(response)

    # server access commands cannot be executed via 'execute as ...'
    def kick(self) -> None:
        _HasStub.runCommand(self, f"kick {self.name}")

    def ban(self) -> None:
        _HasStub.runCommand(self, f"ban {self.name}")

    def pardon(self) -> None:
        _HasStub.runCommand(self, f"pardon {self.name}")

    def op(self) -> None:
        _HasStub.runCommand(self, f"op {self.name}")

    def deop(self) -> None:
        _HasStub.runCommand(self, f"deop {self.name}")


class _PlayerCache(_WorldHub, _HasStub, _PlayerProvider):
    def __init__(self, stub: MinecraftStub) -> None:
        super().__init__(stub)
        self._player_cache = ThreadSafeSingeltonCache(partial(Player, self._stub, self))
        self._default_player: Player | None = None

    def _get_or_create_player(self, name: str) -> Player:
        return self._player_cache.get_or_create(name)

    def getOfflinePlayer(self, name: str) -> Player:
        """Get the :class:`Player` with the given `name` no matter if the player is online or not.
        Does not raise any errors if the player is offline.

        :param name: player name/id
        :type name: str
        :return: the player with the given `name`
        :rtype: Player
        """
        return self._get_or_create_player(name)

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
            response = self._stub.getPlayers(pb.PlayerRequest())
        else:
            response = self._stub.getPlayers(pb.PlayerRequest(names=names))
        raise_on_error(response.status)
        players = [self._get_or_create_player(player.name) for player in response.players]
        if self._default_player is None and players:
            self._default_player = players[0]
        return players

    def getPlayerNames(self) -> list[str]:
        """Equivalent to :func:`getPlayers` but only return their names instead.

        :return: list of all currently online :class:`Player` names
        :rtype: list[str]
        """
        players = self.getPlayers()
        return [player.name for player in players]

    def getPlayer(self, name: str | None = None) -> Player:
        """Get any currently online player, which will become the default player thereafter, or get the online player with given `name`.
        Will raise an error if either no player is online, or if the player with given `name` is not online.

        If you want to check for any currently online players, use :func:`getPlayers` instead.

        :param name: name of the online :class:`Player` that should be returned, or None if any online player will do, defaults to None
        :type name: str | None, optional
        :return: the player with `name` if name is given, else any online player that will become default player thereafter
        :rtype: Player
        """
        if name is None:
            if self._default_player:
                name = self._default_player.name
            else:
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
