from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterator

from ._base import _HasServer
from ._proto import minecraft_pb2 as pb
from .exception import raise_on_error
from .nbt import EntityType


@dataclass(order=True, frozen=True)
class _EntityTypeInternal:
    key: EntityType
    is_spawnable: bool = field(repr=False, hash=False, compare=False, kw_only=True)

    def __str__(self) -> str:
        return self.key

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def _build(cls, buffer: pb.EntityType) -> _EntityTypeInternal:
        return cls(
            EntityType(buffer.key),
            is_spawnable=buffer.isSpawnable,
        )


class EntityTypeFilter(_HasServer, Sequence):
    """Works the same as :class:`~mcpq.material.MaterialFilter` only for entity-types instead.

    .. note::

       The interface and functions for entities is very similar to blocks, such that we are aliasing :class:`~mcpq.nbt.EntityType` to :class:`~mcpq.nbt.Block` at the moment.
       If at a later point the functionality between the two diverges then we will split the classes as well.
    """

    def __init__(
        self,
        server,
        filters: list[Callable[[_EntityTypeInternal], bool]],
        next_or: bool = False,
    ):
        super().__init__(server)
        self._filters = filters
        self._filtered_entity_types: list[EntityType] | None = None
        self._next_or: bool = next_or

    # logic operations

    def _add_filter(self, func: Callable[[_EntityTypeInternal], bool]) -> EntityTypeFilter:
        if self._next_or and self._filters:
            filters = self._filters[:]
            last_filter = filters[-1]
            filters[-1] = lambda m: last_filter(m) or func(m)
            return self.__class__(self._server, filters)
        return self.__class__(self._server, self._filters + [func])

    @property
    def or_(self) -> EntityTypeFilter:
        return self.__class__(self._server, self._filters, True)

    def __add__(self, other) -> EntityTypeFilter:
        if isinstance(other, EntityTypeFilter):
            return self.__class__(
                self._server,
                [
                    lambda m: all(ffunc(m) for ffunc in self._filters)
                    or all(ffunc(m) for ffunc in other._filters)
                ],
            )
        return NotImplemented

    def __and__(self, other) -> EntityTypeFilter:
        if isinstance(other, EntityTypeFilter):
            return self.__class__(
                self._server,
                [
                    lambda m: all(ffunc(m) for ffunc in self._filters)
                    and all(ffunc(m) for ffunc in other._filters)
                ],
            )
        return NotImplemented

    def __or__(self, other) -> EntityTypeFilter:
        if isinstance(other, EntityTypeFilter):
            return self.__class__(
                self._server,
                [
                    lambda m: all(ffunc(m) for ffunc in self._filters)
                    or all(ffunc(m) for ffunc in other._filters)
                ],
            )
        return NotImplemented

    def __invert__(self) -> EntityTypeFilter:
        return self.__class__(
            self._server,
            [lambda m: not all(ffunc(m) for ffunc in self._filters)],
        )

    # apply filters

    def _filtered(self) -> list[EntityType]:
        if self._filtered_entity_types is None:
            if self._filters:
                self._filtered_entity_types = [
                    m.key
                    for m in self._server.get_entity_types(
                        lambda m: all(ffunc(m) for ffunc in self._filters)
                    )
                ]
            else:
                self._filtered_entity_types = [m.key for m in self._server.get_entity_types()]
        return self._filtered_entity_types

    def get(self) -> list[EntityType]:
        return self._filtered()[:]  # copy of cached list

    def getById(self, id: str) -> EntityType:
        element = self.equals(id).first()
        if element is None:
            raise_on_error(pb.Status(code=pb.ENTITY_TYPE_NOT_FOUND, extra=id))
        return element  # type: ignore

    def first(self) -> EntityType | None:
        if len(self):
            return self[0]
        return None

    def choice(self) -> EntityType:
        return random.choice(self)

    def len(self) -> int:
        return len(self)

    # sequence methods

    def __len__(self) -> int:
        return len(self._filtered())

    def __getitem__(self, index) -> EntityType:
        return self._filtered()[index]

    def __iter__(self) -> Iterator[EntityType]:
        return iter(self._filtered())

    def __repr__(self):
        return f"{self.__class__.__name__}({self._filtered()!r}, len={len(self)})"

    # entity type properties

    def spawnable(self, value: bool = True, /) -> EntityTypeFilter:
        return self._add_filter(lambda m: m.is_spawnable is value)

    # additional infered properties

    def vanilla(self, value: bool = True, /) -> EntityTypeFilter:
        return self._add_filter(lambda m: (m.key.namespace == "minecraft") is value)

    def namespace(self, *namespaces: str, negate: bool = False) -> EntityTypeFilter:
        return self._add_filter(lambda m: (m.key.namespace in namespaces) is not negate)

    # additional key filters

    def equals(self, *strings: str, negate: bool = False) -> EntityTypeFilter:
        return self._add_filter(lambda m: (m.key in strings) is not negate)

    def contains(self, *substrings: str, negate: bool = False) -> EntityTypeFilter:
        return self._add_filter(
            lambda m: any(sub in m.key.name for sub in substrings) is not negate
        )

    def startswith(self, *substrings: str, negate: bool = False) -> EntityTypeFilter:
        return self._add_filter(
            lambda m: any(m.key.name.startswith(sub) for sub in substrings) is not negate
        )

    def endswith(self, *substrings: str, negate: bool = False) -> EntityTypeFilter:
        return self._add_filter(
            lambda m: any(m.key.name.endswith(sub) for sub in substrings) is not negate
        )
