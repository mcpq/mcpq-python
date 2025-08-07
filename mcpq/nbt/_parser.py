from ._snbt_and_component import GrammarError, Lark_StandAlone, LexError, ParseError, Transformer
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
    NbtShort,
    NbtType,
)


class TreeToNbt(Transformer):
    def string(self, s):
        (s,) = s
        quote = s[0]
        assert quote in ["'", '"'], f"quote was {quote}?!?"
        assert s[-1] == quote
        assert len(s) >= 2
        result = s[1:-1].replace("\\" + quote, quote).replace("\\\\", "\\")
        return result

    def unquoted_string(self, s):
        (s,) = s
        return s.value

    def bool(self, s):
        (s,) = s
        return s == "true"

    def array(self, s):
        type_ind, *elements = s
        if type_ind is None:
            l = NbtList()
            if not elements or elements == [None]:
                return l
            for element in elements:
                l._check_no_cast_value(element)
                l.data.append(element)
            return l

        match type_ind.value:
            case "B":
                return NbtByteArray(elements)
            case "I":
                return NbtIntArray(elements)
            case "L":
                return NbtLongArray(elements)
            case _:
                raise TypeError(f"Unknown type indicator {type_ind}")

    def compound(self, s):
        d = NbtCompound()
        if s[0] is None:
            # keeps None if empty
            return d
        for key, value in s:
            d._set_no_value_check(key, value)
        return d

    def component(self, s):
        debug_str = ",".join(f"{key}={value}" for key, value in s)
        debug_str = debug_str[: min(len(debug_str), 15)]
        raise GrammarError(
            f"Cannot parse data component in regular SNBT (component looks like: '[{debug_str}...]')"
        )

    pair = tuple
    component_pair = tuple

    byte = lambda self, s: NbtByte(*s)
    short = lambda self, s: NbtShort(*s)
    int = lambda self, s: NbtInt(*s)
    long = lambda self, s: NbtLong(*s)
    float = lambda self, s: NbtFloat(*s)
    double = lambda self, s: NbtDouble(*s)


class TreeToComponent(TreeToNbt):
    def component(self, s):
        d = ComponentData()
        # cannot be empty (to differentiate between NbtList)
        for key, value in s:
            d._set_no_value_check(key, value)
        return d


_snbt_parser = Lark_StandAlone(transformer=TreeToNbt())

_component_parser = Lark_StandAlone(transformer=TreeToComponent())


def parse_snbt(text: str) -> NbtType:
    return _snbt_parser.parse(text)


def parse_component(text: str) -> ComponentData:
    d = _component_parser.parse(text)
    if isinstance(d, ComponentData):
        return d
    if isinstance(d, NbtList) and not isinstance(d, (NbtByteArray, NbtIntArray, NbtLongArray)):
        if len(d) == 0:
            return ComponentData()
    raise TypeError(  # GrammarError
        f"Expected data component, but found SNBT type {d.__class__.__name__} instead"
    )


def try_parse_snbt(text: str) -> NbtType | None:
    try:
        return parse_snbt(text)
    except (LexError, ParseError, GrammarError, TypeError, ValueError):
        pass
    return None


def try_parse_component(text: str) -> ComponentData | None:
    try:
        return parse_component(text)
    except (LexError, ParseError, GrammarError, TypeError, ValueError):
        pass
    return None


#! python3 -m lark.tools.standalone --maybe_placeholders mcpq/_nbt/snbt_and_component.lark -o mcpq/_nbt/_snbt_and_component.py
