from __future__ import annotations

import string
from collections import UserDict, UserList
from collections.abc import Mapping
from typing import Any, Iterable, Literal, MutableMapping, MutableSequence, TypeAlias

NONQUOTABLE_STR = string.digits + string.ascii_letters + "_-.+"


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
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max - 1})"
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
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max - 1})"
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
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max - 1})"
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
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max - 1})"
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
                f"{value} is out of range for {cls.__name__} (-{cls._max} to {cls._max - 1})"
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
            self.extend(iterable)

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

    def _check_no_cast_value(self, value: Any, /, dtype: type | None | False = False):
        v_dtype = type(value)
        has_dtype = self.dtype if dtype is False else dtype
        if has_dtype is None or has_dtype is v_dtype or (has_dtype is NbtByte and v_dtype is bool):
            return
        if isinstance(self, (NbtByteArray, NbtIntArray, NbtLongArray)):
            raise TypeError(f"Tried adding type {v_dtype.__name__} to {self.__class__.__name__}")
        else:
            raise TypeError(
                f"Tried adding type {v_dtype.__name__} to NbtList, but already contained type {has_dtype.__name__}"
            )

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
        for v in list(other) if other is self else other:
            self.append(v)

    def insert(self, index: int, item: Any) -> None:
        self.data.insert(index, self._convert_same_type(item))

    @property
    def bool(self):
        return TypedListView(self, bool)

    @property
    def byte(self):
        return TypedListView(self, NbtByte)

    @property
    def short(self):
        return TypedListView(self, NbtShort)

    @property
    def int(self):
        return TypedListView(self, NbtInt)

    @property
    def long(self):
        return TypedListView(self, NbtLong)

    @property
    def float(self):
        return TypedListView(self, NbtFloat)

    @property
    def double(self):
        return TypedListView(self, NbtDouble)

    @property
    def string(self):
        return TypedListView(self, str)

    @property
    def list(self):
        return TypedListView(self, NbtList)

    @property
    def compound(self):
        return TypedListView(self, NbtCompound)

    @property
    def byte_array(self):
        return TypedListView(self, NbtByteArray)

    @property
    def int_array(self):
        return TypedListView(self, NbtIntArray)

    @property
    def long_array(self):
        return TypedListView(self, NbtLongArray)


class TypedListView(MutableSequence):
    """A generic view of :class:`NbtList` that enforces values to be of a specific type."""

    def __init__(self, data: NbtList, dtype: type[NbtType]):
        self._data = data
        self._dtype = dtype

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self._dtype.__name__}]({repr(self._data)})"

    def _check_cast_type(self, value: Any) -> NbtType:
        tvalue = self._dtype(value)
        self._data._check_no_cast_value(tvalue)
        return tvalue

    def __getitem__(self, index: int) -> NbtType:
        return self._data[index]

    def __len__(self):
        return self._data.__len__()

    def __setitem__(self, index: int, value: Any):
        self._data.data[index] = self._check_cast_type(value)

    def __delitem__(self, index: int):
        del self._data[index]

    def append(self, value):
        return self._data.data.append(self._check_cast_type(value))

    def extend(self, values):
        return self._data.data.extend(self._check_cast_type(value) for value in values)

    def insert(self, index, value):
        return self._data.data.insert(index, self._check_cast_type(value))


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
    """A generic view of :class:`NbtCompound` that enforces values to be of a specific type."""

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
    KEYVALSEP = ":"

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        inner = []
        for key, val in self.items():
            if key and all((k in NONQUOTABLE_STR) for k in key):
                pair = f"{key}" + self.KEYVALSEP
            else:
                pair = escape_with_double_quotes(key) + self.KEYVALSEP

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


class ComponentData(NbtCompound):
    KEYVALSEP = "="

    def __str__(self):
        compound = super().__str__()
        return f"[{compound[1:-1]}]"

    def _set_no_value_check(self, key: str, value: NbtType) -> None:
        if not isinstance(key, str):
            raise ValueError(f"{key} is not a string, expecting all keys to be strings")
        if not all((k in NONQUOTABLE_STR) for k in key):
            raise ValueError(
                f"components may not have quoted keys, got {key} (may only contain characters: a-zA-Z0-9_-.+)"
            )
        return UserDict.__setitem__(self, key, value)


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


# TODO: replace this function with _parser parsing
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


NbtNumberType: TypeAlias = bool | NbtByte | NbtShort | NbtInt | NbtLong | NbtFloat | NbtDouble

NbtType: TypeAlias = (
    NbtNumberType | str | NbtList | NbtCompound | NbtByteArray | NbtIntArray | NbtLongArray
)
