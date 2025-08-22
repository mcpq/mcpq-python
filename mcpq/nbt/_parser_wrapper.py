from ._types import ComponentData, NbtCompound, NbtNumberType, NbtType


def parse_snbt(text: str) -> NbtType:
    from ._parser import parse_snbt

    # only load .parser when necessary

    return parse_snbt(text)


def parse_component(text: str) -> ComponentData:
    from ._parser import parse_component

    # only load .parser when necessary

    return parse_component(text)


def try_parse_snbt(text: str) -> NbtType | None:
    from ._parser import try_parse_snbt

    # only load .parser when necessary

    return try_parse_snbt(text)


def try_parse_component(text: str) -> ComponentData | None:
    from ._parser import try_parse_component

    # only load .parser when necessary

    return try_parse_component(text)


def parse_compound(text: str) -> NbtCompound:
    nbttype = parse_snbt(text)
    if not isinstance(nbttype, NbtCompound):
        raise TypeError(
            f"The parsed string is of type '{type(nbttype).__name__}' expected 'NbtCompound'"
        )
    return nbttype


def try_parse_number(value: str) -> NbtNumberType | None:
    if value:
        num = try_parse_snbt(value)
        if isinstance(num, NbtNumberType):
            return num
    return None
