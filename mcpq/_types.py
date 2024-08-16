from typing import Literal, TypeAlias

__all__ = ["CARDINAL", "DIRECTION", "COLOR"]

CARDINAL: TypeAlias = Literal["east", "south", "west", "north"]
DIRECTION: TypeAlias = Literal[CARDINAL, "up", "down"]

COLOR: TypeAlias = Literal[
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
]
