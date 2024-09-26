from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._util import ThreadSafeSingeltonCache
from .entitytype import EntityType
from .exception import raise_on_error
from .material import Material

if TYPE_CHECKING:
    from .entity import Entity
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
    def material_cache(self, force_update: bool = False) -> dict[str, Material]:
        raise NotImplementedError

    @abstractmethod
    def entity_type_cache(self, force_update: bool = False) -> dict[str, EntityType]:
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
        self, filter: Callable[[Material], bool] | None = None
    ) -> tuple[Material, ...]:
        if filter is None:
            return tuple(self.material_cache().values())
        return tuple(m for m in self.material_cache().values() if filter(m))

    def get_entity_types(
        self, filter: Callable[[EntityType], bool] | None = None
    ) -> tuple[EntityType, ...]:
        if filter is None:
            return tuple(self.entity_type_cache().values())
        return tuple(m for m in self.entity_type_cache().values() if filter(m))
