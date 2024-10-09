from __future__ import annotations

import json
import string
from collections import UserDict, UserList
from collections.abc import Mapping
from typing import Any, Iterable, MutableMapping, TypeAlias

NONQUOTABLE_STR = string.digits + string.ascii_letters + "_-.+"


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
    # has a limit, but not implemented here
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
    def _convert_same_type(self, value):
        dtype = self.dtype
        if dtype is None:
            value = default_nbt(value)
        elif not isinstance(value, dtype):
            if dtype is not NbtByte or not isinstance(value, bool):
                value = dtype(value)
        return value

    def __init__(self, iterable=None):
        super().__init__()
        if iterable is not None:
            for item in list(iterable):
                self.append(item)

    def __str__(self) -> str:
        dtype = self.dtype
        if dtype is None:
            # normal
            inner = ",".join(str(item) for item in iter(self))
        elif dtype is NbtByte:
            # lower() due to allowed bool
            inner = ",".join(str(item).lower() for item in iter(self))
        elif issubclass(dtype, str):
            # always enclose (is optional for nonquotables)
            inner = ",".join(escape_with_double_quotes(item) for item in iter(self))
        else:
            # normal
            inner = ",".join(str(item) for item in iter(self))
        return f"[{inner}]"

    def __setitem__(self, index: int, value: Any):
        self.data[index] = self._convert_same_type(value)

    @property
    def dtype(self) -> type[NbtType] | None:
        if len(self):
            dtype = type(self[0])
            if dtype is bool:
                return NbtByte
            return dtype

    def append(self, item: Any) -> None:
        self.data.append(self._convert_same_type(item))

    def extend(self, other: Iterable) -> None:
        self.data.extend(self._convert_same_type(v) for v in other)

    def insert(self, index: int, item: Any) -> None:
        self.data.insert(index, self._convert_same_type(item))


class NbtByteArray(NbtList):
    def _convert_same_type(self, value):
        # bool also allowed
        if not isinstance(value, (NbtByte, bool)):
            value = NbtByte(value)
        return value

    def __str__(self) -> str:
        # bool extra (lower)
        inner = ",".join(str(item).lower() for item in iter(self))
        return f"[B;{inner}]"

    @property
    def dtype(self) -> type[NbtByte]:
        return NbtByte


class NbtIntArray(NbtList):
    def __str__(self) -> str:
        inner = ",".join(str(item) for item in iter(self))
        return f"[I;{inner}]"

    @property
    def dtype(self) -> type[NbtInt]:
        return NbtInt


class NbtLongArray(NbtList):
    def __str__(self) -> str:
        inner = ",".join(str(item) for item in iter(self))
        return f"[L;{inner}]"

    @property
    def dtype(self) -> type[NbtLong]:
        return NbtLong


class TypedCompoundView(MutableMapping):
    """A generic view that enforces values to be of a specific type."""

    def __init__(self, compound: NbtCompound, dtype: type[NbtType]):
        self._compound = compound
        self._dtype = dtype

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self._dtype.__name__}]({repr(self._compound)})"

    def __setitem__(self, key: str, value: Any):
        value = self._dtype(value)
        self._compound._set_no_value_check(key, value)

    def __getitem__(self, key: str) -> NbtType:
        return self._compound[key]

    def __delitem__(self, key: str):
        del self._compound[key]

    def __iter__(self):
        return iter(self._compound)

    def __len__(self):
        return len(self._compound)

    def __contains__(self, key: str):
        return key in self._compound


class NbtCompound(UserDict[str, Any]):
    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        inner = []
        for key, val in self.items():
            if key and all((k in NONQUOTABLE_STR) for k in key):
                pair = f"{key}="
            else:
                pair = escape_with_double_quotes(key) + "="

            if isinstance(val, bool):
                pair += str(val).lower()
            elif isinstance(val, (NbtCompound, NbtList)):
                pair += str(val)
            elif isinstance(val, str):
                pair += escape_with_double_quotes(val)
            else:
                pair += str(val)
            inner.append(pair)
        return f"{{{','.join(inner)}}}"

    def _set_no_value_check(self, key: str, value: NbtType) -> None:
        if not isinstance(key, str):
            raise ValueError(f"{key} is not a string, expecting all keys to be strings")
        return super().__setitem__(key, value)

    def __setitem__(self, key: str, value: Any) -> None:
        value = default_nbt(value)
        return self._set_no_value_check(key, value)

    def update(self, iterable) -> None:
        for k, v in iterable.items() if isinstance(iterable, Mapping) else iterable:
            self[k] = v

    def get_or_create_nbt(self, name: str) -> NbtCompound:
        if name not in self or not isinstance(self[name], NbtCompound):
            self[name] = NbtCompound()
        return self[name]

    def get_or_create_list(self, name: str) -> NbtList:
        if name not in self or not isinstance(self[name], NbtList):
            self[name] = NbtList()
        return self[name]

    @property
    def bool(self):
        return TypedCompoundView(self, bool)

    @property
    def byte(self):
        return TypedCompoundView(self, NbtByte)

    @property
    def short(self):
        return TypedCompoundView(self, NbtShort)

    @property
    def int(self):
        return TypedCompoundView(self, NbtInt)

    @property
    def long(self):
        return TypedCompoundView(self, NbtLong)

    @property
    def float(self):
        return TypedCompoundView(self, NbtFloat)

    @property
    def double(self):
        return TypedCompoundView(self, NbtDouble)

    @property
    def string(self):
        return TypedCompoundView(self, str)

    @property
    def list(self):
        return TypedCompoundView(self, NbtList)

    @property
    def compound(self):
        return TypedCompoundView(self, NbtCompound)

    @property
    def byte_array(self):
        return TypedCompoundView(self, NbtByteArray)

    @property
    def int_array(self):
        return TypedCompoundView(self, NbtIntArray)

    @property
    def long_array(self):
        return TypedCompoundView(self, NbtLongArray)


def escape_with_double_quotes(s: str):
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


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
        nbt_number = parse_snbt_number(value)
        if nbt_number is not None:
            value = nbt_number
        # don't parse other compound types/str here, prob. not wanted implicitly
    elif isinstance(value, dict):
        value = NbtCompound(value)
    elif isinstance(value, list):
        value = NbtList(value)
    else:
        raise ValueError(
            f"{value} (type: {type(value)}) cannot automatically be converted to nbt type"
        )
    return value


def parse_snbt_number(value: str) -> NbtNumberType | None:
    if not value:
        return None
    if value in ["true", "false"]:
        return value == "true"
    if value.isdigit():
        return NbtInt(value)
    dots = value.count(".")
    if dots == 1 and value.replace(".", "", 1).isdigit():
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
        elif dots == 1 and front.replace(".", "", 1).isdigit():
            if back.lower() == "f":
                return NbtFloat(value)
            if back.lower() == "d":
                return NbtDouble(value)


def parse_snbt_string(value: str) -> str | None:
    "Parse value to 'normal (not snbt escaped)' Python string if entire value is valid string"
    if not value:
        return None  # empty is not valid without quotes

    def check_escapes(quote):
        escape = False
        for l in value[1:-1]:
            if escape:
                escape = False
                if l == "\\":
                    pass
                elif l != quote:
                    raise ValueError(f"`{value}` contains invalid escape character `{l}` ")
            elif l == "\\":
                escape = True
        if escape:
            raise ValueError(f"`{value}` incorrectly escapes \\")

    if value.startswith('"') and value.endswith('"'):
        check_escapes('"')
        normal = value.replace('\\"', '"').replace("\\\\", "\\")[1:-1]
        return normal
    elif value.startswith("'") and value.endswith("'"):
        check_escapes("'")
        normal = value.replace("\\'", "'").replace("\\\\", "\\")[1:-1]
        return normal
    elif all((l in NONQUOTABLE_STR) for l in value):
        return value


def parse_snbt_string_start(value: str) -> tuple[str, int]:
    "Parse the start of value for a valid string and return that substring and index of end of string"
    if not value:
        return "", 0

    # non quoted string
    if value[0] not in ["'", '"']:
        for i, l in enumerate(value):
            if l not in NONQUOTABLE_STR:
                break
        return value[:i], i

    # quoted string
    escape = False
    endstr = value[0]  # either ' or "
    for i in range(1, len(value)):
        l = value[i]
        if escape:
            escape = False
            if l == "\\":
                pass
            elif endstr != l:
                raise ValueError(f"`{value}` contains invalid escape character `{l}`")
        elif l == "\\":
            escape = True
        elif l == endstr:
            return value[1:i].replace("\\" + endstr, endstr).replace("\\\\", "\\"), i + 1
    raise ValueError(f"`{value}` string not correctly closed")


def parse_snbt(value: str) -> NbtType:
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
                # parsing strings happens further in
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
                if incomp < 0:
                    raise ValueError(f"`{inner}` incorrectly closed with `{l}`")
            elif l == "[":
                inlist += 1
            elif l == "]":
                inlist -= 1
                if inlist < 0:
                    raise ValueError(f"`{inner}` incorrectly closed with `{l}`")
            elif l == "," and incomp == 0 and inlist == 0:
                splits.append(i)
        if incomp:
            raise ValueError(f"`{inner}` incorrectly closes compounds {{}}")
        if inlist:
            raise ValueError(f"`{inner}` incorrectly closes lists []")
        if single or double:
            raise ValueError(f"`{inner}` incorrectly closes quotes \" or '")
        if escape:
            raise ValueError(f"`{inner}` incorrectly escapes \\")
        if not splits:  # only one single "thing" inside
            return [inner]
        result = []
        start = 0
        for i in splits + [len(inner)]:
            result.append(inner[start:i])
            start = i + 1
        return result

    if value.startswith("{") and value.endswith("}"):
        parts = split_on_comma(value[1:-1])
        keys_indices = [parse_snbt_string_start(part) for part in parts]
        for (_, index), part in zip(keys_indices, parts):
            if index == 0:
                raise ValueError(f"Missing key for '{part}' in '{value}'")
            if index == len(part):
                raise ValueError(f"Missing value for key '{part}' in '{value}'")
            if part[index] != "=":
                raise ValueError(
                    f"Found invalid separator '{part[index]}' (expected '=') in compound: {value}"
                )
        splits = [
            (key, parse_snbt(part[index + 1 :])) for (key, index), part in zip(keys_indices, parts)
        ]
        return NbtCompound(splits)
    elif value.startswith("[") and value.endswith("]"):
        if value.startswith("[B;"):
            data = [parse_snbt(part) for part in split_on_comma(value[3:-1])]
            ltype = NbtByteArray
            dtypes = (NbtByte, bool)
        elif value.startswith("[I;"):
            data = [parse_snbt(part) for part in split_on_comma(value[3:-1])]
            ltype = NbtIntArray
            dtypes = (NbtInt,)
        elif value.startswith("[L;"):
            data = [parse_snbt(part) for part in split_on_comma(value[3:-1])]
            ltype = NbtLongArray
            dtypes = (NbtLong,)
        else:
            data = [parse_snbt(part) for part in split_on_comma(value[1:-1])]
            ltype = NbtList
            dtypes = (type(data[0]) if data else None,)
            if NbtByte in dtypes or bool in dtypes:
                dtypes = (NbtByte, bool)
        for d in data:
            if type(d) not in dtypes:
                raise ValueError(
                    f"List element `{d}` does not have expected type of {' or '.join(t.__name__ for t in dtypes)} in `{value}`"
                )
        listobject = ltype()
        listobject.data.extend(data)
        return listobject
    elif (nbt_number := parse_snbt_number(value)) is not None:
        return nbt_number
    elif (nbt_string := parse_snbt_string(value)) is not None:
        return nbt_string
    else:
        raise ValueError(f"Cannot parse `{value}` to nbt")


NbtNumberType: TypeAlias = bool | NbtByte | NbtShort | NbtInt | NbtLong | NbtFloat | NbtDouble

NbtType: TypeAlias = (
    NbtNumberType | str | NbtList | NbtCompound | NbtByteArray | NbtIntArray | NbtLongArray
)


# TODO: replace NBT with NbtCompound (once tests are written)
class NBT(NbtCompound):
    def __init__(
        self,
        dict: dict[str, Any] | None = None,
        version: tuple[int, ...] | None = None,
        /,
        **kwargs,
    ):
        super().__init__(dict, **kwargs)
        self.version = version

    def __str__(self) -> str:
        return json.dumps(self)

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
