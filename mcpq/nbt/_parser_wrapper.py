from ._types import ComponentData, NbtType


def parse_snbt(text: str) -> NbtType:
    from ._parser import parse_snbt

    # only load .parser when necessary

    return parse_snbt(text)


def parse_component(text: str) -> ComponentData:
    from ._parser import parse_component

    # only load .parser when necessary

    return parse_component(text)
