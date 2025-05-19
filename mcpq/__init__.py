import importlib.metadata as _metalib

try:
    __version__ = _metalib.version(__package__ or __name__)
except _metalib.PackageNotFoundError:
    __version__ = "0.0.0"


from . import colors, text
from .constants import DOWN, EAST, NORD, NORTH, OBEN, OST, SOUTH, SÜD, UNTEN, UP, WEST
from .entity import Entity
from .events import (
    BlockHitEvent,
    ChatEvent,
    Event,
    PlayerDeathEvent,
    PlayerJoinEvent,
    PlayerLeaveEvent,
    ProjectileHitEvent,
)
from .exception import (
    BlockTypeNotFound,
    EntityNotFound,
    EntityNotSpawnable,
    EntityTypeNotFound,
    InvalidArgument,
    MCPQError,
    MissingArgument,
    NotImplementedOrAvailable,
    PlayerNotFound,
    UnknownError,
    WorldNotFound,
)
from .minecraft import Minecraft
from .nbt import NBT, Block, EntityType
from .player import Player
from .vec3 import Vec3
from .world import World

__all__ = [
    # main types
    "Minecraft",
    "Vec3",
    "NBT",
    "Block",
    "EntityType",
    # colors and text effects
    "colors",
    "text",
    # annotation types (for function signatures)
    "World",
    "Player",
    "Entity",
    # events
    "Event",
    "PlayerJoinEvent",
    "PlayerLeaveEvent",
    "PlayerDeathEvent",
    "ChatEvent",
    "BlockHitEvent",
    "ProjectileHitEvent",
    # constants
    "DOWN",
    "EAST",
    "NORTH",
    "SOUTH",
    "UP",
    "WEST",
    # constants (german)
    "OST",
    "SÜD",
    "NORD",
    "OBEN",
    "UNTEN",
    # exceptions
    "MCPQError",
    "UnknownError",
    "MissingArgument",
    "InvalidArgument",
    "NotImplementedOrAvailable",
    "WorldNotFound",
    "PlayerNotFound",
    "BlockTypeNotFound",
    "EntityTypeNotFound",
    "EntityNotSpawnable",
    "EntityNotFound",
]
