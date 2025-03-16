import importlib.metadata as _metalib

try:
    __version__ = _metalib.version(__package__ or __name__)
except _metalib.PackageNotFoundError:
    __version__ = "0.0.0"


from . import colors, text
from .constants import *  # All Constants
from .entity import Entity
from .events import *  # All Events
from .exception import *  # All Exceptions
from .minecraft import Minecraft
from .nbt import NBT, Block, parse_component, parse_snbt
from .player import Player
from .vec3 import Vec3
from .world import World

__all__ = ["Minecraft", "Vec3", "NBT", "Block"]
