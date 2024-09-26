from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ._proto import minecraft_pb2 as pb


@dataclass(order=True, frozen=True)
class Material:
    key: str
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
            buffer.key,
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
