from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from numbers import Number
from typing import Any, Callable, Iterator, Union, overload

from ._types import CARDINAL, DIRECTION

_NumType = Union[int, float]
_NumVec = Union["Vec3", _NumType]

__all__ = ["Vec3"]


@dataclass(frozen=True, slots=True, eq=True, order=True, repr=True)
class Vec3:
    """:class:`Vec3` is a 3-dimensional vector for representing ``x``, ``y`` and ``z`` coordinates.
    Each instance of this class is **frozen**, so calculations on it yield new instances of :class:`Vec3` instead of changing the x, y and z values directly.
    """

    x: float = 0
    y: float = 0
    z: float = 0

    @classmethod
    def from_yaw_pitch(cls, yaw: _NumType = 0, pitch: _NumType = 0) -> Vec3:
        """Build direction unit-vector from yaw and pitch values.
        This translate the in-Minecraft yaw and pitch values of entities or players (in which direction they are looking) into directional unit-vectors.

        - yaw: -180..179.99 (-180/180 north, -90 east, 0 south, 90 west)

        - pitch: -90..90 (-90 up, 0 straight, 90 down)
        """
        yawed = Vec3().south().rotate(Vec3().down(), yaw)
        pitched = yawed.rotate(yawed.cross(Vec3().down()), pitch)
        return pitched  # .norm()  # already normed

    def yaw_pitch(self) -> tuple[float, float]:
        """The yaw and pitch values from `self` as directional vector.
        This translates directional unit-vectors into in-Minecraft yaw and pitch values used by entities or players (in which direction they are looking).

        - yaw: -180..179.99 (-180 north, -90 east, 0 south, 90 west)

        - pitch: -90..90 (-90 up, 0 straight, 90 down)
        """
        if self.x == 0 and self.y == 0 and self.z == 0:
            return 0.0, 0.0
        yaw = -math.degrees(math.atan2(self.x, self.z))
        pitch = math.degrees(math.atan2(math.sqrt(self.z**2 + self.x**2), self.y)) - 90.0
        return yaw, pitch

    def __add__(self, v: _NumVec) -> Vec3:
        "Vector addition or add scalar to x, y and z"
        if isinstance(v, Number):
            return Vec3(self.x + v, self.y + v, self.z + v)
        if isinstance(v, Vec3):
            return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)
        return NotImplemented

    def __radd__(self, v: _NumVec) -> Vec3:
        return self + v

    def __sub__(self, v: _NumVec) -> Vec3:
        "Vector subtraction or subtract scalar from x, y and z"
        if isinstance(v, Number):
            return Vec3(self.x - v, self.y - v, self.z - v)
        if isinstance(v, Vec3):
            return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)
        return NotImplemented

    def __rsub__(self, v: _NumVec) -> Vec3:
        return self - v

    def __xor__(self, v: Vec3) -> float:
        if isinstance(v, Vec3):
            return self.dot(v)
        return NotImplemented

    def __matmul__(self, v: Vec3) -> Vec3:
        if isinstance(v, Vec3):
            return self.cross(v)
        return NotImplemented

    def __mul__(self, v: _NumVec) -> Vec3:
        "Scalar multiplication or equiavalent to :func:`multiply_elementwise`"
        if isinstance(v, Number):
            return Vec3(self.x * v, self.y * v, self.z * v)
        if isinstance(v, Vec3):
            return self.multiply_elementwise(v)
        return NotImplemented

    def __rmul__(self, v: _NumVec) -> Vec3:
        return self * v

    def __truediv__(self, v: _NumType) -> Vec3:
        "Equivalent to multiplying x, y and z with 1.0 / `v`"
        if isinstance(v, Number):
            return Vec3(self.x / v, self.y / v, self.z / v)
        return NotImplemented

    def __floordiv__(self, v: _NumType) -> Vec3:
        if isinstance(v, Number):
            return Vec3(self.x // v, self.y // v, self.z // v)
        return NotImplemented

    def __neg__(self) -> Vec3:
        return Vec3(-self.x, -self.y, -self.z)

    def __pos__(self) -> Vec3:
        return self  # no change

    def __round__(self, ndigits: int = 0) -> Vec3:
        if ndigits == 0:
            # round returns int if no second parameter is given
            return self.map(round)
        else:
            # returns float otherwise (even if ndigits = 0)
            return self.map(lambda v: round(v, ndigits))

    def __floor__(self) -> Vec3:
        return self.map(math.floor)

    def __ceil__(self) -> Vec3:
        return self.map(math.ceil)

    def __trunc__(self) -> Vec3:
        return self.map(math.trunc)

    def __copy__(self) -> Vec3:
        if type(self) is Vec3:
            return self  # immutable
        return self.__class__(self.x, self.y, self.z)

    def __deepcopy__(self, memo: Any) -> Vec3:
        if type(self) is Vec3:
            return self  # immutable
        return self.__class__(self.x, self.y, self.z)

    def __iter__(self) -> Iterator[_NumType]:
        return iter((self.x, self.y, self.z))

    def __abs__(self) -> float:
        "The (absolute) length of vector `self`"
        return math.hypot(*self)

    def length(self) -> float:
        "The (absolute) length of vector `self`, equivalent to ``abs(self)``"
        return self.__abs__()

    def distance(self, v: Vec3) -> float:
        "The distance between `self` and another point-vector `v`"
        return (self - v).length()

    def angle(self, v: Vec3) -> float:
        "Get the angle between `self` and `v` in degrees (0 <= theta <= 180)"
        return math.degrees(self.angle_rad(v))

    def angle_rad(self, v: Vec3) -> float:
        "Get the angle between `self` and `v` in radians (0 <= theta <= pi)"
        theta = self.norm().dot(v.norm())
        # work against floating point inprecision (e.g. 0.9999999999999998 => 1)
        # in return, this might 'break' extremly tiny rotations
        theta = round(theta, 12)
        return math.acos(max(min(theta, 1), -1))

    def dot(self, v: Vec3) -> float:
        "The dot product between `self` and `v`, equivalent to ``self ^ v``"
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v: Vec3) -> Vec3:
        "The cross product between `self` and `v`, equivalent to ``self @ v``"
        return Vec3(
            self.y * v.z - self.z * v.y,
            self.z * v.x - self.x * v.z,
            self.x * v.y - self.y * v.x,
        )

    def multiply_elementwise(self, v: Vec3) -> Vec3:
        "The element-wise multiplicated vector of `self` and `v`, equivalent to ``self * v``"
        return Vec3(self.x * v.x, self.y * v.y, self.z * v.z)

    def norm(self) -> Vec3:
        "`self` as a normalized unit-vector with length 1"
        return self / self.length()

    def map(self, func: Callable[[_NumType], _NumType]) -> Vec3:
        "A vector with `func` applied to `x`, `y` and `z` of `self` as arguments"
        return Vec3(func(self.x), func(self.y), func(self.z))

    def map_pairwise(self, func: Callable[[_NumType, _NumType], _NumType], v: Vec3) -> Vec3:
        "A vector with `func` applied to each `x`, `y` and `z` of *both* `self` and `v` as arguments"
        return Vec3(func(self.x, v.x), func(self.y, v.y), func(self.z, v.z))

    def rotate(self, v: Vec3, degree: float) -> Vec3:
        "Rotate `self` around vector `v` by `degree` degrees"
        return self.rotate_rad(v, math.radians(degree))

    def rotate_rad(self, v: Vec3, phi: float) -> Vec3:
        "Rotate `self` around vector `v` by `phi` degree radians - Rodrigues rotation"
        v = v.norm()
        return (
            self * math.cos(phi)
            + v.cross(self) * math.sin(phi)
            + v * v.dot(self) * (1.0 - math.cos(phi))
        )

    def round(self, ndigits: int = 0) -> Vec3:
        "Round `x`, `y` and `z` to the `ndigits` comma digit"
        return self.__round__(ndigits)

    def floor(self) -> Vec3:
        "Round `x`, `y` and `z` down to the nearest integer"
        return self.__floor__()

    def ceil(self) -> Vec3:
        "Round `x`, `y` and `z` up to the nearest integer"
        return self.__ceil__()

    def trunc(self) -> Vec3:
        "Leave only the integer part of `x`, `y` and `z`"
        return self.__trunc__()

    def asdict(self) -> dict[str, _NumType]:
        "`x`, `y` and `z` in a dictionary"
        return asdict(self)

    def closest_axis(self) -> Vec3:
        "A vector with only the longest (most significant) axis remaining"
        greatest = max(self.map(abs))
        if abs(self.x) == greatest:
            return Vec3(x=self.x)
        elif abs(self.y) == greatest:
            return Vec3(y=self.y)
        elif abs(self.z) == greatest:
            return Vec3(z=self.z)
        else:
            return Vec3()

    def direction_label(self) -> DIRECTION:
        "The direction of the longest (most significant) axis"
        axis = self.closest_axis()
        if axis.x > 0:
            return "east"
        elif axis.x < 0:
            return "west"
        elif axis.y > 0:
            return "up"
        elif axis.y < 0:
            return "down"
        elif axis.z > 0:
            return "south"
        elif axis.z < 0:
            return "north"
        else:
            return "east"

    def cardinal_label(self) -> CARDINAL:
        "The direction of the longest (most significant) cardinal axis"
        return self.withY(0).direction_label()  # type: ignore

    def in_box(self, corner1: Vec3, corner2: Vec3) -> bool:
        "Whether `self` is enclosed in the bounding box/cube spanned between `corner1` and `corner2`, both corners *inclusive*"
        minc, maxc = corner1.map_pairwise(min, corner2), corner1.map_pairwise(max, corner2)
        return (
            minc.x <= self.x <= maxc.x
            and minc.y <= self.y <= maxc.y
            and minc.z <= self.z <= maxc.z
        )

    def east(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addX(n)``"
        return Vec3(self.x + n, self.y, self.z)

    def west(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addX(-n)``"
        return Vec3(self.x - n, self.y, self.z)

    def up(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addY(n)``"
        return Vec3(self.x, self.y + n, self.z)

    def down(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addY(-n)``"
        return Vec3(self.x, self.y - n, self.z)

    def south(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addZ(n)``"
        return Vec3(self.x, self.y, self.z + n)

    def north(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addZ(-n)``"
        return Vec3(self.x, self.y, self.z - n)

    @overload
    def add(self) -> Vec3:
        ...

    @overload
    def add(self, scalar: _NumType) -> Vec3:
        ...

    @overload
    def add(self, vector: Vec3) -> Vec3:
        ...

    @overload
    def add(self, x: _NumType, y: _NumType, z: _NumType) -> Vec3:
        ...

    @overload
    def add(
        self, *, x: _NumType | None = None, y: _NumType | None = None, z: _NumType | None = None
    ) -> Vec3:
        ...

    def add(self, *args: _NumVec, **kwargs: _NumType) -> Vec3:
        """
        `self` with added scalar, another vector, or explicit component-wise values.
        Supports:
        * add()
        * add(scalar)
        * add(Vec3)
        * add(x, y, z)
        * add(x=1, y=2, z=3) with optional partials (missing parts default to 0)
        """
        if args and kwargs:
            raise TypeError("Cannot use both positional and keyword arguments")

        if kwargs:
            x = kwargs.get("x", 0)
            y = kwargs.get("y", 0)
            z = kwargs.get("z", 0)
            return Vec3(self.x + x, self.y + y, self.z + z)

        if len(args) == 0:
            return self.__add__(1)
        elif len(args) == 1:
            return self.__add__(args[0])
        elif len(args) == 3:
            x, y, z = args
            return Vec3(self.x + x, self.y + y, self.z + z)
        else:
            raise TypeError(f"Expected 0, 1 or 3 arguments to add, got {len(args)}")

    def addX(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `x`, equivalent to ``self + Vec3(n, 0, 0)``"
        return Vec3(self.x + n, self.y, self.z)

    def addY(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `y`, equivalent to ``self + Vec3(0, n, 0)``"
        return Vec3(self.x, self.y + n, self.z)

    def addZ(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `z`, equivalent to ``self + Vec3(0, 0, n)``"
        return Vec3(self.x, self.y, self.z + n)

    def addXY(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `x` and `y`, equivalent to ``self + Vec3(n, n, 0)``"
        return Vec3(self.x + n, self.y + n, self.z)

    def addXZ(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `x` and `z`, equivalent to ``self + Vec3(n, 0, n)``"
        return Vec3(self.x + n, self.y, self.z + n)

    def addYZ(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `y` and `z`, equivalent to ``self + Vec3(0, n, n)``"
        return Vec3(self.x, self.y + n, self.z + n)

    def withX(self, n: _NumType) -> Vec3:
        "`self` with `x` replaced with `n`, equivalent to ``Vec3(n, self.y, self.z)``"
        return Vec3(n, self.y, self.z)

    def withY(self, n: _NumType) -> Vec3:
        "`self` with `y` replaced with `n`, equivalent to ``Vec3(self.x, n, self.z)``"
        return Vec3(self.x, n, self.z)

    def withZ(self, n: _NumType) -> Vec3:
        "`self` with `z` replaced with `n`, equivalent to ``Vec3(self.x, self.y, n)``"
        return Vec3(self.x, self.y, n)

    def withXY(self, n: _NumType) -> Vec3:
        "`self` with `x` and `y` replaced with `n`, equivalent to ``Vec3(n, n, self.z)``"
        return Vec3(n, n, self.z)

    def withXZ(self, n: _NumType) -> Vec3:
        "`self` with `x` and `z` replaced with `n`, equivalent to ``Vec3(n, self.y, n)``"
        return Vec3(n, self.y, n)

    def withYZ(self, n: _NumType) -> Vec3:
        "`self` with `y` and `z` replaced with `n`, equivalent to ``Vec3(self.x, n, n)``"
        return Vec3(self.x, n, n)


if __name__ == "__main__":
    # run some performance benchmarks for dataclass Vec3
    import sys
    import timeit
    from dataclasses import FrozenInstanceError

    print("(Aprox.) Size of a Vec3:", sys.getsizeof(Vec3(1, -333, 98765)))

    print("Using slots:", hasattr(Vec3(), "__slots__"))
    is_frozen = False
    try:
        Vec3().x = 5  # type: ignore
    except FrozenInstanceError:
        is_frozen = True
    print("Using frozen:", is_frozen)

    benchmarks = [
        "Vec3(1, -3, 2)",
        "Vec3(x=1, y=-3, z=2)",
        "Vec3().up() + Vec3().down()",
        "Vec3(1,2,3).cross(Vec3(3,2,1))",
    ]
    for bm in benchmarks:
        times = timeit.timeit(bm, globals=globals())
        print(f"{times:.3f}", "->", bm)

    # fastest is frozen=False and slots=True
    # then frozen=False and slots=False
    # then frozen=True and slots=True
    # finally frozen=True and slots=False
