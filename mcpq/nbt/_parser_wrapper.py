from ._types import ComponentData, NbtCompound, NbtType


def parse_snbt(text: str) -> NbtType:
    from ._parser import parse_snbt

    # only load .parser when necessary

    return parse_snbt(text)


def parse_component(text: str) -> ComponentData:
    from ._parser import parse_component

    # only load .parser when necessary

    return parse_component(text)


def parse_compound(text: str) -> NbtCompound:
    nbttype = parse_snbt(text)
    if not isinstance(nbttype, NbtCompound):
        raise TypeError(
            f"The parsed string is not of type NbtCompound but {type(nbttype).__name__}"
        )
    return nbttype
