from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterator

from ._base import _HasServer
from ._proto import minecraft_pb2 as pb
from .exception import raise_on_error
from .nbt import Block


@dataclass(order=True, frozen=True)
class _MaterialInternal:
    key: Block
    is_air: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_block: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_burnable: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_edible: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_flammable: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_fuel: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_interactable: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_item: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_occluding: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    is_solid: bool = field(repr=False, hash=False, compare=False, kw_only=True)
    has_gravity: bool = field(repr=False, hash=False, compare=False, kw_only=True)

    def __str__(self) -> str:
        return self.key

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def _build(cls, buffer: pb.Material) -> _MaterialInternal:
        return cls(
            Block(buffer.key.removeprefix("minecraft:")),
            is_air=buffer.isAir,
            is_block=buffer.isBlock,
            is_burnable=buffer.isBurnable,
            is_edible=buffer.isEdible,
            is_flammable=buffer.isFlammable,
            is_fuel=buffer.isFuel,
            is_interactable=buffer.isInteractable,
            is_item=buffer.isItem,
            is_occluding=buffer.isOccluding,
            is_solid=buffer.isSolid,
            has_gravity=buffer.hasGravity,
        )


class MaterialFilter(_HasServer, Sequence):
    """
    The :class:`MaterialFilter` filteres materials, which includes types of blocks, items and other materials, by querying the server.
    The exact materials that are available depend on the Minecraft version and plugins/mods that are installed on the :class:`Minecraft` instance.

    Typically, we would like to get a certain subtype of material, which can be filtered directly on this class. Once we have done this, we can iterate over it, return a list of applied filters or choose a random block from the filtered materials:

    .. code::

       from mcpq import Minecraft
       mc = Minecraft()

       # get all blocks that contain the word "wool"
       wool = mc.materials.block().contains("wool")
       # equivalent to:
       wool = mc.blocks.contains("wool")

       print(wool.first())
       # >>> 'black_wool'
       print(wool.len())
       # >>> 16
       print(wool.get())
       # >>> ['black_wool', 'blue_wool', 'brown_wool', ...]

       # get all non-solid blocks
       solids = mc.materials.block().solid(False)
       # get all items
       items = mc.materials.item()

       # once you have your filtered materials you can iterate over them:
       for block in mc.blocks.contains("wool"):
          mc.postToChat(block)
       # or select randomly
       random_wool = mc.blocks.contains("wool").choice()
       # or turn the filter into a list for something else
       wool_list = mc.blocks.contains("wool").get()

    Most filteres can be inverted, either directly, e.g., ``mc.materials.item(False)`` to get all non-item materials, or by using the inverted keyword for string filters, e.g., ``mc.materials.contains("yellow", "orange", negate=True)`` to get all materials that do not contain the words yellow or orange.

    Additionally, filters can be combined in a number of ways.
    Let's say we want to get all block types that contain the words "wool" or "concrete" but NOT the word "yellow". There are multiple ways how we could filter the material list:

    .. code::

       from mcpq import Minecraft
       mc = Minecraft()

       # method chaining
       mc.materials.block().contains("wool", "concrete").contains("yellow", negate=True)
       # method chaining with or_ (or_ binds strongly, i.e., only the two contains calls are or-ed)
       mc.materials.block().contains("wool").or_.contains("concrete").contains("yellow", negate=True)
       # binary operators (short form)
       (mc.materials.contains("wool", "concrete") & ~mc.materials.contains("yellow")).block()
       # binary operators (explicit form)
       wool_concrete = mc.materials.block().contains("wool") | mc.materials.block().contains("concrete")
       wool_concrete & ~mc.materials.contains("yellow")

    Plus there are many more filters:

    .. code::

       # get exactly the block called "red_wool"
       red_wool_block = mc.materials.getById("red_wool")
       # get exactly the blocks "red_wool" and "green_wool"
       red_green = mc.materials.equals("red_wool", "green_wool")
       # number of "cut_copper" blocks (does NOT include, e.g., "cut_copper_stairs")
       number_of_cut_copper = mc.materials.block().endswith("cut_copper").len()
       # and many more...
    """

    def __init__(
        self,
        server,
        filters: list[Callable[[_MaterialInternal], bool]],
        next_or: bool = False,
    ):
        super().__init__(server)
        self._filters = filters
        self._filtered_materials: list[Block] | None = None
        self._next_or: bool = next_or

    # logic operations

    def _add_filter(self, func: Callable[[_MaterialInternal], bool]) -> MaterialFilter:
        if self._next_or and self._filters:
            filters = self._filters[:]
            last_filter = filters[-1]
            filters[-1] = lambda m: last_filter(m) or func(m)
            return self.__class__(self._server, filters)
        return self.__class__(self._server, self._filters + [func])

    @property
    def or_(self) -> MaterialFilter:
        """Or the next filter with the previous one (this is strongly binding) thus (potentially) widening the selection of materials.
        ``mc.materials.block().contains("wool").or_.contains("concrete")`` can be read as ``block AND (wool OR concrete)`` thus giving all blocks that contain either "wool" or "concrete" or both.
        """
        return self.__class__(self._server, self._filters, True)

    def __add__(self, other) -> MaterialFilter:
        if isinstance(other, MaterialFilter):
            return self.__class__(
                self._server,
                [
                    lambda m: all(ffunc(m) for ffunc in self._filters)
                    or all(ffunc(m) for ffunc in other._filters)
                ],
            )
        return NotImplemented

    def __and__(self, other) -> MaterialFilter:
        if isinstance(other, MaterialFilter):
            return self.__class__(
                self._server,
                [
                    lambda m: all(ffunc(m) for ffunc in self._filters)
                    and all(ffunc(m) for ffunc in other._filters)
                ],
            )
        return NotImplemented

    def __or__(self, other) -> MaterialFilter:
        if isinstance(other, MaterialFilter):
            return self.__class__(
                self._server,
                [
                    lambda m: all(ffunc(m) for ffunc in self._filters)
                    or all(ffunc(m) for ffunc in other._filters)
                ],
            )
        return NotImplemented

    def __invert__(self) -> MaterialFilter:
        return self.__class__(
            self._server,
            [lambda m: not all(ffunc(m) for ffunc in self._filters)],
        )

    # apply filters

    def _filtered(self) -> list[Block]:
        if self._filtered_materials is None:
            if self._filters:
                self._filtered_materials = [
                    m.key
                    for m in self._server.get_materials(
                        lambda m: all(ffunc(m) for ffunc in self._filters)
                    )
                ]
            else:
                self._filtered_materials = [m.key for m in self._server.get_materials()]
        return self._filtered_materials

    def get(self) -> list[Block]:
        "Apply all filters and return a Python :class:`list` of filtered blocks"
        return self._filtered()[:]  # copy of cached list

    def getById(self, id: str) -> Block:
        """Apply all filters and return the block with `id`.
        If the block does not exist in the current selection raise an error.
        """
        element = self.equals(id).first()
        if element is None:
            raise_on_error(pb.Status(code=pb.BLOCK_TYPE_NOT_FOUND, extra=id))
        return element  # type: ignore

    def first(self) -> Block | None:
        "Apply all filters and return the first element if one exists else None"
        if len(self):
            return self[0]
        return None

    def choice(self) -> Block:
        "Apply all filters and return a random element"
        return random.choice(self)

    def len(self) -> int:
        "Apply all filters and return the number of elements in the selection"
        return len(self)

    # sequence methods

    def __len__(self) -> int:
        return len(self._filtered())

    def __getitem__(self, index) -> Block:
        return self._filtered()[index]

    def __iter__(self) -> Iterator[Block]:
        return iter(self._filtered())

    def __repr__(self):
        return f"{self.__class__.__name__}({self._filtered()!r}, len={len(self)})"

    # material properties

    def air(self, value: bool = True, /) -> MaterialFilter:
        "Filter for air blocks, e.g., like ``air`` and ``void_air``"
        return self._add_filter(lambda m: m.is_air is value)

    def block(self, value: bool = True, /) -> MaterialFilter:
        "Filter for blocks, i.e., anything that can be set using :func:`~mcpq.world.setBlock`"
        return self._add_filter(lambda m: m.is_block is value)

    def burnable(self, value: bool = True, /) -> MaterialFilter:
        "Filter for blocks that can burn away"
        return self._add_filter(lambda m: m.is_burnable is value)

    def edible(self, value: bool = True, /) -> MaterialFilter:
        "Filter for edible materials"
        return self._add_filter(lambda m: m.is_edible is value)

    def flammable(self, value: bool = True, /) -> MaterialFilter:
        "Filter for blocks that can catch fire"
        return self._add_filter(lambda m: m.is_flammable is value)

    def fuel(self, value: bool = True, /) -> MaterialFilter:
        "Filter for materials that can be used as fuel in a furnace"
        return self._add_filter(lambda m: m.is_fuel is value)

    def interactable(self, value: bool = True, /) -> MaterialFilter:
        "Filter for interactable materials. Interactable materials include those with functionality when they are interacted with by a player such as chests, furnaces, etc. It counts as interactable if there is at least one state in which additional interact handling is performed for the material."
        return self._add_filter(lambda m: m.is_interactable is value)

    def item(self, value: bool = True, /) -> MaterialFilter:
        "Filter for obtainable items."
        return self._add_filter(lambda m: m.is_item is value)

    def occluding(self, value: bool = True, /) -> MaterialFilter:
        """Filter for blocks that occlude light. Most full blocks will occlude light while non-full blocks are non-occluding.
        Check the wiki on opacity_.

        .. _opacity: https://minecraft.wiki/w/Opacity
        """
        return self._add_filter(lambda m: m.is_occluding is value)

    def solid(self, value: bool = True, /) -> MaterialFilter:
        "Filter for blocks that are solid, i.e., can be built upon."
        return self._add_filter(lambda m: m.is_solid is value)

    def gravity(self, value: bool = True, /) -> MaterialFilter:
        "Filter for materials that are affected by gravity."
        return self._add_filter(lambda m: m.has_gravity is value)

    # additional infered properties

    def vanilla(self, value: bool = True, /) -> MaterialFilter:
        "Filter for vanilla block, i.e., block with namespace ``minecraft``"
        return self._add_filter(lambda m: (m.key.namespace == "minecraft") is value)

    def namespace(self, *namespaces: str, negate: bool = False) -> MaterialFilter:
        "Filter for any number of namespaces. Providing multiple namespace means any block having any of the given namespaces is considered a match"
        return self._add_filter(lambda m: (m.key.namespace in namespaces) is not negate)

    # additional key filters

    def equals(self, *strings: str, negate: bool = False) -> MaterialFilter:
        "Filter for any number of exact block matches. Providing multiple means any block equaling any of the given strings is considered a match"
        return self._add_filter(lambda m: (m.key in strings) is not negate)

    def contains(self, *substrings: str, negate: bool = False) -> MaterialFilter:
        "Filter for blocks that contain a substring. Providing multiple means any block containing any of the given substrings is considered a match"
        return self._add_filter(
            lambda m: any(sub in m.key.name for sub in substrings) is not negate
        )

    def startswith(self, *substrings: str, negate: bool = False) -> MaterialFilter:
        "Filter for blocks that start with a substring. Providing multiple means any block starting with any of the given substrings is considered a match"
        return self._add_filter(
            lambda m: any(m.key.name.startswith(sub) for sub in substrings) is not negate
        )

    def endswith(self, *substrings: str, negate: bool = False) -> MaterialFilter:
        "Filter for blocks that end with a substring. Providing multiple means any block ending with any of the given substrings is considered a match"
        return self._add_filter(
            lambda m: any(m.key.name.endswith(sub) for sub in substrings) is not negate
        )
