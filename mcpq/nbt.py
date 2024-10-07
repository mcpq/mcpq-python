from __future__ import annotations

import json
import string
from collections import UserDict, UserList
from collections.abc import Mapping
from typing import Any, Dict, Generic, TypeAlias, TypeVar


# TODO: replace NBT with NbtCompound (once tests are written)
class NBT(dict[str, Any]):
    def __str__(self) -> str:
        return json.dumps(self)

    def get_or_create_nbt(self, value: str) -> NBT:
        if value not in self:
            self[value] = NBT()
        return self[value]

    def get_or_create_list(self, value: str) -> list[NBT | str]:
        if value not in self:
            self[value] = []
        return self[value]

    def set_unbreakable(self) -> None:
        self["Unbreakable"] = 1

    def set_name(self, text: str, italics: bool = True) -> None:
        itstr = str(bool(italics)).lower()
        self.get_or_create_nbt("display")["Name"] = f'[{{"text": "{text}", "italic": {itstr}}}]'

    def add_lore(self, text: str) -> None:
        self.get_or_create_nbt("display").get_or_create_list("Lore").append(f'"{text}"')

    def add_can_place_on(self, block: str) -> None:
        self.get_or_create_list("CanPlaceOn").append(block)

    def add_can_destroy(self, block: str) -> None:
        self.get_or_create_list("CanDestroy").append(block)

    def add_enchantment(self, enchantment: str, level: int = 1) -> None:
        tag = NBT({"id": enchantment, "lvl": level})
        self.get_or_create_list("Enchantments").append(tag)

    def add_aqua_affinity(self, level: int = 1) -> None:
        self.add_enchantment("aqua_affinity", level)

    def add_bane_of_arthropods(self, level: int = 1) -> None:
        self.add_enchantment("bane_of_arthropods", level)

    def add_blast_protection(self, level: int = 1) -> None:
        self.add_enchantment("blast_protection", level)

    def add_channeling(self, level: int = 1) -> None:
        self.add_enchantment("channeling", level)

    def add_binding_curse(self, level: int = 1) -> None:
        self.add_enchantment("binding_curse", level)

    def add_vanishing_curse(self, level: int = 1) -> None:
        self.add_enchantment("vanishing_curse", level)

    def add_depth_strider(self, level: int = 1) -> None:
        self.add_enchantment("depth_strider", level)

    def add_efficiency(self, level: int = 1) -> None:
        self.add_enchantment("efficiency", level)

    def add_feather_falling(self, level: int = 1) -> None:
        self.add_enchantment("feather_falling", level)

    def add_fire_aspect(self, level: int = 1) -> None:
        self.add_enchantment("fire_aspect", level)

    def add_fire_protection(self, level: int = 1) -> None:
        self.add_enchantment("fire_protection", level)

    def add_flame(self, level: int = 1) -> None:
        self.add_enchantment("flame", level)

    def add_fortune(self, level: int = 1) -> None:
        self.add_enchantment("fortune", level)

    def add_frost_walker(self, level: int = 1) -> None:
        self.add_enchantment("frost_walker", level)

    def add_impaling(self, level: int = 1) -> None:
        self.add_enchantment("impaling", level)

    def add_infinity(self, level: int = 1) -> None:
        self.add_enchantment("infinity", level)

    def add_knockback(self, level: int = 1) -> None:
        self.add_enchantment("knockback", level)

    def add_looting(self, level: int = 1) -> None:
        self.add_enchantment("looting", level)

    def add_loyalty(self, level: int = 1) -> None:
        self.add_enchantment("loyalty", level)

    def add_luck_of_the_sea(self, level: int = 1) -> None:
        self.add_enchantment("luck_of_the_sea", level)

    def add_lure(self, level: int = 1) -> None:
        self.add_enchantment("lure", level)

    def add_mending(self, level: int = 1) -> None:
        self.add_enchantment("mending", level)

    def add_multishot(self, level: int = 1) -> None:
        self.add_enchantment("multishot", level)

    def add_piercing(self, level: int = 1) -> None:
        self.add_enchantment("piercing", level)

    def add_power(self, level: int = 1) -> None:
        self.add_enchantment("power", level)

    def add_projectile_protection(self, level: int = 1) -> None:
        self.add_enchantment("projectile_protection", level)

    def add_protection(self, level: int = 1) -> None:
        self.add_enchantment("protection", level)

    def add_punch(self, level: int = 1) -> None:
        self.add_enchantment("punch", level)

    def add_quick_charge(self, level: int = 1) -> None:
        self.add_enchantment("quick_charge", level)

    def add_respiration(self, level: int = 1) -> None:
        self.add_enchantment("respiration", level)

    def add_riptide(self, level: int = 1) -> None:
        self.add_enchantment("riptide", level)

    def add_sharpness(self, level: int = 1) -> None:
        self.add_enchantment("sharpness", level)

    def add_silk_touch(self, level: int = 1) -> None:
        self.add_enchantment("silk_touch", level)

    def add_smite(self, level: int = 1) -> None:
        self.add_enchantment("smite", level)

    def add_soul_speed(self, level: int = 1) -> None:
        self.add_enchantment("soul_speed", level)

    def add_sweeping(self, level: int = 1) -> None:
        self.add_enchantment("sweeping", level)

    def add_swift_sneak(self, level: int = 1) -> None:
        self.add_enchantment("swift_sneak", level)

    def add_thorns(self, level: int = 1) -> None:
        self.add_enchantment("thorns", level)

    def add_unbreaking(self, level: int = 1) -> None:
        self.add_enchantment("unbreaking", level)


# TODO: use BlockKey for materials/block types (add nbt as well)
class BlockKey(str):
    def __repr__(self) -> str:
        if "[" in self:
            return f"'{self.type}{self.data}'"
        return f"'{self.type}'"

    # TODO: repr/str

    def __eq__(self, value: object) -> bool:
        if isinstance(value, BlockKey):
            return self.id == value.id
        if isinstance(value, str):
            return self.id == value or self.type == value or super().__eq__(value)
        return super().__eq__(value)

    def __ne__(self, value: object) -> bool:
        return not self == value

    def __le__(self, value: str) -> bool:
        if isinstance(value, BlockKey):
            return self.id <= value.id
        return self.id <= value

    def __ge__(self, value: str) -> bool:
        if isinstance(value, BlockKey):
            return self.id >= value.id
        return self.id >= value

    def __lt__(self, value: str) -> bool:
        if isinstance(value, BlockKey):
            return self.id < value.id
        return self.id < value

    def __gt__(self, value: str) -> bool:
        if isinstance(value, BlockKey):
            return self.id > value.id
        return self.id > value

    @property
    def id(self) -> str:
        rest = self[: self.index("[")] if "[" in self else self[:]
        if ":" in rest:
            return rest
        return "minecraft:" + rest

    @property
    def type(self) -> str:
        if "[" in self:
            return self[: self.index("[")].removeprefix("minecraft:")
        return self.removeprefix("minecraft:")

    @property
    def namespace(self) -> str:
        if ":" in self:
            return self[: self.index(":")]
        return "minecraft"

    @property
    def data(self) -> str:
        if "[" in self:
            return self[self.index("[") :]
        return "[]"

    @property
    def dataDict(self) -> dict[str, bool | int | str]:
        return self._parse_data(self.data)

    @staticmethod
    def _parse_data(data: str) -> dict[str, bool | int | str]:
        "Parse data of form: '[key1=value1,key2=value2,...]'"
        data = data[1:-1]
        d = {}
        if not data.strip():
            return d
        for entry in data.split(","):
            key, val = entry.split("=")
            if val == "true" or val == "false":
                d[key] = val == "true"
                continue
            try:
                d[key] = int(val)
                continue
            except ValueError:
                pass
            d[key] = val
        return d

    def addData(self, data: dict[str, bool | int | str] | str | BlockKey) -> BlockKey:
        if isinstance(data, BlockKey):
            data = data.dataDict
        elif isinstance(data, str):
            if len(data) < 2 or data[0] != "[" or data[-1] != "]":
                raise ValueError("Expected data in form: '[key1=value1,key2=value2,...]'")
            if " " in data:
                raise ValueError("Did not expect spaces in data")
            # TODO: more checks?
            data = self._parse_data(data)

        combined = self.dataDict | data
        inner = ",".join(f"{key.lower()}={str(val).lower()}" for key, val in combined.items())
        return BlockKey(f"{self.type}[{inner}]")

    def withData(self, data: dict[str, bool | int | str] | str) -> BlockKey:
        return BlockKey(self.id).addData(data)


class NbtByte(int):
    _max = 2**7
    _end = "b"

    def __new__(cls, value, base=None):
        if isinstance(value, str):
            value = value.strip()
            if value and (value[-1] == cls._end.lower() or value[-1] == cls._end.upper()):
                value = value[:-1]
            value = int(value, 10 if base is None else base)
        elif base is not None:
            raise TypeError("can't convert non-string with explicit base")
        else:
            value = int(value)
        if not (-cls._max <= value < cls._max):
            raise ValueError(
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max-1})"
            )
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f"{super().__str__()}{self._end}"


class NbtShort(int):
    _max = 2**15
    _end = "s"

    def __new__(cls, value, base=None):
        if isinstance(value, str):
            value = value.strip()
            if value and (value[-1] == cls._end.lower() or value[-1] == cls._end.upper()):
                value = value[:-1]
            value = int(value, 10 if base is None else base)
        elif base is not None:
            raise TypeError("can't convert non-string with explicit base")
        else:
            value = int(value)
        if not (-cls._max <= value < cls._max):
            raise ValueError(
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max-1})"
            )
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f"{super().__str__()}{self._end}"


class NbtInt(int):
    _max = 2**31

    def __new__(cls, value, base=None):
        value = int(value) if base is None else int(value, base)
        if not (-cls._max <= value < cls._max):
            raise ValueError(
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max-1})"
            )
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f"{super().__str__()}"


class NbtLong(int):
    _max = 2**63
    _end = "l"

    def __new__(cls, value, base=None):
        if isinstance(value, str):
            value = value.strip()
            if value and (value[-1] == cls._end.lower() or value[-1] == cls._end.upper()):
                value = value[:-1]
            value = int(value, 10 if base is None else base)
        elif base is not None:
            raise TypeError("can't convert non-string with explicit base")
        else:
            value = int(value)
        if not (-cls._max <= value < cls._max):
            raise ValueError(
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max-1})"
            )
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f"{super().__str__()}{self._end}"


class NbtFloat(float):
    _max = 3.4 * 10**38
    _end = "f"

    def __new__(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value and (value[-1] == cls._end.lower() or value[-1] == cls._end.upper()):
                value = value[:-1]
        value = float(value)
        if not (-cls._max <= value < cls._max):
            raise ValueError(
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max-1})"
            )
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f"{super().__str__()}{self._end}"


class NbtDouble(float):
    _end = "d"  # optional

    def __new__(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value and (value[-1] == cls._end.lower() or value[-1] == cls._end.upper()):
                value = value[:-1]
        value = float(value)
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f"{super().__str__()}"  # d optional


class NbtList(UserList):
    def _convert_same_type_and_insert(self, index, value):
        if len(self) > 0:
            hastype = type(self[0])
            if not isinstance(value, hastype):
                value = hastype(value)
        else:
            value = default_nbt(value)
        self.data.insert(index, value)

    def __init__(self, iterable=None):
        super().__init__()
        if iterable is not None:
            for index, item in enumerate(list(iterable)):
                self[index] = item

    def __str__(self) -> str:
        inner = ",".join(str(item) for item in iter(self))
        return f"[{inner}]"

    def __setitem__(self, index: int, value: Any):
        self._convert_same_type_and_insert(index, value)

    def insert(self, i: int, item: Any) -> None:
        self._convert_same_type_and_insert(i, item)

    def append(self, item: Any) -> None:
        self._convert_same_type_and_insert(len(self), item)


class NbtByteArray(NbtList):
    def _convert_same_type_and_insert(self, index, value):
        if not isinstance(value, (NbtByte, bool)):
            value = NbtByte(value)
        self.data.insert(index, value)

    def __str__(self) -> str:
        inner = ",".join(str(item).lower() for item in iter(self))
        return f"[B;{inner}]"


class NbtIntArray(NbtList):
    def _convert_same_type_and_insert(self, index, value):
        if not isinstance(value, NbtInt):
            value = NbtInt(value)
        self.data.insert(index, value)

    def __str__(self) -> str:
        inner = ",".join(str(item).lower() for item in iter(self))
        return f"[I;{inner}]"


class NbtLongArray(NbtList):
    def _convert_same_type_and_insert(self, index, value):
        if not isinstance(value, NbtLong):
            value = NbtLong(value)
        self.data.insert(index, value)

    def __str__(self) -> str:
        inner = ",".join(str(item).lower() for item in iter(self))
        return f"[L;{inner}]"


T = TypeVar("T")


class TypedView(dict[str, T], Generic[T]):
    """A generic view that enforces values to be of a specific type."""

    def __init__(self, original_dict: Dict[str, Any], value_type: type[T]):
        self._original_dict = original_dict
        self._value_type = value_type

    def __setitem__(self, key: str, value: Any):
        self._original_dict[key] = self._value_type(value)

    def __getitem__(self, key: str) -> Any:
        return self._original_dict[key]

    def __delitem__(self, key: str):
        del self._original_dict[key]

    def __iter__(self):
        return iter(self._original_dict)

    def __len__(self):
        return len(self._original_dict)

    def __contains__(self, key: str):
        return key in self._original_dict


class NbtCompound(UserDict[str, Any]):
    _nonquotable = string.digits + string.ascii_letters + "_-.+"

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        inner = []
        for key, val in self.items():
            if all((k in self._nonquotable) for k in key):
                pair = f"{key}="
            else:
                pair = f'"{key}"='

            if isinstance(val, bool):
                pair += str(val).lower()
            elif isinstance(val, (NbtCompound, NbtList)):
                pair += str(val)
            elif isinstance(val, str):
                pair += f'"{str(val)}"'
            else:
                pair += str(val)
            inner.append(pair)
        return f"{{{','.join(inner)}}}"

    def __setitem__(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise ValueError(f"{key} is not a string, expecting all keys to be strings")
        value = default_nbt(value)
        return super().__setitem__(key, value)

    def update(self, iterable) -> None:
        for k, v in iterable.items() if isinstance(iterable, Mapping) else iterable:
            self[k] = v

    def get_or_create_nbt(self, name: str) -> NbtCompound:
        if name not in self or not isinstance(self[name], NbtCompound):
            self[name] = NbtCompound()
        return self[name]

    def get_or_create_list(self, name: str) -> list[NbtType]:
        if name not in self or not isinstance(self[name], NbtList):
            self[name] = NbtList()
        return self[name]

    @property
    def bool(self):
        return TypedView(self, bool)

    @property
    def byte(self):
        return TypedView(self, NbtByte)

    @property
    def short(self):
        return TypedView(self, NbtShort)

    @property
    def int(self):
        return TypedView(self, NbtInt)

    @property
    def long(self):
        return TypedView(self, NbtLong)

    @property
    def float(self):
        return TypedView(self, NbtFloat)

    @property
    def double(self):
        return TypedView(self, NbtDouble)

    @property
    def string(self):
        return TypedView(self, str)

    @property
    def list(self):
        return TypedView(self, NbtList)

    @property
    def compound(self):
        return TypedView(self, NbtCompound)

    @property
    def byte_array(self):
        return TypedView(self, NbtByteArray)

    @property
    def int_array(self):
        return TypedView(self, NbtIntArray)

    @property
    def long_array(self):
        return TypedView(self, NbtLongArray)


def default_nbt(
    value: Any,
) -> NbtType:
    if isinstance(
        value,
        (
            NbtByte,
            NbtShort,
            NbtInt,
            NbtLong,
            NbtFloat,
            NbtDouble,
            NbtList,
            NbtCompound,
            NbtByteArray,
            NbtIntArray,
            NbtLongArray,
        ),
    ):
        pass
    elif isinstance(value, bool):
        pass  # allow std. bool
    elif isinstance(value, int):
        # if -(2**7) <= value < 2**7:
        #     value = NbtByte(value)
        if -(2**31) <= value < 2**31:
            value = NbtInt(value)
        else:
            value = NbtLong(value)
    elif isinstance(value, float):
        value = NbtDouble(value)
    elif isinstance(value, str):
        pass
    elif isinstance(value, dict):
        value = NbtCompound(value)
    elif isinstance(value, list):
        value = NbtList(value)
    else:
        raise ValueError(f"{value} cannot automatically be converted to nbt type")
    return value


def parse_snbt(value: str) -> NbtType:
    nonquotable = string.digits + string.ascii_letters + "_-.+"
    if value in ["true", "false"]:
        return value == "true"
    if value.isdigit():
        return NbtInt(value)
    dots = value.count(".")
    if dots == 1 and value.replace(".", "").isdigit():
        return NbtDouble(value)
    if len(value) > 1:
        front, back = value[:-1], value[-1]
        if front.isdigit():
            if back.lower() == "b":
                return NbtByte(value)
            if back.lower() == "s":
                return NbtShort(value)
            if back.lower() == "l":
                return NbtLong(value)
        elif dots == 1 and front.replace(".", "").isdigit():
            if back.lower() == "f":
                return NbtFloat(value)
            if back.lower() == "d":
                return NbtDouble(value)

    def split_on_comma(inner: str) -> list[str]:
        if not inner:
            return []
        splits = []
        incomp = 0
        inlist = 0
        single = False
        double = False
        escape = False
        for i in range(0, len(inner)):
            l = inner[i]
            if escape:
                escape = False
            elif l == "\\":
                escape = True
            elif single:
                if l == "'":
                    single = False
            elif double:
                if l == '"':
                    double = False
            elif l == "'":
                single = True
            elif l == '"':
                double = True
            elif l == "{":
                incomp += 1
            elif l == "}":
                incomp -= 1
                assert incomp >= 0
            elif l == "[":
                inlist += 1
            elif l == "]":
                inlist -= 1
                assert inlist >= 0
            elif l == "," and incomp == 0 and inlist == 0:
                splits.append(i)
        if not splits:  # only one single "thing" inside
            return [inner]
        result = []
        start = 0
        for i in splits + [len(inner)]:
            result.append(inner[start:i])
            start = i + 1
        return result

    def startingstring(inner: str) -> tuple[str, int]:
        if not inner:
            return "", 0

        # non quoted string
        if inner[0] not in ["'", '"']:
            for i, l in enumerate(inner):
                if l not in nonquotable:
                    break
            return inner[:i], i

        # quoted string
        escape = False
        endstr = inner[0]  # either ' or "
        for i in range(1, len(inner)):
            l = inner[i]
            if escape:
                escape = False
            elif l == "\\":
                escape = True
            elif l == endstr:
                return inner[1:i], i + 1
        raise ValueError(f"'{inner}' str not correctly closed")

    if value.startswith("{") and value.endswith("}"):
        parts = split_on_comma(value[1:-1])
        indices = [startingstring(part) for part in parts]
        assert all(
            part[index] == "=" for (_, index), part in zip(indices, parts)
        ), f"Found invalid separator (not '=') in compound: {value}"
        splits = [
            (key, parse_snbt(part[index + 1 :])) for (key, index), part in zip(indices, parts)
        ]
        return NbtCompound(splits)
    elif value.startswith("[") and value.endswith("]"):
        if value.startswith("[B;"):
            return NbtByteArray([parse_snbt(part) for part in split_on_comma(value[3:-1])])
        elif value.startswith("[I;"):
            return NbtIntArray([parse_snbt(part) for part in split_on_comma(value[3:-1])])
        elif value.startswith("[L;"):
            return NbtLongArray([parse_snbt(part) for part in split_on_comma(value[3:-1])])
        else:
            return NbtList([parse_snbt(part) for part in split_on_comma(value[1:-1])])
    elif value.startswith('"') and value.endswith('"'):
        nstr, endindex = startingstring(value)
        assert endindex == len(value), f"Incorrect quoting of str: {value} ({nstr} -> {endindex})"
        return nstr
    elif value.startswith("'") and value.endswith("'"):
        nstr, endindex = startingstring(value)
        assert endindex == len(value), f"Incorrect quoting of str: {value} ({nstr} -> {endindex})"
        return nstr
    elif all(l in nonquotable for l in value):
        return value
    else:
        raise ValueError(f"Cannot parse '{value}' to nbt")


NbtType: TypeAlias = (
    bool
    | NbtByte
    | NbtShort
    | NbtInt
    | NbtLong
    | NbtFloat
    | NbtDouble
    | str
    | NbtList
    | NbtCompound
    | NbtByteArray
    | NbtIntArray
    | NbtLongArray
)


if __name__ == "__main__":
    from pprint import pp

    blocks = [
        BlockKey("spruce_stairs"),
        BlockKey("minecraft:spruce_stairs"),
        BlockKey("spruce_stairs[waterlogged=true]"),
        BlockKey("spruce_stairs[waterlogged=true,facing=south]"),
        BlockKey("minecraft:spruce_stairs[waterlogged=true]"),
        BlockKey("minecraft:spruce_stairs[waterlogged=true,facing=south]"),
        BlockKey("my_mod:superblock"),
        BlockKey("my_mod:superblock[waterlogged=true]"),
        BlockKey("my_mod:superblock[waterlogged=true,facing=south]"),
        BlockKey("stone"),
        BlockKey("air"),
        BlockKey("waxed_copper_stairs"),
    ]
    print(blocks)
    pp(sorted(blocks))
    print(f"{str(blocks[0])=}  - {type(str(blocks[0]))=}")
    # for b1 in sorted(blocks):
    #     for b2 in sorted(blocks):
    #         print(f"{b1 == b2}: {b1} == {b2}")
    #         if b1 == b2:
    #             assert not (b1 != b2)
    #         else:
    #             assert b1 != b2
    print([b.id for b in blocks])
    print([b.type for b in blocks])
    print([b.namespace for b in blocks])
    print([b.data for b in blocks])
    print([b.dataDict for b in blocks])

    nbt = NbtCompound()
    nbt.byte["key1"] = 0
    nbt.byte["key2"] = "1b"
    print(nbt)
    assert nbt.byte["key1"] == 0
    snbt = '{"a"=1,b=2,c={hudel=5,baum=4b,k=[1,2,3],"view"=[L;1L,5L]}}'
    print(snbt)
    new = parse_snbt(snbt)
    print("->")
    print(new)
    print()

    snbt = '{"a"=1,b=2,c={hudel=5,"lol"="what is this",baum=4b,k=[1,2,3],"view"=[B;1b,5B],name="two double \\\\michae\\"le",normal=michaele123,humbu=3.3.f}}'
    print(snbt)
    new = parse_snbt(snbt)
    print("->")
    print(new)
    print()
