from __future__ import annotations

import math
from numbers import Number
from typing import Any, Callable, Iterator, Union, final, overload

from ._types import CARDINAL, DIRECTION
from ._util import deprecated

_NumType = Union[int, float]
_NumVec = Union["Vec3", _NumType]

__all__ = ["Vec3"]


@final
class Vec3:
    """:class:`Vec3` is an immutable 3-dimensional vector for representing ``x``, ``y`` and ``z`` coordinates.
    As instances of this class are immutable, calculations yield new instances of :class:`Vec3` instead of changing the x, y and z values directly.

    .. code::

       v = Vec3(1, 4, 8)
       assert v.x == 1 and v.y == 4 and v.z == 8
       # do NOT assign to x, y and z directly, Vec3 is immutable!
       # instead use withX/withY/withZ or addX/east, addY/up and addZ/south or other methods
       assert v.east().south(5) == Vec3(2, 4, 13)
       assert v.addX(-1).withY(0) - Vec3(z=8) == Vec3()  # Vec3() == Vec3(0, 0, 0)
    """

    # class constants
    ZEROS: Vec3  #: Vec3(0, 0, 0)
    ONES: Vec3  #: Vec3(1, 1, 1)
    ORIGIN: Vec3  #: Vec3(0, 0, 0)
    EAST: Vec3  #: Vec3(1, 0, 0)
    WEST: Vec3  #: Vec3(-1, 0, 0)
    UP: Vec3  #: Vec3(0, 1, 0)
    DOWN: Vec3  #: Vec3(0, -1, 0)
    SOUTH: Vec3  #: Vec3(1, 0, 0)
    NORTH: Vec3  #: Vec3(-1, 0, 0)

    __slots__ = ("_x", "_y", "_z")

    def __init__(self, x: _NumType = 0, y: _NumType = 0, z: _NumType = 0):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    def __repr__(self):
        return f"{self.__class__.__name__}(x={self._x}, y={self._y}, z={self._z})"

    def __eq__(self, other):
        return isinstance(other, Vec3) and (self._x, self._y, self._z) == (
            other._x,
            other._y,
            other._z,
        )

    def __hash__(self) -> int:
        return hash((self._x, self._y, self._z))

    def __lt__(self, other: Vec3) -> bool:
        return (self._x, self._y, self._z) < (other._x, other._y, other._z)

    def __le__(self, other: Vec3) -> bool:
        return (self._x, self._y, self._z) <= (other._x, other._y, other._z)

    def __gt__(self, other: Vec3) -> bool:
        return (self._x, self._y, self._z) > (other._x, other._y, other._z)

    def __ge__(self, other: Vec3) -> bool:
        return (self._x, self._y, self._z) >= (other._x, other._y, other._z)

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
        if self._x == 0 and self._y == 0 and self._z == 0:
            return 0.0, 0.0
        yaw = -math.degrees(math.atan2(self._x, self._z))
        pitch = math.degrees(math.atan2(math.sqrt(self._z**2 + self._x**2), self._y)) - 90.0
        return yaw, pitch

    def __add__(self, v: _NumVec) -> Vec3:
        "Vector addition or add scalar to x, y and z"
        if isinstance(v, Number):
            return Vec3(self._x + v, self._y + v, self._z + v)
        if isinstance(v, Vec3):
            return Vec3(self._x + v._x, self._y + v._y, self._z + v._z)
        return NotImplemented

    def __radd__(self, v: _NumVec) -> Vec3:
        return self + v

    def __sub__(self, v: _NumVec) -> Vec3:
        "Vector subtraction or subtract scalar from x, y and z"
        if isinstance(v, Number):
            return Vec3(self._x - v, self._y - v, self._z - v)
        if isinstance(v, Vec3):
            return Vec3(self._x - v._x, self._y - v._y, self._z - v._z)
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
        "Scalar multiplication if v is a number or equivalent to :func:`multiply_elementwise` otherwise"
        if isinstance(v, Number):
            return Vec3(self._x * v, self._y * v, self._z * v)
        if isinstance(v, Vec3):
            return self.multiply_elementwise(v)
        return NotImplemented

    def __rmul__(self, v: _NumVec) -> Vec3:
        return self * v

    def __truediv__(self, v: _NumType) -> Vec3:
        "Equivalent to multiplying `x`, `y` and `z` with 1.0 / `v`"
        if isinstance(v, Number):
            return Vec3(self._x / v, self._y / v, self._z / v)
        return NotImplemented

    def __floordiv__(self, v: _NumType) -> Vec3:
        if isinstance(v, Number):
            return Vec3(self._x // v, self._y // v, self._z // v)
        return NotImplemented

    def __neg__(self) -> Vec3:
        return Vec3(-self._x, -self._y, -self._z)

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
        return self.__class__(self._x, self._y, self._z)

    def __deepcopy__(self, memo: Any) -> Vec3:
        if type(self) is Vec3:
            return self  # immutable
        return self.__class__(self._x, self._y, self._z)

    def __iter__(self) -> Iterator[_NumType]:
        return iter((self._x, self._y, self._z))

    def __abs__(self) -> float:
        "The length/magnitude of vector `self`"
        return math.hypot(self._x, self._y, self._z)

    def distance(self, v: Vec3) -> float:
        "The distance between `self` and another point-vector `v`"
        return (self - v).length()

    def length(self) -> float:
        "The length/magnitude of vector `self`, equivalent to ``abs(self)``"
        return self.__abs__()

    def norm(self) -> Vec3:
        "`self` as a normalized unit-vector with length 1"
        return self / self.length()

    def scale(self, factor: _NumType) -> Vec3:
        "`self` scaled by factor `factor`, equivalent to ``self * factor``"
        return Vec3(self._x * factor, self._y * factor, self._z * factor)

    def with_length(self, length: _NumType) -> Vec3:
        "A vector with the same direction as `self` scaled to length `length`"
        return self.scale(length / self.length())

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
        return self._x * v._x + self._y * v._y + self._z * v._z

    def cross(self, v: Vec3) -> Vec3:
        "The cross product between `self` and `v`, equivalent to ``self @ v``"
        return Vec3(
            self._y * v._z - self._z * v._y,
            self._z * v._x - self._x * v._z,
            self._x * v._y - self._y * v._x,
        )

    def multiply_elementwise(self, v: Vec3) -> Vec3:
        "The element-wise multiplicated vector of `self` and `v`, equivalent to ``self * v``"
        return Vec3(self._x * v._x, self._y * v._y, self._z * v._z)

    def map(self, func: Callable[[_NumType], _NumType]) -> Vec3:
        "A vector with `func` applied to `x`, `y` and `z` of `self` as arguments"
        return Vec3(func(self._x), func(self._y), func(self._z))

    def map_pairwise(self, func: Callable[[_NumType, _NumType], _NumType], v: Vec3) -> Vec3:
        "A vector with `func` applied to each `x`, `y` and `z` of *both* `self` and `v` as arguments"
        return Vec3(func(self._x, v._x), func(self._y, v._y), func(self._z, v._z))

    def map_nwise(self, func: Callable[..., _NumType], *vectors: Vec3) -> Vec3:
        """A vector with `func` applied to each `x`, `y` and `z` of `self` and *all* other `vectors` as arguments"""
        xs = (self._x, *(v._x for v in vectors))
        ys = (self._y, *(v._y for v in vectors))
        zs = (self._z, *(v._z for v in vectors))
        return Vec3(
            func(*xs),
            func(*ys),
            func(*zs),
        )

    def max(self, *vectors: Vec3) -> Vec3:
        "A vector that is the component-wise maximum of `self` and the other `vectors`"
        all_vectors = (self, *vectors)
        return Vec3(
            max(v._x for v in all_vectors),
            max(v._y for v in all_vectors),
            max(v._z for v in all_vectors),
        )

    def min(self, *vectors: Vec3) -> Vec3:
        "A vector that is the component-wise minimum of `self` and the other `vectors`"
        all_vectors = (self, *vectors)
        return Vec3(
            min(v._x for v in all_vectors),
            min(v._y for v in all_vectors),
            min(v._z for v in all_vectors),
        )

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

    @deprecated("asdict is deprected, use to_dict instead")
    def asdict(self) -> dict[str, _NumType]:
        "Deprecated: Use :func:`to_dict` instead"
        return self.to_dict()

    def to_dict(self) -> dict[str, _NumType]:
        "`x`, `y` and `z` in a dictionary"
        return {"x": self._x, "y": self._y, "z": self._z}

    def to_tuple(self) -> tuple[_NumType]:
        "`x`, `y` and `z` in a tuple"
        return (self._x, self._y, self._z)

    def is_close(self, v: Vec3, *, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
        "Whether all components of `self` and `v` are approximately equal"
        return (
            math.isclose(self._x, v._x, rel_tol=rel_tol, abs_tol=abs_tol)
            and math.isclose(self._y, v._y, rel_tol=rel_tol, abs_tol=abs_tol)
            and math.isclose(self._z, v._z, rel_tol=rel_tol, abs_tol=abs_tol)
        )

    def closest_axis(self) -> Vec3:
        "A vector with only the longest (most significant) axis remaining"
        greatest = max(self.map(abs))
        if abs(self._x) == greatest:
            return Vec3(x=self._x)
        elif abs(self._y) == greatest:
            return Vec3(y=self._y)
        elif abs(self._z) == greatest:
            return Vec3(z=self._z)
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

    def clamp(self, min_v: Vec3, max_v: Vec3) -> Vec3:
        "The vector `self` with clamped x, y and z between the corresponding components of `min_val` and `max_val`"
        return Vec3(
            max(min_v._x, min(self._x, max_v._x)),
            max(min_v._y, min(self._y, max_v._y)),
            max(min_v._z, min(self._z, max_v._z)),
        )

    def in_box(self, corner1: Vec3, corner2: Vec3) -> bool:
        "Whether `self` is enclosed in the bounding box/cube spanned between `corner1` and `corner2`, both corners *inclusive*"
        minc, maxc = (
            corner1.map_pairwise(min, corner2),
            corner1.map_pairwise(max, corner2),
        )
        return (
            minc._x <= self._x <= maxc._x
            and minc._y <= self._y <= maxc._y
            and minc._z <= self._z <= maxc._z
        )

    def east(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addX(n)``"
        return Vec3(self._x + n, self._y, self._z)

    def west(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addX(-n)``"
        return Vec3(self._x - n, self._y, self._z)

    def up(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addY(n)``"
        return Vec3(self._x, self._y + n, self._z)

    def down(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addY(-n)``"
        return Vec3(self._x, self._y - n, self._z)

    def south(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addZ(n)``"
        return Vec3(self._x, self._y, self._z + n)

    def north(self, n: _NumType = 1) -> Vec3:
        "Equivalent to ``self.addZ(-n)``"
        return Vec3(self._x, self._y, self._z - n)

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
        self,
        *,
        x: _NumType | None = None,
        y: _NumType | None = None,
        z: _NumType | None = None,
    ) -> Vec3:
        ...

    def add(self, *args: _NumVec, **kwargs: _NumType) -> Vec3:
        """
        `self` with added scalar, another vector, or explicit component-wise values.
        Supports:

        - ``add()`` will add 1 to all components
        - ``add(scalar)`` will add scalar to all components
        - ``add(Vec3(...))`` will do standard vector addition
        - ``add(x, y, z)`` will add the components to their respective component
        - ``add(x=1, y=2, z=3)`` with optional partials (missing parts default to 0)
        """
        if args and kwargs:
            raise TypeError("Cannot use both positional and keyword arguments")

        if kwargs:
            x = kwargs.get("x", 0)
            y = kwargs.get("y", 0)
            z = kwargs.get("z", 0)
            return Vec3(self._x + x, self._y + y, self._z + z)

        if len(args) == 0:
            return self.__add__(1)
        elif len(args) == 1:
            return self.__add__(args[0])
        elif len(args) == 3:
            x, y, z = args
            return Vec3(self._x + x, self._y + y, self._z + z)
        else:
            raise TypeError(f"Expected 0, 1 or 3 arguments to add, got {len(args)}")

    def addX(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `x`, equivalent to ``self + Vec3(n, 0, 0)``"
        return Vec3(self._x + n, self._y, self._z)

    def addY(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `y`, equivalent to ``self + Vec3(0, n, 0)``"
        return Vec3(self._x, self._y + n, self._z)

    def addZ(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `z`, equivalent to ``self + Vec3(0, 0, n)``"
        return Vec3(self._x, self._y, self._z + n)

    def addXY(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `x` and `y`, equivalent to ``self + Vec3(n, n, 0)``"
        return Vec3(self._x + n, self._y + n, self._z)

    def addXZ(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `x` and `z`, equivalent to ``self + Vec3(n, 0, n)``"
        return Vec3(self._x + n, self._y, self._z + n)

    def addYZ(self, n: _NumType = 1) -> Vec3:
        "`self` with `n` added to `y` and `z`, equivalent to ``self + Vec3(0, n, n)``"
        return Vec3(self._x, self._y + n, self._z + n)

    def withX(self, n: _NumType) -> Vec3:
        "`self` with `x` replaced with `n`, equivalent to ``Vec3(n, self.y, self.z)``"
        return Vec3(n, self._y, self._z)

    def withY(self, n: _NumType) -> Vec3:
        "`self` with `y` replaced with `n`, equivalent to ``Vec3(self.x, n, self.z)``"
        return Vec3(self._x, n, self._z)

    def withZ(self, n: _NumType) -> Vec3:
        "`self` with `z` replaced with `n`, equivalent to ``Vec3(self.x, self.y, n)``"
        return Vec3(self._x, self._y, n)

    def withXY(self, n: _NumType) -> Vec3:
        "`self` with `x` and `y` replaced with `n`, equivalent to ``Vec3(n, n, self.z)``"
        return Vec3(n, n, self._z)

    def withXZ(self, n: _NumType) -> Vec3:
        "`self` with `x` and `z` replaced with `n`, equivalent to ``Vec3(n, self.y, n)``"
        return Vec3(n, self._y, n)

    def withYZ(self, n: _NumType) -> Vec3:
        "`self` with `y` and `z` replaced with `n`, equivalent to ``Vec3(self.x, n, n)``"
        return Vec3(self._x, n, n)


# Vec3 Constants
Vec3.ZEROS = Vec3(0, 0, 0)
Vec3.ONES = Vec3(1, 1, 1)
Vec3.ORIGIN = Vec3(0, 0, 0)
Vec3.EAST = Vec3(1, 0, 0)
Vec3.WEST = Vec3(-1, 0, 0)
Vec3.UP = Vec3(0, 1, 0)
Vec3.DOWN = Vec3(0, -1, 0)
Vec3.SOUTH = Vec3(0, 0, 1)
Vec3.NORTH = Vec3(0, 0, -1)

# TODO: clamp, scale?, from_tuple?, normalize?, test for missing and cls.constants

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
    except (FrozenInstanceError, AttributeError):
        is_frozen = True
    print("Using frozen:", is_frozen)

    benchmarks = [
        "Vec3(1, -3, 2)",
        "Vec3(x=1, y=-3, z=2)",
        "Vec3().up() + Vec3().down()",
        "Vec3(1,2,3).cross(Vec3(3,2,1))",
        "Vec3(1,2,3).length()",
    ]
    for bm in benchmarks:
        times = timeit.timeit(bm, globals=globals())
        print(f"{times:.3f}", "->", bm)

    # BENCHMARK DATACLASSES:
    # fastest is frozen=False and slots=True
    # then frozen=False and slots=False
    # then frozen=True and slots=True
    # finally frozen=True and slots=False
    #
    # Using slots: True
    # Using frozen: True
    # 0.251 -> Vec3(1, -3, 2)
    # 0.344 -> Vec3(x=1, y=-3, z=2)
    # 1.697 -> Vec3().up() + Vec3().down()
    # 0.960 -> Vec3(1,2,3).cross(Vec3(3,2,1))

    # BENCHMARK WITHOUT DATACLASS:
    # x, y and z with object.__setattr__ approach (-> same performance as dataclass)
    # 0.252 -> Vec3(1, -3, 2)
    # 0.349 -> Vec3(x=1, y=-3, z=2)
    # 1.648 -> Vec3().up() + Vec3().down()
    # 0.949 -> Vec3(1,2,3).cross(Vec3(3,2,1))

    # BENCHMARK WITHOUT DATACLASS (using _x, _y, _z in slots and internally)
    # 0.119 -> Vec3(1, -3, 2)
    # 0.205 -> Vec3(x=1, y=-3, z=2)
    # 0.927 -> Vec3().up() + Vec3().down()
    # 0.522 -> Vec3(1,2,3).cross(Vec3(3,2,1))
