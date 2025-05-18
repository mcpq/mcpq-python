import pytest

from mcpq.nbt import (
    Block,
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
    parse_snbt,
)


def test_block():
    block = Block("namespace:type[componentkey1=componentvalue1]")
    block = Block("acacia_stairs[facing=east]")
    assert str(block) == "acacia_stairs[facing=east]"

    # block comparison and ordering is always done on the id:
    bs = [
        Block("minecraft:stone"),
        Block("other:block_name"),
        Block("acacia_stairs"),
        Block("another:type"),
    ]
    assert sorted(bs) == [
        Block("another:type"),
        Block("acacia_stairs"),
        Block("minecraft:stone"),
        Block("other:block_name"),
    ]
    block = Block("acacia_stairs[facing=east]")
    assert block == "acacia_stairs" and block == "minecraft:acacia_stairs"
    assert not block.equals("acacia_stairs")
    assert not block.equals("acacia_stairs[half=top,facing=east]")
    assert block.equals("acacia_stairs[facing=east]")

    assert block.getData()
    assert block.getData() == {"facing": "east"}

    b = Block("acacia_stairs[waterlogged=true]")
    sb = Block("oak_sign")
    assert b.withId("oak_sign") == "oak_sign[waterlogged=true]"
    assert b.withId("oak_sign").equals("oak_sign[waterlogged=true]")
    assert b.withId(sb) == "oak_sign[waterlogged=true]"
    assert b.withId(sb).equals("oak_sign[waterlogged=true]")

    b = Block("acacia_stairs[facing=east]")
    wb = Block("other_block[waterlogged=true]")
    assert b.withData({"waterlogged": True}) == "acacia_stairs[waterlogged=true]"
    assert b.withData({"waterlogged": True}).equals("acacia_stairs[waterlogged=true]")
    assert b.withData("[waterlogged=true]") == "acacia_stairs[waterlogged=true]"
    assert b.withData("[waterlogged=true]").equals("acacia_stairs[waterlogged=true]")
    assert b.withData(wb) == "acacia_stairs[waterlogged=true]"
    assert b.withData(wb).equals("acacia_stairs[waterlogged=true]")
    assert b.withData(wb.getData()) == "acacia_stairs[waterlogged=true]"
    assert b.withData(wb.getData()).equals("acacia_stairs[waterlogged=true]")
    assert b.withData() == "acacia_stairs"
    assert b.withData().equals("acacia_stairs")
    assert b.withData() != "acacia_stairs[]"
    assert b.withData().equals("acacia_stairs[]")

    b = Block("acacia_stairs[facing=east,half=top]")
    wb = Block("other_block[waterlogged=true,half=bottom]")
    assert b.withMergeData({"waterlogged": True, "half": "bottom"}).equals(
        "acacia_stairs[facing=east,half=bottom,waterlogged=true]"
    )
    assert (
        b.withMergeData({"waterlogged": True, "half": "bottom"})
        == 'acacia_stairs[facing="east",half="bottom",waterlogged=true]'
    )
    assert b.withMergeData("[waterlogged=true,half=bottom]").equals(
        "acacia_stairs[facing=east,half=bottom,waterlogged=true]"
    )
    assert (
        b.withMergeData("[waterlogged=true,half=bottom]")
        == 'acacia_stairs[facing="east",half="bottom",waterlogged=true]'
    )
    assert b.withMergeData(wb).equals("acacia_stairs[facing=east,half=bottom,waterlogged=true]")
    assert b.withMergeData(wb) == 'acacia_stairs[facing="east",half="bottom",waterlogged=true]'
    assert b.withMergeData(wb.getData()).equals(
        "acacia_stairs[facing=east,half=bottom,waterlogged=true]"
    )
    assert (
        b.withMergeData(wb.getData())
        == 'acacia_stairs[facing="east",half="bottom",waterlogged=true]'
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

    assert NbtByte(1) == True
    assert NbtByte(0) == False


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

    assert NbtInt(0) == False
    assert NbtInt(1) == True
    for v in [NbtDouble(1), NbtFloat(1), 1, NbtByte(1), NbtShort(1), NbtLong(1)]:
        assert NbtInt(1) == v
    for v in [
        NbtDouble(2),
        NbtFloat(2),
        2,
        NbtByte(2),
        NbtShort(2),
        NbtLong(2),
        False,
        None,
    ]:
        assert NbtInt(1) != v


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
    for v in [
        "-2.213E-18",
        "-2.213e-18",
        "3.4492891728878024E-4",
        ".1",
        "1.",
        "123E23",
        ".1E23",
        "1.E23",
        "1.1E+23",
        "1",
    ]:
        assert NbtFloat(f"{v}f") == float(v)
        assert type(parse_snbt(f"{v}f")) is NbtFloat
        assert parse_snbt(f"{v}f") == float(v)
    with pytest.raises(ValueError):
        parse_snbt("1e48f")
    for v in invalids:
        with pytest.raises(ValueError):
            NbtFloat(v)
        with pytest.raises(ValueError):
            NbtFloat(f"{v}f")
        with pytest.raises(ValueError):
            NbtFloat(f"{v}F")

    for v in [NbtDouble(1.4), NbtFloat(1.4), 1.4]:
        assert NbtFloat(1.4) == v
    for v in [NbtDouble(1.45), NbtFloat(1.45), 1.45, True, False, None]:
        assert NbtFloat(1.4) != v


def test_double():
    valids = (
        list(range(-3, 11))
        + list(i + 0.22 for i in range(-3, 11))
        + [3.4 * 10**41, 3.4 * 10**64, -3.4 * 10**41, -3.4 * 10**64]
    )
    # has a limit in theory, but not implemented here
    for v in valids:
        n = NbtDouble(v)
        assert n == v
        assert str(n) == f"{float(v)}"
        assert NbtDouble(f"{v}d") == v
        assert NbtDouble(f"{v}D") == v
    for v in [
        "-2.213E-18",
        "-2.213e-18",
        "3.4492891728878024E-4",
        ".1",
        "1.",
        "123E48",
        ".1E48",
        "1.E48",
        "1.1E+48",
    ]:
        assert NbtDouble(f"{v}d") == float(v)
        assert NbtDouble(f"{v}") == float(v)
        assert type(parse_snbt(v)) is NbtDouble
        assert parse_snbt(v) == float(v)
    assert type(parse_snbt("1d")) is NbtDouble
    assert type(parse_snbt("1")) is not NbtDouble
    for v in ["text"]:
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
    a1 = """Call \'me\' "Ishmael" and use a \\-command"""
    assert a == a1
    r = """\"Call 'me' \\"Ishmael\\" and use a \\\\-command\""""

    def escape_with_double_quotes(normal_string: str):
        escaped = normal_string.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    print("Normal:", a)
    print("Escape:", escape_with_double_quotes(a))
    print("Should:", r)
    assert escape_with_double_quotes(a) == r
    assert escape_with_double_quotes(a1) == r

    loc = "test"
    s[loc] = a
    print("n[loc]:", n[loc])
    print("n:", n)
    assert s[loc] == a
    assert str(n) == f"{{{loc}:{r}}}"
    assert str(parse_snbt(str(n))) == f"{{{loc}:{r}}}"

    n.clear()
    loc = "Strange 'key' without \" or \\\\"
    locr = escape_with_double_quotes(loc)
    n[loc] = "text"
    assert n[loc] == "text"
    assert str(n) == f'{{{locr}:"text"}}'
    assert str(parse_snbt(str(n))) == f'{{{locr}:"text"}}'

    l = NbtList([a, "text", loc])
    assert l[0] == a
    assert l[1] == "text"
    assert l[2] == loc
    assert str(l) == f'[{r},"text",{locr}]'
    assert str(parse_snbt(str(l))) == f'[{r},"text",{locr}]'

    l.clear()
    last = '''"Nice' string"'''
    l.append(last)
    assert l[0] == last
    assert str(l) == f"[{escape_with_double_quotes(last)}]"
    assert str(parse_snbt(str(l))) == f"[{escape_with_double_quotes(last)}]"


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

    n.byte.append(9)
    n.append(12)
    assert str(n) == "[9b,12b]" and len(n) == 2, f"got {n} with len {len(n)}"
    assert all(type(el) is NbtByte for el in n)
    n.clear()
    assert len(n) == 0

    n.string.append(9)
    n.append(12)
    assert str(n) == '["9","12"]' and len(n) == 2, f"got {n} with len {len(n)}"
    assert all(type(el) is str for el in n)
    n.clear()
    assert len(n) == 0

    n.float.append(9)
    n.append(12)
    assert str(n) == "[9.0f,12.0f]" and len(n) == 2, f"got {n} with len {len(n)}"
    assert all(type(el) is NbtFloat for el in n)
    n.clear()
    assert len(n) == 0

    n.int.append(9)
    with pytest.raises(TypeError):
        n.string.append(12)
    with pytest.raises(TypeError):
        n.float.append(12)
    assert len(n) == 1
    n.clear()
    assert len(n) == 0

    n.append(12)
    assert len(n) == 1 and type(n[0]) is NbtInt, f"{n=}, {len(n)=}"
    with pytest.raises(ValueError):
        n.append(2**63 + 2)
    n.clear()
    assert len(n) == 0

    # long array

    n = NbtLongArray()
    assert str(n) == "[L;]"
    assert len(n) == 0
    assert not n

    with pytest.raises(TypeError):
        n.int.append(1)
    with pytest.raises(TypeError):
        n.string.append("1")
    with pytest.raises(TypeError):
        n.float.append(1)
    n.long.append(5)
    n.append(9)
    assert str(n) == "[L;5l,9l]" and len(n) == 2, f"got {n} with len {len(n)}"
    assert all(type(el) is NbtLong for el in n)
    n.clear()
    assert len(n) == 0

    # byte array

    n = NbtByteArray()
    assert str(n) == "[B;]"
    assert len(n) == 0
    assert not n

    with pytest.raises(TypeError):
        n.int.append(1)
    with pytest.raises(TypeError):
        n.string.append("1")
    with pytest.raises(TypeError):
        n.float.append(1)
    n.bool.append(True)
    n.byte.append(9)
    n.append(5)
    assert str(n) == "[B;true,9b,5b]" and len(n) == 3, f"got {n} with len {len(n)}"
    assert all(type(el) in (NbtByte, bool) for el in n)
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
            '{key1:"value1","key 2":2}',
            NbtCompound,
        ),
        (n.compound, {"": ""}, {"": ""}, '{"":""}', NbtCompound),
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
        # TODO: special case, using [0, True, 2] would be converted to wrong types
        (n, ["0b", True, "2b"], ["0b", True, "2b"], "[0b,true,2b]", NbtList),
        # not a problem here as False as first value makes list a byte list
        (n, [False, "1b", "2b"], [False, 1, 2], "[false,1b,2b]", NbtList),
        (n, {}, {}, "{}", NbtCompound),
        (
            n,
            {"key1": "value1", "key 2": 2},
            {"key1": "value1", "key 2": 2},
            '{key1:"value1","key 2":2}',
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
        assert str(n) == f"{{{loc}:{text}}}", f"{index}: {valids[index]}"
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
        with pytest.raises(Exception):  # Lark Error?
            print(index, set)
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

    # test type equality on equal check:
    a = NbtCompound({"waterlogged": True, "distance": [4, 3, 2], "deep": {"hi": 5}})
    for e in [
        a,
        a.asComponentData(),  # should be converted back
        NbtCompound({"waterlogged": True, "distance": [4, 3, 2], "deep": {"hi": 5}}),
        NbtCompound({"waterlogged": True, "distance": NbtList([4, 3, 2]), "deep": {"hi": 5}}),
        NbtCompound({"distance": [4, 3, 2], "deep": {"hi": 5}, "waterlogged": True}),
        NbtCompound({"distance": [4, 3, 2], "deep": {"hi": 5}, "waterlogged": "1b"}),
        {"distance": [4, 3, 2], "deep": {"hi": 5}, "waterlogged": "1b"},
        {"waterlogged": "true", "distance": [4, 3, 2], "deep": {"hi": 5}},
    ]:
        assert a == e, f"{a=} != {e=}"
    for e in [
        NbtCompound({"distance": [4, 3, 2], "deep": {"hi": 5}, "waterlogged": "1"}),
        NbtCompound({"distance": [4, 3, 2], "deep": {"hi": 5}, "waterlogged": 1}),
        NbtCompound({"waterlogged": False, "distance": [4, 3, 2], "deep": {"hi": 5}}),
        NbtCompound({"waterlogged": True, "distance": [4, 3, 2], "deep": {}}),
        NbtCompound({"waterlogged": True, "distance": NbtIntArray([4, 3, 2]), "deep": {"hi": 5}}),
        {"waterlogged": "True", "distance": [4, 3, 2], "deep": {"hi": 5}},
    ]:
        assert a != e, f"{a=} == {e=}"


def test_parsing():
    valids = [
        "{}",
        '{"":{}}',
        '{"": {}}',
        '{"":""}',
        '{"":     ""}',
        "[1,5]",
        '[{},{"":"","text":{}}]',
        '[{},{"":"", "text":{}}]',
        '[{},{"":"",      "text":{}}]',
        "[{},{'':'','text':{}}]",
        '["1b","1l"]',
        "[true,1b,4b,false]",
        "[false,1b,4b,true]",
        "[1b,true,4b,false]",
        "[B;true,1b,4b,false]",
        "[B;false,1b,4b,true]",
        "[B;1b,true,4b,false]",
        "[ku,geh,my]",
        "[[[],[]],[[[]]]]",
        "[ku,geh,'1b']",
        "[ku,'true',le]",
        "[ku,'{}',le]",
        "[ku,'[]',le]",
        "[ku,'1232',le]",
        "-2.213E-18d",
        "3.4492891728878024e-4d",
        '"\\\\"',
        "'\\\\'",
        '"\\\\\'"',
        "'\\\\\"'",
        "'\\\\r'",
        "'\\\\n'",
    ]
    for v in valids:
        print(v)
        parse_snbt(v)

    invalids = [
        '{""={}}',
        '{""=""}',
        '[{},{""="","text"={}}]',
        "[{},{''='','text'={}}]",
        "{{}}",
        "{:}",
        "{",
        "}",
        "{'key': {}}}",
        "{'key': {}",
        "{:{}}",
        '{"key"}',
        '{"key:"}',
        '{"":}',
        '[1,"1"]',
        "[ku,geh,1b]",
        "[ku,true,le]",
        "[ku,{},le]",
        "[ku,[],le]",
        "[ku,1232,le]",
        '["1", 1]',
        '[1b, "1b"]',
        '["1b", 1b]',
        '["]',
        "[\\]",
        "['\\']",
        "['\\']",
        "[,]",
        "[[]",
        "[]]",
        "\\\\",  # must be quoted
        "'\\'",  # must be escaped twice (in python string)
        '"\\"',  # must be escaped twice (in python string)
        # TODO: this should not work, but does?
        # '"\\\'"',
        # "'\\\"'",
        # "'\\r'",
        # "'\\n'",
    ]
    for v in invalids:
        print(v)
        with pytest.raises(Exception):  # lark error here
            parse_snbt(v)

    valids_str = [
        ("[ku,geh,my]", '["ku","geh","my"]'),
        ("{id: 1,hint: 'nice'}", '{id:1,hint:"nice"}'),
        ("{'id':1,\"hint\": 'nice'}", '{id:1,hint:"nice"}'),
    ]
    for v, res in valids_str:
        print(v)
        assert str(parse_snbt(v)) == res
        assert str(parse_snbt(str(parse_snbt(v)))) == res

    compounds = ['{key:1,list:[1,2,3],"hello 1":"nice"}']
    for c in compounds:
        nbt = NbtCompound.parse(c)
        assert nbt
        assert str(NbtCompound.parse(str(nbt))) == str(nbt)
    for c in ["1", "[1,2,3]", '"hi"', "1.4f"]:
        with pytest.raises(TypeError):
            NbtCompound.parse(c)


def test_component_data():
    nbt_str = '{key:1,list:[1,2,3],hello1:"nice"}'
    nbt = NbtCompound.parse(nbt_str)
    component_data = nbt.asComponentData()
    assert isinstance(component_data, ComponentData)
    assert str(component_data) == "[" + nbt_str.replace(":", "=")[1:-1] + "]"
    assert component_data.asCompound() == nbt

    compounds = ['[key=1,list=[1,2,3],hello1="nice"]']
    for c in compounds:
        nbt = ComponentData.parse(c)
        assert nbt
        assert str(ComponentData.parse(str(nbt))) == str(nbt)
    for c in ["1", "[1,2,3]", '"hi"', "1.4f", "{key:1}"]:
        with pytest.raises(TypeError):
            ComponentData.parse(c)


@pytest.mark.skip
def test_parsing_todos():
    invalids = [
        '"\\\'"',
        "'\\\"'",
        "'\\r'",
        "'\\n'",
    ]
    for v in invalids:
        print(v)
        with pytest.raises(Exception):  # lark error here
            parse_snbt(v)


def test_player_data():
    data = """{seenCredits: 0b, DeathTime: 0s, Bukkit.updateLevel: 2, foodTickTimer: 0, recipeBook: {isBlastingFurnaceFilteringCraftable: 0b, isGuiOpen: 0b, toBeDisplayed: ["minecraft:birch_chest_boat", "minecraft:jungle_chest_boat", "minecraft:crafting_table", "minecraft:oak_chest_boat", "minecraft:bamboo_chest_raft", "minecraft:acacia_chest_boat", "minecraft:mangrove_chest_boat", "minecraft:spruce_chest_boat", "minecraft:cherry_chest_boat", "minecraft:dark_oak_chest_boat"], isSmokerGuiOpen: 0b, isBlastingFurnaceGuiOpen: 0b, isFurnaceFilteringCraftable: 0b, isFurnaceGuiOpen: 0b, isFilteringCraftable: 0b, isSmokerFilteringCraftable: 0b, recipes: ["minecraft:birch_chest_boat", "minecraft:jungle_chest_boat", "minecraft:crafting_table", "minecraft:oak_chest_boat", "minecraft:bamboo_chest_raft", "minecraft:acacia_chest_boat", "minecraft:mangrove_chest_boat", "minecraft:spruce_chest_boat", "minecraft:cherry_chest_boat", "minecraft:dark_oak_chest_boat"]}, XpTotal: 0, OnGround: 0b, AbsorptionAmount: 0.0f, playerGameType: 1, Attributes: [{Name: "minecraft:generic.max_health", Base: 20.0d}, {Name: "minecraft:generic.movement_speed", Base: 0.10000000149011612d}], Invulnerable: 0b, SelectedItemSlot: 0, Brain: {memories: {}}, bukkit: {newTotalExp: 0, newLevel: 0, newExp: 0, keepLevel: 0b, lastPlayed: 1742115166782L, firstPlayed: 1727295819566L, expToDrop: 0, lastKnownName: "Tester"}, Dimension: "minecraft:overworld", Paper.Origin: [-1.5d, 96.0d, -3.5d], abilities: {walkSpeed: 0.1f, flySpeed: 0.05f, instabuild: 1b, flying: 1b, mayfly: 1b, invulnerable: 1b, mayBuild: 1b}, Score: 0, Rotation: [88.80469f, 20.399933f], HurtByTimestamp: 0, foodSaturationLevel: 5.0f, WorldUUIDMost: -324847824704549623L, SelectedItem: {id: "minecraft:acacia_boat", tag: {asd: 2}, Count: 1b}, Paper.OriginWorld: [I; -75634529, -496153335, -1855661986, -2106814127], Paper: {LastLogin: 1742110050816L, LastSeen: 1742115166782L}, EnderItems: [], foodLevel: 20, Air: 300s, XpSeed: -776347013, XpLevel: 0, Motion: [3.4492891728878024E-4d, 0.0d, -2.213E-18d], UUID: [I; -1406999311, -101697727, -1525262829, 331660734], Spigot.ticksLived: 345851, Inventory: [{Slot: 0b, id: "minecraft:acacia_boat", tag: {asd: 2}, Count: 1b}, {Slot: 1b, id: "minecraft:acacia_boat", tag: {asd: "\\' "}, Count: 1b}, {Slot: 2b, id: "minecraft:acacia_boat", tag: {asd: "\\n "}, Count: 1b}], WorldUUIDLeast: -7970007540112256687L, FallDistance: 0.0f, DataVersion: 3465, SleepTimer: 0s, XpP: 0.0f, warden_spawn_tracker: {ticks_since_last_warning: 9823, warning_level: 0, cooldown_ticks: 0}, previousPlayerGameType: 0, Pos: [129.2085770903654d, 81.24618693923294d, -100.51093785797983d], Health: 20.0f, HurtTime: 0s, FallFlying: 0b, Fire: -20s, PortalCooldown: 0, foodExhaustionLevel: 0.0f, Paper.SpawnReason: "DEFAULT"}"""
    nbt = NbtCompound.parse(data)
    assert nbt["seenCredits"] == 0
    assert nbt["bukkit"]["lastKnownName"] == "Tester"
