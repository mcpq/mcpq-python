from ._block import Block
from ._parser_wrapper import parse_snbt
from ._types import (
    ComponentData,
    NbtByte,
    NbtByteArray,
    NbtCompound,
    NbtDouble,
    NbtFloat,
    NbtInt,
    NbtIntArray,
    NbtList,
    NbtLong,
    NbtLongArray,
    NbtNumberType,
    NbtShort,
    NbtType,
)

EntityType = Block

# TODO: in the future, make NBT a builder with helper functions
NBT = NbtCompound


__all__ = [
    "NbtByte",
    "NbtByteArray",
    "NbtCompound",
    "NbtDouble",
    "NbtFloat",
    "NbtInt",
    "NbtIntArray",
    "NbtList",
    "NbtLong",
    "NbtLongArray",
    "NbtShort",
    "ComponentData",
    "NbtType",
    "NbtNumberType",
    "parse_snbt",
    "EntityType",
    "Block",
    "NBT",
]
