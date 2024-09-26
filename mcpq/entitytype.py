from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ._proto import minecraft_pb2 as pb


@dataclass(order=True, frozen=True)
class EntityType:
    key: str
    is_spawnable: bool = field(repr=False, hash=False, compare=False, kw_only=True)

    def __str__(self) -> str:
        return self.key

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def _build(cls, buffer: pb.EntityType) -> EntityType:
        return cls(
            buffer.key,
            is_spawnable=buffer.isSpawnable,
        )
