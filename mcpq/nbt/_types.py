from __future__ import annotations

import string
from collections import UserDict, UserList
from collections.abc import Mapping
from typing import Any, Iterable, MutableMapping, MutableSequence, TypeAlias

NONQUOTABLE_STR = string.digits + string.ascii_letters + "_-.+"


class NbtByte(int):
    """Signed 8-bit integer and subclass of :class:`int`.
    Both 1b == True and 0b == False are true as booleans just represent 0 and 1 byte."""

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
    """Signed 16-bit integer and subclass of :class:`int`"""

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
    """Signed 32-bit integer and subclass of :class:`int`"""

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
    """Signed 64-bit integer and subclass of :class:`int`"""

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
    """Signed float with limit ±3.4e+38 and subclass of :class:`float`"""

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
    """Subclass of :class:`float`"""

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
    """:class:`NbtList` behaves like a python list with the exception that all its elements must have the same nbt type.
    When the list is empty any nbt type can be added but once an element was added the list (and conversions) are defined by the first element's type.
    """

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

    def __eq__(self, value: object) -> bool:
        if id(self) == id(value):
            return True
        if type(self) is not type(value):
            if isinstance(value, (list, UserList)):
                try:
                    value = self.__class__(value)
                except Exception:
                    return False
            else:
                return False
        if len(self) != len(value):
            return False
        for v, o in zip(self, value):
            if isinstance(v, bool) and isinstance(o, NbtByte):
                if (v is True and o != 1) or (v is False and o != 0):
                    break
            elif isinstance(v, NbtByte) and isinstance(o, bool):
                if (v != 1 and o is True) or (v != 0 and o is False):
                    break
            elif type(v) is not type(o):
                break
            else:
                if v != o:
                    break
        else:
            return True
        return False

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
    def bool(self) -> TypedListView[bool]:
        return TypedListView(self, bool)

    @property
    def byte(self) -> TypedListView[NbtByte]:
        return TypedListView(self, NbtByte)

    @property
    def short(self) -> TypedListView[NbtShort]:
        return TypedListView(self, NbtShort)

    @property
    def int(self) -> TypedListView[NbtInt]:
        return TypedListView(self, NbtInt)

    @property
    def long(self) -> TypedListView[NbtLong]:
        return TypedListView(self, NbtLong)

    @property
    def float(self) -> TypedListView[NbtFloat]:
        return TypedListView(self, NbtFloat)

    @property
    def double(self) -> TypedListView[NbtDouble]:
        return TypedListView(self, NbtDouble)

    @property
    def string(self) -> TypedListView[str]:
        return TypedListView(self, str)

    @property
    def list(self) -> TypedListView[NbtList]:
        return TypedListView(self, NbtList)

    @property
    def compound(self) -> TypedListView[NbtCompound]:
        return TypedListView(self, NbtCompound)

    @property
    def byte_array(self) -> TypedListView[NbtByteArray]:
        return TypedListView(self, NbtByteArray)

    @property
    def int_array(self) -> TypedListView[NbtIntArray]:
        return TypedListView(self, NbtIntArray)

    @property
    def long_array(self) -> TypedListView[NbtLongArray]:
        return TypedListView(self, NbtLongArray)


class TypedListView(MutableSequence):
    """A generic view of :class:`NbtList` that enforces values to be of a specific type and subclass of :class:`list`."""

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
    """Subclass of :class:`NbtList`."""

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
    """Subclass of :class:`NbtList`."""

    def __str__(self) -> str:
        inner = ",".join(str(item) for item in iter(self))
        return f"[I;{inner}]"

    @property
    def dtype(self) -> type[NbtInt]:
        return NbtInt


class NbtLongArray(NbtList):
    """Subclass of :class:`NbtList`."""

    def __str__(self) -> str:
        inner = ",".join(str(item) for item in iter(self))
        return f"[L;{inner}]"

    @property
    def dtype(self) -> type[NbtLong]:
        return NbtLong


class TypedCompoundView(MutableMapping):
    """A generic view of :class:`NbtCompound` that enforces values to be of a specific type and subclass of :class:`dict`."""

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
    """The definitive class for parsing and manipulating NBT-format_ data.
    It can be used like a python dict with the exception that its keys must be strings.
    It can also be passed a dict at initialization which will be automatically converted (see convertion rules below).

    Alias :class:`NBT` of :class:`NbtCompound`.

    .. _NBT-format: https://minecraft.wiki/w/NBT_format

    .. code::

       from mcpq import Minecraft, Vec3, NBT
       mc = Minecraft()
       nbt = NBT()  # create new NBT dictionary, called a compound in NBT format
       # its keys must always be strings
       nbt["bool_key"] = True  # will be converted to byte 1 (=`true`)
       nbt["int_key"] = 1  # will be converted to int (or long if number is too large)
       nbt["double_key"] = 1.4  # will be converted to double
       nbt["string_key"] = "not a number text"  # will stay a string (see number conversion below)
       # for lists and dicts: all internal values will be recursively converted
       nbt["list_key"] = [1,2,3]  # will be converted to nbt-list of int
       nbt["compound_key"] = {"waterlogged": True}  # will be converted to compound
       # compounds and lists can also be created/got and directly returned like so:
       inner_compound = nbt.get_or_create_nbt("compound_key")  # get compound set above
       inner_compound["waterlogged"] = False  # overwrite nbt["compound_key"]["waterlogged"]
       nbt.get_or_create_list("list_key").extend([4,5,6])  # append to upper list

       # to easier convert to different number types, string-numbers will be parsed like so:
       nbt["bool_key"] = "true"  # will be converted to byte 1 (=`true`)
       nbt["byte_key"] = "1b"  # will be converted to byte 1
       nbt["short_key"] = "1s"  # will be converted to short 1
       nbt["int_key"] = "1"  # will be converted to int 1
       nbt["long_key"] = "1l"  # will be converted to long 1
       nbt["float_key"] = "1.4f"  # will be converted to float 1.4
       nbt["double_key"] = "1.4"  # will be converted to double 1.4

       # to enforce a certain type during conversion use the corresponding property:
       nbt.string["string_key"] = "1b"  # will STAY a string `"1b"` and not be converted
       nbt.string["key"] = {"text": "hi"}  # will be converted to string, not compound
       nbt.byte_array["key"] = [1,2,3]  # will be converted to byte-array instead of nbt-list of int
       nbt.short["short_key"] = 1  # will be converted to short, not int

       # types are also checked on equality checks of compounds and lists:
       NBT({"check": True}) == NBT({"check": "1b"})  # true (true == 1b)
       NBT({"check": True}) == NBT({"check": "true"})  # true (true == true)
       NBT({"check": 1}) == NBT({"check": "1s"})  # false
       NBT({"check": "1.4d"}) == NBT({"check": "1.4f"})  # false
       # but NOT for primitive type checks, there the base type comparison is used:
       NBT({"check": True})["check"] == NBT({"check": "1b"})["check"]  # true (int compare)
       NBT({"check": True})["check"] == NBT({"check": "true"})["check"]  # true (int compare)
       NBT({"check": 1})["check"] == NBT({"check": "1s"})["check"]  # true (int compare)
       NBT({"check": "1.4d"})["check"] == NBT({"check": "1.4f"})["check"]  # true (float compare)

       snbt = str(nbt)  # convert to snbt (string NBT)
       print(str(NBT({"key1": "value1", "key 2": 2})))
       # >>> '{key1:"value1","key 2":2}'

       # this can then be used for commands or other operations, for example:
       # to remove the AI and remove sound from a cow spawned at 0 0
       nbt = NBT({"NoAI": "1b", "Silent": "1b"})
       cow = mc.spawnEntity("cow", mc.getHeighestPos(0, 0).up())
       cow.runCommand(f"data merge entity @s {nbt}")
    """

    KEYVALSEP = ":"

    @classmethod
    def parse(cls, string: str) -> NbtCompound:
        """Parse `string` of a compound in SNBT-format to :class:`NBT`.

        .. code::

           from mcpq import Minecraft, Vec3, NBT
           nbt = NBT.parse('{key1:"value1",key2:2}')
           same_nbt = NBT.parse(str(nbt))

        :param string: the string of a compound in SNBT-format
        :type string: str
        :return: the parsed compound
        :rtype: NbtCompound
        """
        from ._parser_wrapper import parse_compound

        return parse_compound(string)

    def asComponentData(self) -> ComponentData:
        """Convert `self` of type :class:`NbtCompound` to :class:`ComponentData`.
        Note, keys must not contain characters that would have to be quoted.
        """
        return ComponentData(self)

    def deepcopy(self) -> NbtCompound:
        import copy

        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, value: object) -> bool:
        if id(self) == id(value):
            return True
        if type(self) is not type(value):
            if isinstance(value, (dict, UserDict)):
                try:
                    value = self.__class__(value)
                except Exception:
                    return False
            else:
                return False
        if self.keys() != value.keys():
            return False
        for k, v in self.items():
            o = value[k]
            if isinstance(v, bool) and isinstance(o, NbtByte):
                if (v is True and o != 1) or (v is False and o != 0):
                    break
            elif isinstance(v, NbtByte) and isinstance(o, bool):
                if (v != 1 and o is True) or (v != 0 and o is False):
                    break
            elif type(v) is not type(o):
                break
            else:
                if v != o:
                    break
        else:
            return True
        return False

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

    def get_or_create_nbt(self, key: str) -> NbtCompound:
        """Get an existing or create a :class:`NbtCompound` at key `key`.
        Equivalent to ``self[key]`` if key is a :class:`NbtCompound`, otherwise overwrite with new compound and return it.

        :param key: key to get or create compound at
        :type key: str
        :return: existing compound if key had one else new (overwritten) compound
        :rtype: NbtCompound
        """
        if key not in self or not isinstance(self[key], NbtCompound):
            self[key] = NbtCompound()
        return self[key]

    def get_or_create_list(self, key: str) -> NbtList:
        """Get an existing or create a :class:`NbtList` at key `key`.
        Equivalent to ``self[key]`` if key is a :class:`NbtList`, otherwise overwrite with new list and return it.

        :param key: key to get or create list at
        :type key: str
        :return: existing list if key had one else new (overwritten) list
        :rtype: NbtList
        """
        if key not in self or not isinstance(self[key], NbtList):
            self[key] = NbtList()
        return self[key]

    @property
    def bool(self) -> TypedCompoundView[bool]:
        return TypedCompoundView(self, bool)

    @property
    def byte(self) -> TypedCompoundView[NbtByte]:
        return TypedCompoundView(self, NbtByte)

    @property
    def short(self) -> TypedCompoundView[NbtShort]:
        return TypedCompoundView(self, NbtShort)

    @property
    def int(self) -> TypedCompoundView[NbtInt]:
        return TypedCompoundView(self, NbtInt)

    @property
    def long(self) -> TypedCompoundView[NbtLong]:
        return TypedCompoundView(self, NbtLong)

    @property
    def float(self) -> TypedCompoundView[NbtFloat]:
        return TypedCompoundView(self, NbtFloat)

    @property
    def double(self) -> TypedCompoundView[NbtDouble]:
        return TypedCompoundView(self, NbtDouble)

    @property
    def string(self) -> TypedCompoundView[str]:
        return TypedCompoundView(self, str)

    @property
    def list(self) -> TypedCompoundView[NbtList]:
        return TypedCompoundView(self, NbtList)

    @property
    def compound(self) -> TypedCompoundView[NbtCompound]:
        return TypedCompoundView(self, NbtCompound)

    @property
    def byte_array(self) -> TypedCompoundView[NbtByteArray]:
        return TypedCompoundView(self, NbtByteArray)

    @property
    def int_array(self) -> TypedCompoundView[NbtIntArray]:
        return TypedCompoundView(self, NbtIntArray)

    @property
    def long_array(self) -> TypedCompoundView[NbtLongArray]:
        return TypedCompoundView(self, NbtLongArray)


class ComponentData(NbtCompound):
    """:class:`ComponentData` subclasses and behaves exactly like :class:`NBT` with the only difference being its string representation:
    Instead of ``{key1:value1,key2:value2}`` it is represented as ``[key1=value1,key2=value2]``, allowing it to represent the component-format_ on item, item stacks and block entities.
    Additionally, the keys of :class:`ComponentData` may not contain characters that have to be quoted in NBT format and must be strings.

    Checkout :class:`Block` for an explanation and example on how to parse and write component data directly.

    .. _component-format: https://minecraft.wiki/w/Data_component_format
    """

    KEYVALSEP = "="

    @classmethod
    def parse(cls, string: str) -> ComponentData:
        """Parse `string` of a component-data block to :class:`ComponentData`."""
        from ._parser_wrapper import parse_component

        return parse_component(string)

    def asComponentData(self):
        return self

    def asCompound(self) -> NbtCompound:
        """Convert `self` of type :class:`ComponentData` to :class:`NbtCompound`"""
        return NbtCompound(self)

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
        from ._parser_wrapper import try_parse_number

        nbt_number = try_parse_number(value)
        if nbt_number is not None:
            value = nbt_number
        # don't parse other compound types/str here, prob. not wanted implicitly
    elif isinstance(value, dict):
        value = NbtCompound(value)
    elif isinstance(value, list):
        value = NbtList(value)
    else:
        raise ValueError(
            f"{value} of type '{type(value).__name__}' cannot automatically be converted to nbt type"
        )
    return value


NbtNumberType: TypeAlias = bool | NbtByte | NbtShort | NbtInt | NbtLong | NbtFloat | NbtDouble

NbtType: TypeAlias = (
    NbtNumberType | str | NbtList | NbtCompound | NbtByteArray | NbtIntArray | NbtLongArray
)
