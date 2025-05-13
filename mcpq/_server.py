from __future__ import annotations

from functools import partial
from typing import Any

from ._abc import _ServerInterface
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._util import ThreadSafeSingeltonCache
from .entity import Entity
from .entitytype import _EntityTypeInternal
from .exception import raise_on_error
from .material import _MaterialInternal
from .player import Player
from .world import World


class _Server(_ServerInterface):
    """Impl. of internal interface for interacting with server and caching selected results"""

    def __init__(self, stub: MinecraftStub) -> None:
        if not isinstance(stub, MinecraftStub):
            raise TypeError(f"Argument 'stub' must be of type MinecraftStub was '{type(stub)}'")
        self._stub = stub
        self._world_by_name_cache = ThreadSafeSingeltonCache(None)
        self._entity_cache = ThreadSafeSingeltonCache(partial(Entity, self), use_weakref=True)
        self._player_cache = ThreadSafeSingeltonCache(partial(Player, self))
        self._material_cache: dict[str, _MaterialInternal] = {}
        self._entity_type_cache: dict[str, _EntityTypeInternal] = {}
        self._server_info_cache: dict[str, Any] = {}

    @property
    def stub(self) -> MinecraftStub:
        return self._stub

    def entity_cache(self) -> ThreadSafeSingeltonCache[str, Entity]:
        return self._entity_cache

    def player_cache(self) -> ThreadSafeSingeltonCache[str, Player]:
        return self._player_cache

    def world_by_name_cache(
        self, force_update: bool = False
    ) -> ThreadSafeSingeltonCache[str, World]:
        if not self._world_by_name_cache or force_update:
            response = self.stub.accessWorlds(pb.WorldRequest())
            raise_on_error(response.status)
            for world in response.worlds:
                self._world_by_name_cache.get_or_create(
                    world.name, factory=partial(World, self, world.info.key)
                )
        return self._world_by_name_cache

    def material_cache(self, force_update: bool = False) -> dict[str, _MaterialInternal]:
        if not self._material_cache or force_update:
            response = self.stub.getMaterials(pb.MaterialRequest())
            raise_on_error(response.status)
            self._material_cache = {
                m.key: _MaterialInternal._build(m)
                for m in sorted(response.materials, key=lambda m: m.key)
            }
        return self._material_cache

    def entity_type_cache(self, force_update: bool = False) -> dict[str, _EntityTypeInternal]:
        if not self._entity_type_cache or force_update:
            response = self.stub.getEntityTypes(pb.EntityTypeRequest())
            raise_on_error(response.status)
            self._entity_type_cache = {
                m.key: _EntityTypeInternal._build(m)
                for m in sorted(response.types, key=lambda m: m.key)
            }
        return self._entity_type_cache

    def server_info_cache(self, force_update: bool = False) -> dict[str, Any]:
        if not self._server_info_cache or force_update:
            response = self.stub.getServerInfo(pb.ServerInfoRequest())
            raise_on_error(response.status)
            self._server_info_cache = {
                # TODO: automatically parse all properties to dict
                "mcversion": str(response.mcVersion),
                "mcpqversion": str(response.mcpqVersion),
                "serverversion": str(response.serverVersion),
                # _local properties may be added by _server functions
            }
        return self._server_info_cache
