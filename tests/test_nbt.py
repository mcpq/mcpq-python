import pytest

from mcpq.nbt import (
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
)


def test_bytes():
    valids = list(range(-3, 11)) + [-(2**5), 2**5, 2**7 - 1, -(2**7)]
    invalids = [2**7, -(2**7 + 1), 2**8, -(2**8), 2**32, -(2**32), "text"]
    for v in valids:
        n = NbtByte(v)
        assert n == v
        assert str(n) == f"{v}b"
        assert NbtByte(f"{v}b") == v
        assert NbtByte(f"{v}B") == v
    for v in invalids:
        with pytest.raises(ValueError):
            NbtByte(v)
        with pytest.raises(ValueError):
            NbtByte(f"{v}b")
        with pytest.raises(ValueError):
            NbtByte(f"{v}B")
    assert NbtByte("0101b", 2) == 5  # not required for real nbt


def test_short():
    valids = list(range(-3, 11)) + [-(2**5), 2**5, 2**15 - 1, -(2**15)]
    invalids = [2**15, -(2**15 + 1), 2**32, -(2**32), 2**64, -(2**64), "text"]
    for v in valids:
        n = NbtShort(v)
        assert n == v
        assert str(n) == f"{v}s"
        assert NbtShort(f"{v}s") == v
        assert NbtShort(f"{v}S") == v
    for v in invalids:
        with pytest.raises(ValueError):
            NbtShort(v)
        with pytest.raises(ValueError):
            NbtShort(f"{v}s")
        with pytest.raises(ValueError):
            NbtShort(f"{v}S")
    assert NbtShort("0101s", 2) == 5  # not required for real nbt


def test_int():
    valids = list(range(-3, 11)) + [-(2**16), 2**16, 2**31 - 1, -(2**31)]
    invalids = [2**31, -(2**31 + 1), 2**64, -(2**64), "text"]
    for v in valids:
        n = NbtInt(v)
        assert n == v
        assert str(n) == f"{v}"
        assert NbtInt(f"{v}") == v
    for v in invalids:
        with pytest.raises(ValueError):
            NbtInt(v)
        with pytest.raises(ValueError):
            NbtInt(f"{v}")
    assert NbtInt("0101", 2) == 5  # not required for real nbt


def test_long():
    valids = list(range(-3, 11)) + [-(2**32), 2**32, 2**63 - 1, -(2**63)]
    invalids = [2**63, -(2**63 + 1), 2**64, -(2**64), "text"]
    for v in valids:
        n = NbtLong(v)
        assert n == v
        assert str(n) == f"{v}l"
        assert NbtLong(f"{v}l") == v
        assert NbtLong(f"{v}L") == v
    for v in invalids:
        with pytest.raises(ValueError):
            NbtLong(v)
        with pytest.raises(ValueError):
            NbtLong(f"{v}l")
        with pytest.raises(ValueError):
            NbtLong(f"{v}L")
    assert NbtLong("0101l", 2) == 5  # not required for real nbt


def test_float():
    import math

    limit = 3.4 * 10**38
    valids = (
        list(range(-3, 11))
        + list(i + 0.22 for i in range(-3, 11))
        + [-limit, math.nextafter(limit, 0)]
    )
    invalids = [-math.nextafter(limit, math.inf), limit, 10**64, -(10**64), "text"]
    for v in valids:
        n = NbtFloat(v)
        assert n == v
        assert str(n) == f"{float(v)}f"
        assert NbtFloat(f"{v}f") == v
        assert NbtFloat(f"{v}F") == v
    for v in invalids:
        with pytest.raises(ValueError):
            NbtFloat(v)
        with pytest.raises(ValueError):
            NbtFloat(f"{v}f")
        with pytest.raises(ValueError):
            NbtFloat(f"{v}F")


def test_double():
    valids = (
        list(range(-3, 11))
        + list(i + 0.22 for i in range(-3, 11))
        + [3.4 * 10**41, 3.4 * 10**64, -3.4 * 10**41, -3.4 * 10**64]
    )
    # has a limit in theory, but not implemented here
    invalids = ["text"]
    for v in valids:
        n = NbtDouble(v)
        assert n == v
        assert str(n) == f"{float(v)}"
        assert NbtDouble(f"{v}d") == v
        assert NbtDouble(f"{v}D") == v
    for v in invalids:
        with pytest.raises(ValueError):
            NbtDouble(v)
        with pytest.raises(ValueError):
            NbtDouble(f"{v}d")
        with pytest.raises(ValueError):
            NbtDouble(f"{v}dF")


def test_string():
    n = NbtCompound()
    s = n.string

    a = "Call 'me' \"Ishmael\" and use a \\-command"
    r = """\"Call 'me' \\"Ishmael\\" and use a \\\\-command\""""

    def escape_with_double_quotes(normal_string: str):
        escaped = normal_string.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    print("Normal:", a)
    print("Escape:", escape_with_double_quotes(a))
    print("Should:", r)
    assert escape_with_double_quotes(a) == r

    loc = "test"
    s[loc] = a
    print("n[loc]:", n[loc])
    print("n:", n)
    assert s[loc] == a
    assert str(n) == f"{{{loc}={r}}}"

    n.clear()
    loc = "Strange 'key' without \" or \\\\"
    locr = escape_with_double_quotes(loc)
    n[loc] = "text"
    assert n[loc] == "text"
    assert str(n) == f'{{{locr}="text"}}'

    l = NbtList([a, "text", loc])
    assert l[0] == a
    assert l[1] == "text"
    assert l[2] == loc
    assert str(l) == f'[{r},"text",{locr}]'

    l.clear()
    last = '''"Nice' string"'''
    l.append(last)
    assert l[0] == last
    assert str(l) == f"[{escape_with_double_quotes(last)}]"


def test_list():
    n = NbtList()
    assert str(n) == "[]"
    assert len(n) == 0
    assert not n

    n.extend([1, 2, 3])
    assert str(n) == "[1,2,3]"
    assert len(n) == 3
    assert n
    assert all(type(el) is NbtInt for el in n)

    n.clear()
    assert len(n) == 0

    for i in range(3):
        n.append(i)
    assert str(n) == "[0,1,2]"
    assert len(n) == 3
    assert all(type(el) is NbtInt for el in n)

    n[0] = 9
    n[1] = 12
    n[2] = -3
    assert str(n) == "[9,12,-3]"
    assert len(n) == 3
    assert all(type(el) is NbtInt for el in n)

    n.clear()
    assert len(n) == 0

    n.insert(0, "text1")
    n.insert(0, "text 2")
    assert str(n) == '["text 2","text1"]'
    assert len(n) == 2
    assert all(type(el) is str for el in n)

    n.clear()
    assert len(n) == 0

    # TODO


def test_compound():
    n = NbtCompound()
    assert str(n) == "{}"
    assert len(n) == 0
    assert not n

    b = NbtCompound.fromkeys(("hi", "nice"), 1)
    assert len(b) == 2
    assert b["hi"] == 1
    assert b["nice"] == 1

    b = NbtCompound({"hi": "test", "wow": {"cool": 2}})
    assert len(b) == 2
    assert b["hi"] == "test"
    assert b["wow"] == {"cool": 2}
    assert type(b["wow"]) is NbtCompound

    b = NbtCompound((("hi", "test"), ("wow", {"cool": 2})))
    assert len(b) == 2
    assert b["hi"] == "test"
    assert b["wow"] == {"cool": 2}
    assert type(b["wow"]) is NbtCompound

    valids = [
        (n.byte, 1, 1, "1b", NbtByte),
        (n.short, 1, 1, "1s", NbtShort),
        (n.int, 1, 1, "1", NbtInt),
        (n.long, 1, 1, "1l", NbtLong),
        (n.float, 1, 1, "1.0f", NbtFloat),
        (n.float, 1.23, 1.23, "1.23f", NbtFloat),
        (n.double, 1, 1, "1.0", NbtDouble),
        (n.double, 1.23, 1.23, "1.23", NbtDouble),
        (n.bool, 1, True, "true", bool),
        (n.bool, 0, False, "false", bool),
        (n.string, "text", "text", '"text"', str),
        (n.string, 1, "1", '"1"', str),
        (n.string, "1b", "1b", '"1b"', str),
        (n.string, {}, "{}", '"{}"', str),
        (n.string, [], "[]", '"[]"', str),
        (n.list, [], [], "[]", NbtList),
        (n.list, [1, 2, 3], [1, 2, 3], "[1,2,3]", NbtList),
        (n.compound, {}, {}, "{}", NbtCompound),
        (
            n.compound,
            {"key1": "value1", "key 2": 2},
            {"key1": "value1", "key 2": 2},
            '{key1="value1","key 2"=2}',
            NbtCompound,
        ),
        (n.byte_array, [1, False, 3], [1, 0, 3], "[B;1b,false,3b]", NbtByteArray),
        (n.int_array, [1, 2, 3], [1, 2, 3], "[I;1,2,3]", NbtIntArray),
        (n.long_array, [1, 2, 3], [1, 2, 3], "[L;1l,2l,3l]", NbtLongArray),
        # defaults
        (n, "1b", 1, "1b", NbtByte),
        (n, True, True, "true", bool),
        (n, False, False, "false", bool),
        (n, "1s", 1, "1s", NbtShort),
        (n, 1, 1, "1", NbtInt),
        (n, "1l", 1, "1l", NbtLong),
        (n, "1.0f", 1, "1.0f", NbtFloat),
        (n, 1.0, 1, "1.0", NbtDouble),
        (n, "1.0d", 1, "1.0", NbtDouble),
        (n, [], [], "[]", NbtList),
        (n, [1, 2, 3], [1, 2, 3], "[1,2,3]", NbtList),
        (n, {}, {}, "{}", NbtCompound),
        (
            n,
            {"key1": "value1", "key 2": 2},
            {"key1": "value1", "key 2": 2},
            '{key1="value1","key 2"=2}',
            NbtCompound,
        ),
        (n, "text", "text", '"text"', str),
        (n, "1.0.0", "1.0.0", '"1.0.0"', str),
        (n, "1f", "1f", '"1f"', str),
        (n, "[]", "[]", '"[]"', str),
        (n, "{}", "{}", '"{}"', str),
        (n, """"'\\-+!""", """"'\\-+!""", '''"\\"'\\\\-+!"''', str),
    ]

    loc = "test"
    for index, (view, set, get, text, t) in enumerate(valids):
        view[loc] = set
        assert n[loc] == get, f"{index}: {valids[index]}"
        assert type(n[loc]) is t, f"{index}: {valids[index]}"
        assert len(n) == 1, f"{index}: {valids[index]}"
        assert str(n) == f"{{{loc}={text}}}", f"{index}: {valids[index]}"
    del n[loc]
    assert not n
    assert len(n) == 0

    invalids = [
        (n.byte, "text"),
        (n.byte, "1s"),
        (n.byte, "1l"),
        (n.short, "text"),
        (n.short, "1b"),
        (n.short, "1l"),
        (n.int, "text"),
        (n.int, "1b"),
        (n.int, "1s"),
        (n.int, "1l"),
        (n.long, "text"),
        (n.long, "1b"),
        (n.long, "1s"),
        (n.float, "text"),
        (n.float, "1.0.0"),
        (n.float, "1.0d"),
        (n.double, "text"),
        (n.double, "1.0.0"),
        (n.double, "1.0f"),
        (n.list, [1, "hi"]),
        # TODO
    ]
    for index, (view, set) in enumerate(invalids):
        with pytest.raises(ValueError):
            view[loc] = set
        assert not n, f"{index}: {valids[index]}"

    invalid_typed = [
        (n.list, 123),  # number not iterable
        # TODO
    ]
    for index, (view, set) in enumerate(invalid_typed):
        with pytest.raises(TypeError):
            view[loc] = set
        assert not n, f"{index}: {invalid_typed[index]}"
