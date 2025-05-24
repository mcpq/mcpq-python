import math
from numbers import Number

import pytest

from mcpq import Vec3


def close(a, b, abs_tol=10**-6) -> bool:
    if isinstance(a, Number) and isinstance(b, Number):
        return math.isclose(a, b, abs_tol=abs_tol)
    return all(math.isclose(i, j, abs_tol=abs_tol) for i, j in zip(a, b, strict=True))


def test_close() -> None:
    assert close(0.000001, 0)
    assert not close(0.001, -0.001)
    assert close(Vec3(), Vec3(0.000001, -0.000001))
    assert not close(Vec3(), Vec3(0.001, -0.001))


def test_eq() -> None:
    # created by dataclass, only sanity checks
    assert Vec3() == Vec3()
    assert Vec3(1, 2, 3) == Vec3(1, 2, 3)
    assert Vec3(1, 2, 3) == Vec3(1.0, 2.0, 3.0)
    assert Vec3(1, 2, 3) != Vec3()
    assert Vec3() != Vec3(1, 2, 3)
    assert Vec3() != 0  # type: ignore
    assert 0 != Vec3()  # type: ignore
    assert Vec3() != 0.0  # type: ignore
    assert 0.0 != Vec3()  # type: ignore
    assert Vec3() != False  # type: ignore
    assert False != Vec3()  # type: ignore
    assert Vec3() != True  # type: ignore
    assert True != Vec3()  # type: ignore
    assert Vec3() != None  # type: ignore
    assert None != Vec3()  # type: ignore
    assert Vec3() != object()


def test_bool() -> None:
    assert bool(Vec3(1, -2, 3)) == True
    assert bool(Vec3()) == True  # better to have any vector be True


def test_init() -> None:
    assert Vec3(0, 0, 0) == Vec3(x=0, y=0, z=0)
    assert Vec3() == Vec3(x=0, y=0, z=0)
    assert Vec3(2.5, 3.5, 4.5)
    assert Vec3(2.5, y=3.5, z=4.5)
    assert Vec3(y=3.5, z=4.5).x == 0
    assert Vec3()


def test_statics() -> None:
    a = 12
    assert Vec3().up() == Vec3(0, 1, 0)
    assert Vec3().down() == Vec3(0, -1, 0)
    assert Vec3().south() == Vec3(0, 0, 1)
    assert Vec3().north() == Vec3(0, 0, -1)
    assert Vec3().east() == Vec3(1, 0, 0)
    assert Vec3().west() == Vec3(-1, 0, 0)
    assert Vec3().east(a) == Vec3(a, 0, 0)
    assert Vec3().up(a) == Vec3(0, a, 0)
    assert Vec3().south(a) == Vec3(0, 0, a)
    assert Vec3().east(-a) == Vec3(-a, 0, 0)
    assert Vec3().up(-a) == Vec3(0, -a, 0)
    assert Vec3().south(-a) == Vec3(0, 0, -a)
    assert Vec3().east(-a) == Vec3().west(a)
    assert Vec3().up(-a) == Vec3().down(a)
    assert Vec3().south(-a) == Vec3().north(a)
    assert Vec3().addX() == Vec3().east()
    assert Vec3().addY() == Vec3().up()
    assert Vec3().addZ() == Vec3().south()
    assert Vec3().addXY() == Vec3().east().up()
    assert Vec3().addXZ() == Vec3().east().south()
    assert Vec3().addYZ() == Vec3().up().south()
    assert Vec3().addX(a) == Vec3().east(a)
    assert Vec3().addY(a) == Vec3().up(a)
    assert Vec3().addZ(a) == Vec3().south(a)
    assert Vec3().addXY(a) == Vec3().east(a).up(a)
    assert Vec3().addXZ(a) == Vec3().east(a).south(a)
    assert Vec3().addYZ(a) == Vec3().up(a).south(a)
    assert Vec3().addX(a) == Vec3(x=a)
    assert Vec3().addX(-a) == Vec3(x=-a)
    assert Vec3().addY(a) == Vec3(y=a)
    assert Vec3().addY(-a) == Vec3(y=-a)
    assert Vec3().addZ(a) == Vec3(z=a)
    assert Vec3().addZ(-a) == Vec3(z=-a)
    assert Vec3().addXY(a) == Vec3(x=a, y=a)
    assert Vec3().addXY(-a) == Vec3(x=-a, y=-a)
    assert Vec3().addXZ(a) == Vec3(x=a, z=a)
    assert Vec3().addXZ(-a) == Vec3(x=-a, z=-a)
    assert Vec3().addYZ(a) == Vec3(y=a, z=a)
    assert Vec3().addYZ(-a) == Vec3(y=-a, z=-a)
    assert Vec3().withX(a) == Vec3(x=a)
    assert Vec3().withX(-a) == Vec3(x=-a)
    assert Vec3().withY(a) == Vec3(y=a)
    assert Vec3().withY(-a) == Vec3(y=-a)
    assert Vec3().withZ(a) == Vec3(z=a)
    assert Vec3().withZ(-a) == Vec3(z=-a)
    assert Vec3().withXY(a) == Vec3(x=a, y=a)
    assert Vec3().withXY(-a) == Vec3(x=-a, y=-a)
    assert Vec3().withXZ(a) == Vec3(x=a, z=a)
    assert Vec3().withXZ(-a) == Vec3(x=-a, z=-a)
    assert Vec3().withYZ(a) == Vec3(y=a, z=a)
    assert Vec3().withYZ(-a) == Vec3(y=-a, z=-a)
    myvec = Vec3(112, -1, -99)
    assert myvec.up() == myvec + Vec3(0, 1, 0)
    assert myvec.down() == myvec + Vec3(0, -1, 0)
    assert myvec.south() == myvec + Vec3(0, 0, 1)
    assert myvec.north() == myvec + Vec3(0, 0, -1)
    assert myvec.east() == myvec + Vec3(1, 0, 0)
    assert myvec.west() == myvec + Vec3(-1, 0, 0)
    assert myvec.east(a) == myvec + Vec3(a, 0, 0)
    assert myvec.up(a) == myvec + Vec3(0, a, 0)
    assert myvec.south(a) == myvec + Vec3(0, 0, a)
    assert myvec.east(-a) == myvec + Vec3(-a, 0, 0)
    assert myvec.up(-a) == myvec + Vec3(0, -a, 0)
    assert myvec.south(-a) == myvec + Vec3(0, 0, -a)
    assert myvec.east(-a) == myvec + Vec3().west(a)
    assert myvec.up(-a) == myvec + Vec3().down(a)
    assert myvec.south(-a) == myvec + Vec3().north(a)
    assert myvec.addX() == myvec.east()
    assert myvec.addY() == myvec.up()
    assert myvec.addZ() == myvec.south()
    assert myvec.addXY() == myvec.east().up()
    assert myvec.addXZ() == myvec.east().south()
    assert myvec.addYZ() == myvec.up().south()
    assert myvec.addX(a) == myvec.east(a)
    assert myvec.addY(a) == myvec.up(a)
    assert myvec.addZ(a) == myvec.south(a)
    assert myvec.addXY(a) == myvec.east(a).up(a)
    assert myvec.addXZ(a) == myvec.east(a).south(a)
    assert myvec.addYZ(a) == myvec.up(a).south(a)
    assert myvec.addX() == myvec + Vec3(1, 0, 0)
    assert myvec.addY() == myvec + Vec3(0, 1, 0)
    assert myvec.addZ() == myvec + Vec3(0, 0, 1)
    assert myvec.addXY() == myvec + Vec3(1, 1, 0)
    assert myvec.addXZ() == myvec + Vec3(1, 0, 1)
    assert myvec.addYZ() == myvec + Vec3(0, 1, 1)
    assert myvec.addX(a) == myvec + Vec3(a, 0, 0)
    assert myvec.addX(-a) == myvec + Vec3(-a, 0, 0)
    assert myvec.addY(a) == myvec + Vec3(0, a, 0)
    assert myvec.addY(-a) == myvec + Vec3(0, -a, 0)
    assert myvec.addZ(a) == myvec + Vec3(0, 0, a)
    assert myvec.addZ(-a) == myvec + Vec3(0, 0, -a)
    assert myvec.addXY(a) == myvec + Vec3(a, a, 0)
    assert myvec.addXY(-a) == myvec + Vec3(-a, -a, 0)
    assert myvec.addXZ(a) == myvec + Vec3(a, 0, a)
    assert myvec.addXZ(-a) == myvec + Vec3(-a, 0, -a)
    assert myvec.addYZ(a) == myvec + Vec3(0, a, a)
    assert myvec.addYZ(-a) == myvec + Vec3(0, -a, -a)
    assert myvec.withX(a) == Vec3(a, myvec.y, myvec.z)
    assert myvec.withY(a) == Vec3(myvec.x, a, myvec.z)
    assert myvec.withZ(a) == Vec3(myvec.x, myvec.y, a)
    assert myvec.withXY(a) == Vec3(a, a, myvec.z)
    assert myvec.withXY(-a) == Vec3(-a, -a, myvec.z)
    assert myvec.withXZ(a) == Vec3(a, myvec.y, a)
    assert myvec.withXZ(-a) == Vec3(-a, myvec.y, -a)
    assert myvec.withYZ(a) == Vec3(myvec.x, a, a)
    assert myvec.withYZ(-a) == Vec3(myvec.x, -a, -a)


def test_func_add() -> None:
    myvec = Vec3(1, -3, 4.6)
    assert myvec.add() == myvec + 1
    assert myvec.add(1) == myvec + 1
    assert myvec.add(14) == myvec + 14
    assert myvec.add(-14) == myvec - 14
    with pytest.raises(TypeError):
        myvec.add(1, 2)
    assert myvec.add(9, 1, -1) == myvec + Vec3(9, 1, -1)
    assert myvec.add(Vec3()) == myvec
    assert myvec.add(myvec) == myvec + myvec
    assert myvec.add(x=4) == myvec.addX(4)
    assert myvec.add(y=-4) == myvec.addY(-4)
    assert myvec.add(z=12) == myvec.addZ(12)
    assert myvec.add(x=-4, y=5) == myvec.addX(-4).addY(5)
    assert myvec.add(x=-4, z=6) == myvec.addX(-4).addZ(6)
    assert myvec.add(y=-4, z=6) == myvec.addY(-4).addZ(6)
    assert myvec.add(x=12, y=-4, z=6) == myvec.addX(12).addY(-4).addZ(6)
    assert myvec.add(z=6, x=12, y=-4) == myvec.addX(12).addY(-4).addZ(6)
    with pytest.raises(TypeError):
        myvec.add(1, y=5)
    with pytest.raises(TypeError):
        myvec.add(1, 2, 3, x=5)


def test_neg() -> None:
    v = Vec3(1, -2, 3)
    assert -v == Vec3(-v.x, -v.y, -v.z)
    assert +(-v) == -v
    assert -(+v) == -v
    assert -(-v) == v
    assert +(+v) == v


def test_abs_length() -> None:
    from math import sqrt

    v = Vec3(1, -2, 3)
    l = sqrt(v.x**2 + v.y**2 + v.z**2)
    assert close(v.length(), l)
    assert close(abs(v), v.length())


def test_distance() -> None:
    v1 = Vec3(1, -2, 3)
    v2 = Vec3(5, 6, 1)
    assert v1.distance(v2) == (v2 - v1).length()
    assert v1.distance(v2) == v2.distance(v1)
    assert close(v1.distance(v2), 9.1651513)


def test_add() -> None:
    a = 5
    v = Vec3(1, 2, 3)
    assert v + a == Vec3(v.x + a, v.y + a, v.z + a)
    assert a + v == Vec3(v.x + a, v.y + a, v.z + a)
    assert v + v == Vec3(v.x + v.x, v.y + v.y, v.z + v.z)
    assert v + (-v) == Vec3()
    with pytest.raises(TypeError):
        assert v + object()  # type: ignore
    with pytest.raises(TypeError):
        assert object() + v  # type: ignore


def test_sub() -> None:
    a = 5
    v = Vec3(1, 2, 3)
    w = Vec3(-12, 133, -4.5)
    assert v - a == Vec3(v.x - a, v.y - a, v.z - a)
    assert a - v == Vec3(v.x - a, v.y - a, v.z - a)
    assert v - v == Vec3(v.x - v.x, v.y - v.y, v.z - v.z)
    assert v - v == Vec3()
    assert v - w != w - v
    assert v - w == -w + v
    assert v - (-v) == v + v
    with pytest.raises(TypeError):
        assert v - object()  # type: ignore
    with pytest.raises(TypeError):
        assert object() - v  # type: ignore


def test_mul() -> None:
    a = 5
    v = Vec3(1, 2, 3)
    k = v + Vec3(4, 2, 0)

    assert v * a == Vec3(v.x * a, v.y * a, v.z * a)
    assert a * v == Vec3(v.x * a, v.y * a, v.z * a)

    assert v ^ v == v.dot(v)
    assert v ^ v == 14
    assert v ^ v == v.x * v.x + v.y * v.y + v.z * v.z
    assert v ^ v > 0
    assert v ^ (-v) < 0
    assert v ^ k == k ^ v == v.dot(k) == k.dot(v) == 22

    assert v * Vec3() == Vec3()
    assert v * Vec3(1, 1, 1) == v
    assert v * k == Vec3(v.x * k.x, v.y * k.y, v.z * k.z)
    assert v * k == v.multiply_elementwise(k)
    assert v.multiply_elementwise(k) == k.multiply_elementwise(v)
    assert v.multiply_elementwise(k) == Vec3(5, 8, 9)

    assert v @ v == v.cross(v)
    assert v @ v == Vec3()
    assert v @ k == v.cross(k)
    assert k @ v == k.cross(v)
    assert v @ k != k.cross(v)
    assert v @ k == -k.cross(v)
    assert v @ k == Vec3(-6, 12, -6)

    with pytest.raises(TypeError):
        assert v ^ object()  # type: ignore
    with pytest.raises(TypeError):
        assert object() ^ v  # type: ignore
    with pytest.raises(TypeError):
        assert v * object()  # type: ignore
    with pytest.raises(TypeError):
        assert object() * v  # type: ignore
    with pytest.raises(TypeError):
        assert v @ object()  # type: ignore
    with pytest.raises(TypeError):
        assert object() @ v  # type: ignore


def test_div() -> None:
    a = 2
    v = Vec3(1, 2, 3)
    assert v / a == Vec3(v.x / a, v.y / a, v.z / a)
    assert v // a == Vec3(v.x // a, v.y // a, v.z // a)
    assert v / a == v * (1.0 / a)
    assert v // a != v * (1.0 // a)
    assert v // a == v.map(lambda w: w // a)
    with pytest.raises(TypeError):
        assert v / object()  # type: ignore
    with pytest.raises(TypeError):
        # does not make sense to implement, use mul
        assert a / v == v * (a / 1.0)  # type: ignore
    with pytest.raises(TypeError):
        # does not make sense
        assert a // v  # type: ignore
    with pytest.raises(ZeroDivisionError):
        assert v / 0
    with pytest.raises(ZeroDivisionError):
        assert v // 0


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_unsupported_casting() -> None:
    v = Vec3(1.4, -2.61, 3.8)
    with pytest.raises(TypeError):
        int(v)  # type: ignore


def test_round() -> None:
    from math import ceil, floor, trunc

    v = Vec3(1.4, -2.61, 3.8)
    assert round(v) == v.round() == Vec3(1, -3, 4)
    assert round(v) == v.round(0) == Vec3(1, -3, 4)
    assert round(v, 0) == v.round() == Vec3(1, -3, 4)
    assert round(v, 0) == v.round(0) == Vec3(1, -3, 4)
    assert floor(v) == v.floor() == Vec3(1, -3, 3)
    assert ceil(v) == v.ceil() == Vec3(2, -2, 4)
    assert trunc(v) == v.trunc() == Vec3(1, -2, 3)

    assert all(isinstance(w, int) for w in v.floor())
    assert all(isinstance(w, int) for w in v.ceil())
    assert all(isinstance(w, int) for w in v.trunc())

    assert round(v, 1) != v
    assert round(v, 2) == v

    assert all(isinstance(w, int) for w in v.round())  # round can guarantee int
    assert all(isinstance(w, int) for w in round(v))  # round can guarantee int

    assert all(isinstance(w, int) for w in v.round(0))  # round can guarantee int
    assert all(isinstance(w, int) for w in round(v, 0))  # round can guarantee int

    assert all(
        isinstance(w, float) for i in range(1, 4) for w in v.round(i)
    )  # requires float ndigits > 0
    assert all(
        isinstance(w, float) for i in range(1, 4) for w in round(v, i)
    )  # requires float ndigits > 0

    # python uses backer's rounding, so not correct for 0.5
    assert v.round() == v.map(lambda w: int(w + 0.5) if w > 0 else int(w - 0.5))


def test_iter() -> None:
    v = Vec3(1, 2, 3)
    assert list(iter(v)) == list(range(1, 4))
    assert list(v) == list(range(1, 4))


def test_len_norm() -> None:
    v = Vec3(1, -2, 3)
    assert close(v.length(), (1 + 4 + 9) ** 0.5)
    assert close(v.norm(), v / v.length())
    assert close(v.norm().length(), 1)


def test_map() -> None:
    import operator

    v = Vec3(1.2, -2.9, 3)
    assert v.map(abs) == v.map(lambda w: w * (1 if w >= 0 else -1))
    f = lambda w: w + 0.5
    assert v.map(f) == Vec3(*list(map(f, v)))
    f = lambda w: (w * 3 + 12.5) % 19
    assert v.map(f) == Vec3(*list(map(f, v)))
    assert v.map(operator.neg) == -v
    w = Vec3(-3, 0, 2)
    assert v.map_pairwise(min, w) == Vec3(-3, -2.9, 2)
    assert v.map_pairwise(max, w) == Vec3(1.2, 0, 3)
    assert v.map_pairwise(lambda e1, e2: e1 if isinstance(e1, int) else e2, w) == Vec3(-3, 0, 3)
    assert v.map_pairwise(operator.add, w) == v + w
    assert v.map_pairwise(operator.mul, w) == v * w
    assert v.map_pairwise(operator.pow, w) == Vec3(v.x**w.x, v.y**w.y, v.z**w.z)


def test_angle() -> None:
    def rad_degree_check(v1, v2, angle):
        assert close(v1.angle_rad(v2), math.radians(angle))
        assert close(v2.angle_rad(v1), math.radians(angle))
        assert close(v1.angle(v2), angle)
        assert close(v2.angle(v1), angle)

    def check_round(v, k, stepsize=5):
        all_close = True
        print(f"{v=} ^ {k=}"), "Rotation will not have rotated angle as equal!"
        assert v.angle(k) == 90
        for i in range(0, 360 + stepsize, stepsize):
            vp = v.rotate(k, i)
            angle = v.angle(vp)
            ip = i if i <= 180 else 360 - i
            single_close = close(ip, angle)
            # print(f"{single_close=}: {ip=} {angle=}")
            rad_degree_check(v, vp, ip)
            all_close = all_close and single_close
        return all_close

    # nice angle checks including zero
    assert check_round(Vec3(1, 0, 0), Vec3(0, 1, 0))
    assert check_round(Vec3(1, 0, 0), Vec3(0, 0, 1))
    assert check_round(Vec3(0, 1.5, 0), Vec3(3.66, 0, 0))
    assert check_round(Vec3(0, 1.5, 0), Vec3(0, 0, 4.5))
    assert check_round(Vec3(0, 0, 0.33), Vec3(3.66, 0, 0))
    assert check_round(Vec3(0, 0, 0.33), Vec3(0, 2.2, 0))

    # some basic checks in addition
    rad_degree_check(Vec3().east(), Vec3().up(), 90)
    rad_degree_check(Vec3().east(), Vec3().south(), 90)
    rad_degree_check(Vec3().east(), Vec3().north(), 90)
    rad_degree_check(Vec3().east(), Vec3().down(), 90)

    rad_degree_check(Vec3().west().down(), Vec3().west().up(), 90)
    rad_degree_check(Vec3().west().down(), Vec3().east().down(), 90)
    rad_degree_check(Vec3().east().up(), Vec3().up(), 45)
    rad_degree_check(Vec3().east().up(), Vec3().east(), 45)
    rad_degree_check(Vec3().east(), Vec3().west(), 180)
    rad_degree_check(Vec3().up(), Vec3().down(), 180)
    rad_degree_check(Vec3().south(), Vec3().north(), 180)
    rad_degree_check(Vec3().east().up().south(), Vec3().west().down().north(), 180)

    # this test results in float point inprecision and fails if not rounding in angle()
    rad_degree_check(Vec3().east().up(), Vec3().east().up(), 0)
    rad_degree_check(Vec3().east(12), Vec3().east(5), 0)
    assert Vec3().east(12).up().angle(Vec3().east(5).up()) > 0

    # some selected angles
    rad_degree_check(Vec3(1, 4, 2), Vec3(-2, -3, 6), 93.57459392151869900815884594557451387)
    rad_degree_check(
        Vec3(1, -19, 2), Vec3(-3, -3, 6), 62.00019487102253092366620570713150837736351
    )
    # TODO: calc higher prec
    # rad_degree_check(Vec3(1, -1, 1.1), Vec3(1, -1, 1), 2.86357)
    # rad_degree_check(Vec3(1, -1.4, 1.3), Vec3(1.02, -1, 1.224), 8.56129)

    # zero divisions
    with pytest.raises(ZeroDivisionError):
        rad_degree_check(Vec3().east().up(), Vec3(), 0)
    with pytest.raises(ZeroDivisionError):
        rad_degree_check(Vec3(), Vec3(), 0)


def test_rotate() -> None:
    from math import radians

    v = Vec3(1, 2, 3)
    k = Vec3().up()
    w90 = radians(90)
    w180 = radians(180)
    w270 = radians(270)
    w360 = radians(360)
    assert 4 * w90 == w360
    assert 3 * w90 == w270
    assert 2 * w90 == w180
    assert 2 * w180 == w360
    assert close(Vec3(3, 2, -1), v.rotate_rad(k, w90))
    assert close(Vec3(-1, 2, -3), v.rotate_rad(k, w180))
    assert close(Vec3(-3, 2, 1), v.rotate_rad(k, w270))

    def all_tests() -> None:
        assert close(v, v.rotate_rad(k, w360))
        assert close(v.rotate_rad(k, w90), v.rotate_rad(k, -w270))
        assert close(v.rotate_rad(k, w90).rotate_rad(k, w90), v.rotate_rad(k, w180))
        assert close(v.rotate_rad(k, w180).rotate_rad(k, w90), v.rotate_rad(k, -w90))
        assert close(v, v.rotate_rad(k, -w360))
        assert close(v.rotate_rad(k, w270), v.rotate_rad(-k, w90))
        assert close(v.rotate_rad(k, w180), v.rotate_rad(-k, w180))
        assert close(v.rotate_rad(k, w90), v.rotate_rad(-k, w270))
        for i in range(360):
            assert v.rotate(k, i) == v.rotate_rad(k, radians(i))

    all_tests()
    k = Vec3().north(5.5)
    assert close(Vec3(2, -1, 3), v.rotate_rad(k, w90))
    assert close(Vec3(-1, -2, 3), v.rotate_rad(k, w180))
    assert close(Vec3(-2, 1, 3), v.rotate_rad(k, w270))
    all_tests()
    k = Vec3().west(-2)
    assert close(Vec3(1, -3, 2), v.rotate_rad(k, w90))
    assert close(Vec3(1, -2, -3), v.rotate_rad(k, w180))
    assert close(Vec3(1, 3, -2), v.rotate_rad(k, w270))
    all_tests()


def test_order() -> None:
    v1 = Vec3(0, 0, 0)
    v2 = Vec3(1, 2, 3)
    v3 = Vec3(3, 2, 1)
    assert sorted([v3, v1, v2]) == [v1, v2, v3]


def test_frozen() -> None:
    from dataclasses import FrozenInstanceError

    v = Vec3(1, 2, 3)
    with pytest.raises(FrozenInstanceError):
        v.x = 5  # type: ignore
    with pytest.raises(FrozenInstanceError):
        v.y = 5  # type: ignore
    with pytest.raises(FrozenInstanceError):
        v.z = 5  # type: ignore
    with pytest.raises(FrozenInstanceError):
        v.x += 5  # type: ignore
    with pytest.raises(FrozenInstanceError):
        v.y += 5  # type: ignore
    with pytest.raises(FrozenInstanceError):
        v.z += 5  # type: ignore


def test_asdict() -> None:
    v = Vec3(1, 2, 3)
    assert v.asdict() == {"x": 1, "y": 2, "z": 3}


def test_pickle() -> None:
    import pickle

    def assert_load_eq_dump(v: Vec3) -> None:
        assert pickle.loads(pickle.dumps(v)) == v

    assert_load_eq_dump(Vec3())
    assert_load_eq_dump(Vec3(z=1 / 3))
    assert_load_eq_dump(Vec3(-123456, -22, 123.6))


def test_copy() -> None:
    import copy

    v = Vec3(0, -22, 123.6)
    cp = copy.copy(v)
    dc = copy.deepcopy(v)
    assert v == cp == dc
    assert v is cp  # due to immutable
    assert v is dc  # due to immutable

    class NewTestVec(Vec3):
        pass

    nv = NewTestVec(0, -22, 123.6)
    cp = copy.copy(nv)
    dc = copy.deepcopy(nv)
    assert nv == cp == dc
    assert isinstance(cp, NewTestVec)
    assert isinstance(dc, NewTestVec)
    assert v != nv


def test_hash() -> None:
    assert hash(Vec3(0, -22, 123.6)) == hash(Vec3(0, -22, 123.6))
    assert hash(Vec3()) == hash(Vec3())
    assert hash(Vec3(0, -22, 123.6)) != hash(Vec3())
    assert hash(Vec3()) != hash(0)
    assert hash(Vec3()) != hash(object())
    assert hash(Vec3()) != hash(0.0)
    assert hash(Vec3()) != hash(False)


def test_pow() -> None:
    v = Vec3(1, -2, 3)
    a = 4
    with pytest.raises(TypeError):
        v**a  # type: ignore
    with pytest.raises(TypeError):
        a**v  # type: ignore
    with pytest.raises(TypeError):
        v**v  # type: ignore
    with pytest.raises(TypeError):
        v**-1  # type: ignore
    with pytest.raises(TypeError):
        v**0  # type: ignore
    with pytest.raises(TypeError):
        v**1  # type: ignore


def test_cloest_axis() -> None:
    assert Vec3().closest_axis() == Vec3()
    assert Vec3(1, 1, 1).closest_axis() == Vec3(x=1)
    assert Vec3(0, 1, 1).closest_axis() == Vec3(y=1)
    assert Vec3(0, -0.5, 1).closest_axis() == Vec3(z=1)
    assert Vec3(33.3, -4.5, 1).closest_axis() == Vec3(x=33.3)
    assert Vec3(3.3, -4.5, 1).closest_axis() == Vec3(y=-4.5)
    assert Vec3(3.3, -4.5, 10).closest_axis() == Vec3(z=10)


def test_direction() -> None:
    EAST, SOUTH, NORTH, WEST, UP, DOWN = "east", "south", "north", "west", "up", "down"
    DEFAULT = EAST
    v = Vec3()
    assert v.cardinal_label() == v.direction_label() == DEFAULT
    v = Vec3(1, 1, 1)
    assert v.cardinal_label() == v.direction_label() == EAST  # default for plus
    v = -Vec3(1, 1, 1)
    assert v.cardinal_label() == v.direction_label() == WEST  # default for minus

    v = Vec3().east()
    assert v.cardinal_label() == v.direction_label() == EAST
    v = Vec3().south()
    assert v.cardinal_label() == v.direction_label() == SOUTH
    v = Vec3().north()
    assert v.cardinal_label() == v.direction_label() == NORTH
    v = Vec3().west()
    assert v.cardinal_label() == v.direction_label() == WEST
    v = Vec3().up()
    assert v.cardinal_label() == DEFAULT
    assert v.direction_label() == UP
    v = Vec3().down()
    assert v.cardinal_label() == DEFAULT
    assert v.direction_label() == DOWN

    a, b = 1.33, 1.31
    v = Vec3().east(a).up(b).south(b)
    assert v.cardinal_label() == v.direction_label() == EAST
    v = Vec3().east(b).up(b).south(a)
    assert v.cardinal_label() == v.direction_label() == SOUTH
    v = Vec3().east(b).up(b).south(-a)
    assert v.cardinal_label() == v.direction_label() == NORTH
    v = Vec3().east(-a).up(b).south(b)
    assert v.cardinal_label() == v.direction_label() == WEST
    v = Vec3().east(b).up(a).south(b)
    assert v.cardinal_label() == DEFAULT
    assert v.direction_label() == UP
    v = Vec3().east(b).up(-a).south(b)
    assert v.cardinal_label() == DEFAULT
    assert v.direction_label() == DOWN


def test_in_cube() -> None:
    p1 = Vec3(-3, 0, -2)
    p2 = Vec3(3, -4, -5)
    assert p1.in_box(p1, p2)
    assert p2.in_box(p1, p2)
    assert not Vec3(0, 0, 0).in_box(p1, p2)
    assert not Vec3(0, 0, 0).in_box(p2, p1)
    assert Vec3(0, 0, -3).in_box(p1, p2)
    assert Vec3(0, 0, -3).in_box(p2, p1)
    assert p1.withX(p2.x).in_box(p1, p2)
    assert p1.withY(p2.y).in_box(p1, p2)
    assert p1.withZ(p2.z).in_box(p1, p2)
    assert p2.withX(p1.x).in_box(p1, p2)
    assert p2.withY(p1.y).in_box(p1, p2)
    assert p2.withZ(p1.z).in_box(p1, p2)
    assert not p1.withX(p2.x + 0.2).in_box(p1, p2)
    assert not p1.withY(p2.y - 0.2).in_box(p1, p2)
    assert not p1.withZ(p2.z - 15).in_box(p1, p2)


def test_vec_alias() -> None:
    from mcpq import Minecraft
    from mcpq._base import _SharedBase

    mc = Minecraft.__new__(Minecraft)  # without calling __init__
    assert mc.Vec3 is Vec3
    assert mc.vec is Vec3
    assert mc.vec(1, 2, 3) == Vec3(1, 2, 3)
    mc.__class__ = _SharedBase  # so _cleanup does not run as it would fail


def test_from_yaw_pitch() -> None:
    # yaw: -180..179.99 (-180 north, -90 east, 0 south, 90 west)
    # pitch -90..90 (-90 up, 0 straight, 90 down)
    assert Vec3.from_yaw_pitch() == Vec3.from_yaw_pitch(0, 0)
    assert close(Vec3.from_yaw_pitch(0, 0), Vec3().south())
    assert close(Vec3.from_yaw_pitch(-90, 0), Vec3().east())
    assert close(Vec3.from_yaw_pitch(-180, 0), Vec3().north())
    assert close(Vec3.from_yaw_pitch(180, 0), Vec3().north())
    assert close(Vec3.from_yaw_pitch(90, 0), Vec3().west())
    assert close(Vec3.from_yaw_pitch(0, -90), Vec3().up())
    assert close(Vec3.from_yaw_pitch(0, 90), Vec3().down())

    assert close(Vec3.from_yaw_pitch(0, 45), Vec3().south().down().norm())
    assert close(Vec3.from_yaw_pitch(-90, 45), Vec3().east().down().norm())
    assert close(Vec3.from_yaw_pitch(-180, 45), Vec3().north().down().norm())
    assert close(Vec3.from_yaw_pitch(180, 45), Vec3().north().down().norm())
    assert close(Vec3.from_yaw_pitch(90, 45), Vec3().west().down().norm())

    assert close(Vec3.from_yaw_pitch(0, -45), Vec3().south().up().norm())
    assert close(Vec3.from_yaw_pitch(-90, -45), Vec3().east().up().norm())
    assert close(Vec3.from_yaw_pitch(-180, -45), Vec3().north().up().norm())
    assert close(Vec3.from_yaw_pitch(180, -45), Vec3().north().up().norm())
    assert close(Vec3.from_yaw_pitch(90, -45), Vec3().west().up().norm())

    assert close(Vec3.from_yaw_pitch(0, -90), Vec3().up())
    assert close(Vec3.from_yaw_pitch(-90, -90), Vec3().up())
    assert close(Vec3.from_yaw_pitch(-180, -90), Vec3().up())
    assert close(Vec3.from_yaw_pitch(180, -90), Vec3().up())
    assert close(Vec3.from_yaw_pitch(90, -90), Vec3().up())

    assert close(Vec3.from_yaw_pitch(0, 90), Vec3().down())
    assert close(Vec3.from_yaw_pitch(-90, 90), Vec3().down())
    assert close(Vec3.from_yaw_pitch(-180, 90), Vec3().down())
    assert close(Vec3.from_yaw_pitch(180, 90), Vec3().down())
    assert close(Vec3.from_yaw_pitch(90, 90), Vec3().down())

    assert close(Vec3.from_yaw_pitch(45, 0), Vec3().south().west().norm())
    assert close(Vec3.from_yaw_pitch(-45, 0), Vec3().south().east().norm())
    assert close(Vec3.from_yaw_pitch(-135, 0), Vec3().north().east().norm())
    assert close(Vec3.from_yaw_pitch(135, 0), Vec3().north().west().norm())


def test_yaw_pitch() -> None:
    # yaw: -180..179.99 (-180 north, -90 east, 0 south, 90 west)
    # pitch -90..90 (-90 up, 0 straight, 90 down)
    def check_pair(a: float | int, b: float | int) -> None:
        yaw, pitch = Vec3.from_yaw_pitch(a, b).yaw_pitch()
        assert close((yaw, pitch), (a, b))
        assert isinstance(yaw, float)
        assert isinstance(pitch, float)

    check_pair(0, 0)
    check_pair(-90, 0)
    check_pair(-180, 0)
    check_pair(179.9, 0)
    check_pair(90, 0)
    check_pair(0, -90)
    check_pair(0, 90)

    check_pair(0, 45)
    check_pair(-90, 45)
    check_pair(-180, 45)
    check_pair(179.9, 45)
    check_pair(90, 45)
    check_pair(45, -90)
    check_pair(45, 90)

    check_pair(0, -45)
    check_pair(-90, -45)
    check_pair(-180, -45)
    check_pair(179.9, -45)
    check_pair(90, -45)
    check_pair(-45, -90)
    check_pair(-45, 90)
    check_pair(135, -90)
    check_pair(-135, -90)
    check_pair(-135, 90)
    check_pair(135, 90)

    for yaw in range(-180, 180, 5):
        for pitch in range(-89, 90, 5):
            # TODO: some bugs at pitch -90 and 90
            check_pair(yaw, pitch)

    assert Vec3().yaw_pitch() == (0, 0)
    assert Vec3().up().yaw_pitch() == (0, -90)
    assert Vec3().down().yaw_pitch() == (0, 90)
    assert Vec3().east().yaw_pitch() == (-90, 0)
    assert Vec3().south().yaw_pitch() == (0, 0)
    assert Vec3().west().yaw_pitch() == (90, 0)
    assert Vec3().north().yaw_pitch() == (-180, 0)
    assert Vec3(100, 0, 100).yaw_pitch() == (-45, 0)
