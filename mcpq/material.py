from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterator

from ._base import _HasServer
from ._proto import minecraft_pb2 as pb
from .exception import raise_on_error
from .nbt import Block


@dataclass(order=True, frozen=True)
class Material:
    key: Block
    is_air: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_block: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_burnable: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_edible: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_flammable: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_fuel: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_interactable: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_item: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_occluding: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_solid: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    has_gravity: bool = field(repr=False, hash=False, compare=False, kw_only=True)

    def __str__(self) -> str:
        return self.key

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def _build(cls, buffer: pb.Material) -> Material:
        return cls(
            Block(buffer.key.removeprefix("minecraft:")),
            is_air=buffer.isAir,
            is_block=buffer.isBlock,
            is_burnable=buffer.isBurnable,
            is_edible=buffer.isEdible,
            is_flammable=buffer.isFlammable,
            is_fuel=buffer.isFuel,
            is_interactable=buffer.isInteractable,
            is_item=buffer.isItem,
            is_occluding=buffer.isOccluding,
            is_solid=buffer.isSolid,
            has_gravity=buffer.hasGravity,
        )


class MaterialFilter(_HasServer, Sequence):
    def __init__(self, server, filters: list[Callable[[Material], bool]]):
        super().__init__(server)
        self._filters = filters
        self._filtered_materials: list[Block] | None = None

    # apply filters

    def _filtered(self, refresh: bool = False) -> list[Block]:
        if self._filtered_materials is None or refresh:
            if self._filters:
                self._filtered_materials = [
                    m.key
                    for m in self._server.get_materials(
                        lambda m: all(ffunc(m) for ffunc in self._filters)
                    )
                ]
            else:
                self._filtered_materials = [m.key for m in self._server.get_materials()]
        return self._filtered_materials

    def get(self) -> list[Block]:
        return self._filtered()[:]  # copy of cached list

    def getById(self, id: str) -> Block:
        element = self.equals(id).first()
        if element is None:
            raise_on_error(pb.Status(code=pb.BLOCK_TYPE_NOT_FOUND, extra=id))
        return element

    def first(self) -> Block | None:
        if len(self):
            return self[0]
        return None

    def choice(self) -> Block:
        return random.choice(self)

    def len(self) -> int:
        return len(self)

    # sequence methods

    def __len__(self) -> int:
        return len(self._filtered())

    def __getitem__(self, index) -> Block:
        return self._filtered()[index]

    def __iter__(self) -> Iterator[Block]:
        return iter(self._filtered())

    def __repr__(self):
        return f"{self.__class__.__name__}({self._filtered()!r}, len={len(self)})"

    # material properties

    def air(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_air is value])

    def block(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_block is value])

    def burnable(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_burnable is value])

    def edible(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_edible is value])

    def flammable(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_flammable is value])

    def fuel(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_fuel is value])

    def interactable(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_interactable is value])

    def item(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_item is value])

    def occluding(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_occluding is value])

    def solid(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(self._server, self._filters + [lambda m: m.is_solid is value])

    # additional infered properties

    def vanilla(self, value: bool = True, /) -> MaterialFilter:
        return self.__class__(
            self._server, self._filters + [lambda m: (m.key.namespace == "minecraft") is value]
        )

    def namespace(self, namespace: str, /, negate: bool = False) -> MaterialFilter:
        return self.__class__(
            self._server, self._filters + [lambda m: (m.key.namespace == namespace) is not negate]
        )

    # additional key filters

    def equals(self, *strings: str, negate: bool = False) -> MaterialFilter:
        return self.__class__(
            self._server, self._filters + [lambda m: (m.key in strings) is not negate]
        )

    def contains(self, *substrings: str, negate: bool = False) -> MaterialFilter:
        return self.__class__(
            self._server,
            self._filters + [lambda m: any(sub in m.key for sub in substrings) is not negate],
        )

    def startswith(self, *substrings: str, negate: bool = False) -> MaterialFilter:
        # TODO: ignore namespace: on startswith (add function to Block)
        return self.__class__(
            self._server,
            self._filters
            + [lambda m: any(m.key.startswith(sub) for sub in substrings) is not negate],
        )

    def endswith(self, *substrings: str, negate: bool = False) -> MaterialFilter:
        return self.__class__(
            self._server,
            self._filters
            + [lambda m: any(m.key.endswith(sub) for sub in substrings) is not negate],
        )
