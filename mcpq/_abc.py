from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable

from ._proto import minecraft_pb2 as pb
from .exception import raise_on_error

if TYPE_CHECKING:
    from ._proto import MinecraftStub
    from ._util import ThreadSafeSingeltonCache
    from .entity import Entity
    from .entitytype import _EntityTypeInternal
    from .material import _MaterialInternal
    from .player import Player
    from .world import World


class _ServerInterface(ABC):
    """Internal interface for interacting with server and caching selected results"""

    @property
    @abstractmethod
    def stub(self) -> MinecraftStub:
        raise NotImplementedError

    @abstractmethod
    def entity_cache(self) -> ThreadSafeSingeltonCache[str, Entity]:
        raise NotImplementedError

    @abstractmethod
    def player_cache(self) -> ThreadSafeSingeltonCache[str, Player]:
        raise NotImplementedError

    @abstractmethod
    def world_by_name_cache(
        self, force_update: bool = False
    ) -> ThreadSafeSingeltonCache[str, World]:
        raise NotImplementedError

    @abstractmethod
    def material_cache(self, force_update: bool = False) -> dict[str, _MaterialInternal]:
        raise NotImplementedError

    @abstractmethod
    def entity_type_cache(self, force_update: bool = False) -> dict[str, _EntityTypeInternal]:
        raise NotImplementedError

    @abstractmethod
    def server_info_cache(self, force_update: bool = False) -> dict[str, Any]:
        raise NotImplementedError

    def get_or_create_entity(self, entity_id: str) -> Entity:
        return self.entity_cache().get_or_create(entity_id)

    def get_or_create_player(self, name: str) -> Player:
        return self.player_cache().get_or_create(name)

    def get_worlds(self) -> tuple[World, ...]:
        return tuple(self.world_by_name_cache().values())

    def get_world_by_name(self, name: str) -> World:
        world = self.world_by_name_cache().get(name)
        if world is None:
            raise_on_error(pb.Status(code=pb.WORLD_NOT_FOUND, extra="name=" + name))
        return world

    def get_world_by_key(self, key: str) -> World:
        world = None
        parts = key.split(":", maxsplit=1)
        if len(parts) == 1:
            key = "minecraft:" + key
        for world in self.get_worlds():
            if world.key == key:
                return world
        raise_on_error(pb.Status(code=pb.WORLD_NOT_FOUND, extra="key=" + key))
        return world

    def get_materials(
        self, filter: Callable[[_MaterialInternal], bool] | None = None
    ) -> tuple[_MaterialInternal, ...]:
        if filter is None:
            return tuple(self.material_cache().values())
        return tuple(m for m in self.material_cache().values() if filter(m))

    def get_entity_types(
        self, filter: Callable[[_EntityTypeInternal], bool] | None = None
    ) -> tuple[_EntityTypeInternal, ...]:
        if filter is None:
            return tuple(self.entity_type_cache().values())
        return tuple(m for m in self.entity_type_cache().values() if filter(m))

    def get_server_version(self) -> str:
        full_version: str | None = self.server_info_cache().get("serverversion")
        if full_version:
            return full_version
        return "unknown"

    def get_mc_version_string(self) -> str:
        version: str | None = self.server_info_cache().get("mcversion")
        if version:
            return version
        full_version: str = self.get_server_version()
        if full_version != "unknown":
            # spigottest = "4226-Spigot-146439e-2889b3a (MC: 1.21)"
            # papertest = "git-Paper-196 (MC: 1.20.1)"
            # TODO: write unit test for this
            m = re.findall("\\(MC: (.+)\\)", full_version)
            if m and len(m):
                version = self.server_info_cache()["mcversion"] = m[-1]
                return version
            logging.warning(f"Minecraft version could not be parsed from '{full_version}'")
        return "unknown"

    def get_mc_version(self) -> tuple[int, ...]:
        version_tuple = self.server_info_cache().get("_mcversion_tuple")
        if version_tuple:
            return version_tuple
        versionstr = self.get_mc_version_string()
        if versionstr != "unknown":
            numsstr = versionstr.split(".")
            try:
                version_tuple = tuple(int(n) for n in numsstr)
                self.server_info_cache()["_mcversion_tuple"] = version_tuple
                return version_tuple
            except ValueError:
                logging.warning(
                    f"Minecraft version '{versionstr}' could not be parsed to tuple of integers"
                )
        return tuple()

    def get_mcpq_version(self) -> str:
        mcpq_version = self.server_info_cache().get("mcpqversion")
        if mcpq_version is not None:
            return mcpq_version
        return "unknown"
