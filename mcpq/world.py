from __future__ import annotations

from functools import partial

from . import entity
from ._base import _EntityProvider, _HasStub
from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from ._types import CARDINAL, COLOR, DIRECTION
from ._util import ThreadSafeSingeltonCache
from .exception import raise_on_error
from .vec3 import Vec3

MAX_BLOCKS = 50000  # TODO: replace with block stream


class _DefaultWorld(_HasStub, _EntityProvider):
    """Manipulating the world is the heart piece of the entire library.
    With this you can query blocks and world features and set them in turn, as well as finding and spawning entities in the world.
    This allows building on the server quickly and precisely with only a few commands.

    .. note::

       When using the world functions on :class:`Minecraft` (``mc``) the 'default' world is used. The default world is defined by the server as the first world loaded by the server, which is usually the overworld.
       If you want to affect a specific world, use :class:`World` classes instead, such as ``mc.overworld``, ``mc.nether`` or ``mc.end``.

    .. code-block:: python

       # affect all worlds
       mc.pvp = False  # disable pvp everywhere (on all worlds)

       # affect only 'default' world (entities and blocks are only collected/set in that world)
       ground_pos = mc.getHeighestPos(0, 0)  # get heighest position on ground (= non-air) at origin
       block = mc.getBlock(ground_pos)  # get the block type there
       mc.setBlock("diamond_block", ground_pos)  # replace that block at location with diamond
       mc.setBlockList("emerald_block", [ground_pos.up(2).east(i) for i in range(0,20,2)])  # set every second block in a line along the x axis to emerald
       mc.setBlockCube("oak_planks", ground_pos.up(50), ground_pos.up(50) + 9)  # set a 10 x 10 x 10 oak plank block 50 blocks above ground
       sheep = mc.spawnEntity("sheep", ground_pos.up(1))  # spawn a sheep on that block
       entities = mc.getEntities()  # get all (loaded) entities
       entities = mc.getEntitiesAround(ground_pos, 20)  # get all  (loaded) entities around origin highest block in 20 block radius
       mc.removeEntities("sheep")  # remove all (loaded) sheep
       blocks = mc.copyBlockCube(Vec3(0,0,0), Vec3(5,5,5))  # copy all blocks between those two points (inclusive)
       mc.pasteBlockCube(blocks, ground_pos.up(20))  # paste back the copied blocks 20 blocks above origin ground
       mc.setBed(ground_pos.up(1))  # place a bed on top of diamond block
    """

    @property
    def _pb_world(self) -> pb.World | None:
        return None

    def __getitem__(
        self,
        pos: tuple[int, int, int] | Vec3,
    ) -> str:
        """Allowed access:
        world[1,2,3] == world[Vec3(1,2,3)] == world[(1,2,3)] for single block access"""
        if isinstance(pos, Vec3):
            return self.getBlock(pos)
        elif isinstance(pos, tuple):
            if len(pos) == 3:
                if all(isinstance(el, int) for el in pos):
                    return self.getBlock(Vec3(*pos))
                # TODO: think about getitem and setitem and possible options again
                else:
                    raise TypeError("Expected tuple with int types")
            else:
                raise TypeError("Expected tuple 3 elements")
        else:
            x, y, z = pos  # attempt to unpack
            return self.getBlock(Vec3(x, y, z))
            # raise TypeError("Expected tuple or Vec3 for block access")

    def __setitem__(
        self,
        pos: tuple[int | slice, int | slice, int | slice] | Vec3,
        blocktype: str,
    ) -> None:
        """Allowed access:
        world[1,2,3] == world[Vec3(1,2,3)] == world[(1,2,3)] for single block access
        world[1:4, 2, 0:10:2] == world[1:4, 2:3, 0:10:2] for slice access]"""
        if not isinstance(blocktype, str):
            raise TypeError(f"Expected to set blocktype str, got {type(blocktype)} instead")

        if isinstance(pos, Vec3):
            return self.setBlock(blocktype, pos)
        elif isinstance(pos, tuple):
            if len(pos) == 3:
                if all(isinstance(el, int) for el in pos):
                    return self.setBlock(blocktype, Vec3(*pos))
                elif all(isinstance(el, (int, slice)) for el in pos):
                    spos = [el if isinstance(el, slice) else slice(el, el + 1) for el in pos]
                    if any(s.start is None or s.stop is None for s in spos):
                        raise ValueError("Open slices are forbidden")
                    for el in spos:
                        el.indices(0)  # only to raise Errors such as float or zero checks
                    positions = [
                        Vec3(x, y, z)
                        for x in range(spos[0].start, spos[0].stop, spos[0].step or 1)
                        for y in range(spos[1].start, spos[1].stop, spos[1].step or 1)
                        for z in range(spos[2].start, spos[2].stop, spos[2].step or 1)
                    ]  # TODO: make setBlockList to take Iterable instead of list
                    return self.setBlockList(blocktype, positions)
                else:
                    raise TypeError("Expected tuple with int or slice types")
            # TODO: think about setitem and getitem and possible options again
            else:
                raise TypeError("Expected a tuple 3 elements")
        else:
            x, y, z = pos  # attempt to unpack
            return self.setBlock(blocktype, Vec3(x, y, z))

    def _fetch_entities(
        self, include_non_spawnable: bool, with_locations: bool, entity_type: str
    ) -> list[entity.Entity]:
        request = pb.EntityRequest(
            worldwide=pb.EntityRequest.WorldEntities(
                world=self._pb_world,
                type=entity_type,
                includeNotSpawnable=include_non_spawnable,
            ),
            withLocations=with_locations,
        )
        response = self._stub.getEntities(request)
        raise_on_error(response.status)
        entities = []
        for e in response.entities:
            if include_non_spawnable and e.type == "player":
                # TODO: players are also included in getEntities(includeNotSpawnable=True) call
                continue
            nativeE = self._get_or_create_entity(e.id)
            if with_locations:
                nativeE._inject_update(e)
            else:
                # update only type
                nativeE._type = e.type
            entities.append(nativeE)
        return entities

    @property
    def pvp(self) -> bool:
        """True if any world on the server has pvp enabled.
        Can be set to enable or disable pvp on all worlds on the server.
        """
        # TODO: returning if ANY world has pvp
        response = self._stub.accessWorlds(pb.WorldRequest())
        raise_on_error(response.status)
        return any(world.info.pvp for world in response.worlds)

    @pvp.setter
    def pvp(self, value: bool) -> None:
        # TODO: setting ALL world pvp variables
        response = self._stub.accessWorlds(pb.WorldRequest())
        raise_on_error(response.status)
        response = self._stub.accessWorlds(
            pb.WorldRequest(
                worlds=[
                    pb.World(name=world.name, info=pb.WorldInfo(pvp=value))
                    for world in response.worlds
                ]
            )
        )
        raise_on_error(response.status)

    def getHighestPos(self, x: int, z: int) -> Vec3:
        """The position of the highest non-air block with given `x` and `z` in the world.

        :return: The position of the highest non-air block with given `x` and `z`
        :rtype: Vec3
        """
        response = self._stub.getHeight(pb.HeightRequest(world=self._pb_world, x=x, z=z))
        raise_on_error(response.status)
        pos = Vec3(response.block.pos.x, response.block.pos.y, response.block.pos.z)
        return pos

    def getHeight(self, x: int, z: int) -> int:
        "Equivalent to the y value of :func:`getHighestPos` with `x` and `z`."
        return self.getHighestPos(x, z).y  # type: ignore

    def getBlock(self, pos: Vec3) -> str:
        """The block type/id at position `pos` in world.

        .. note::

           The function does only query the block type/id, no additional block data is included.

        :param pos: position to query block from
        :type pos: Vec3
        :return: block type/id at queried position
        :rtype: str
        """
        response = self._stub.getBlock(
            pb.BlockRequest(world=self._pb_world, pos=pb.Vec3(**pos.floor().asdict()))
        )
        raise_on_error(response.status)
        return response.info.blockType

    # TODO: differentiate between block type and Block
    # def getBlockWithData(self, pos: Vec3) -> Block:
    #     raise NotImplementedError

    def getBlockList(self, positions: list[Vec3]) -> list[str]:
        """The list of all block types/ids at given `positions` in world in the same order.

        .. note::

           The function does only query the block types/ids, no additional block data is included.

        :param positions: list of positions to query
        :type positions: list[Vec3]
        :return: list of block types/ids at given positions (same order)
        :rtype: list[str]
        """
        # TODO: natively support this operation
        return [self.getBlock(pos) for pos in positions]

    def setBlock(self, blocktype: str, pos: Vec3) -> None:
        """Change the block at position `pos` to `blocktype` in world.
        This will overwrite any block at that position.

        :param blocktype: the valid block type/id to set the block to
        :type blocktype: str
        :param pos: the position where the block should be set
        :type pos: Vec3
        """
        response = self._stub.setBlock(
            pb.Block(
                world=self._pb_world,
                info=pb.BlockInfo(blockType=blocktype),
                pos=pb.Vec3(**pos.floor().asdict()),
            )
        )
        raise_on_error(response)

    def setBed(self, pos: Vec3, direction: CARDINAL = "east", color: COLOR = "red") -> None:
        """Place a bed at `pos` in `direction` with `color`, which is composed of two placed blocks with specific block data.

        :param pos: the position of foot part of bed
        :type pos: Vec3
        :param direction: direction in which to place head part of bed, defaults to "east"
        :type direction: CARDINAL, optional
        :param color: color of bed, defaults to "red"
        :type color: COLOR, optional
        """
        pos = pos.floor()
        pos2 = getattr(pos, direction)(1)
        self.runCommand(
            f"setblock {pos.x} {pos.y} {pos.z} {color}_bed[part=foot,facing={direction}]"
        )
        self.runCommand(
            f"setblock {pos2.x} {pos2.y} {pos2.z} {color}_bed[part=head,facing={direction}]"
        )

    def setBlockList(self, blocktype: str, positions: list[Vec3]) -> None:
        """Change all blocks at `positions` to `blocktype` in world.
        This will overwrite all blocks at the given positions.
        This is more efficient that using :func:`setBlock` mutliple times with the same `blocktype`.

        :param blocktype: the valid block type/id to set the blocks to
        :type blocktype: str
        :param positions: the positions where the blocks should be set
        :type positions: list[Vec3]
        """
        for chunk in (
            positions[index : index + MAX_BLOCKS] for index in range(0, len(positions), MAX_BLOCKS)
        ):
            response = self._stub.setBlocks(
                pb.Blocks(
                    world=self._pb_world,
                    info=pb.BlockInfo(blockType=blocktype),
                    pos=[pb.Vec3(**pos.floor().asdict()) for pos in chunk],
                )
            )
            raise_on_error(response)

    def setBlockCube(self, blocktype: str, pos1: Vec3, pos2: Vec3) -> None:
        """Change all blocks in a cube between the corners `pos1` and `pos2` in world to `blocktype`, where both positions are *inclusive*. meaning that both given positions/corners will be part of the cube.
        This will overwrite all blocks between the given positions.
        The positions span a cube if all their coordinates are different,
        a plane if one of their coordinates is the same or a line if two of their three coordinates are the same.


        .. code-block:: python

           # xlen, ylen, zlen are the length of the cube in the specified axis
           start = Vec3()  # this would be the lowest (most negative coordinates) corner of the cube we want to draw, here origin
           world.setBlockCube("diamond_block", start, start.addX(xlen).addY(ylen).addZ(zlen))

           # this is equivalent to (but more efficent and faster than)

           for x in range(xlen + 1):
               for y in range(ylen + 1):
                   for z in range(zlen + 1):
                       world.setBlock("diamond_block", start.addX(x).addY(y).addZ(z))

        :param blocktype: the valid block type/id to set the blocks to
        :type blocktype: str
        :param pos1: the position of one corner of the cube
        :type pos1: Vec3
        :param pos2: the position of the opposite corner of the cube
        :type pos2: Vec3
        """
        response = self._stub.setBlockCube(
            pb.Blocks(
                world=self._pb_world,
                info=pb.BlockInfo(blockType=blocktype),
                pos=[
                    pb.Vec3(**pos1.floor().asdict()),
                    pb.Vec3(**pos2.floor().asdict()),
                ],
            )
        )
        raise_on_error(response)

    def copyBlockCube(self, pos1: Vec3, pos2: Vec3) -> list[list[list[str]]]:
        """Get all block types in a cube between `pos1` and `pos2` inclusive.
        Should be used in conjunction with :func:`pasteBlockCube`.

        .. note::

           The function does only copy the block types/ids, no additional block data is included.

        :param pos1: the position of one corner of the cube
        :type pos1: Vec3
        :param pos2: the position of the opposite corner of the cube
        :type pos2: Vec3
        :return: the block types in the cube given as rows of x with columns of y with slices of depth z respectively
        :rtype: list[list[list[str]]]
        """
        pos1, pos2 = pos1.map_pairwise(min, pos2), pos1.map_pairwise(max, pos2)
        pos1, pos2 = pos1.floor(), pos2.floor()
        return [
            [
                [self.getBlock(Vec3(x, y, z)) for z in range(pos1.z, pos2.z + 1)]
                for y in range(pos1.y, pos2.y + 1)
            ]
            for x in range(pos1.x, pos2.x + 1)
        ]

    def pasteBlockCube(
        self,
        blocktypes: list[list[list[str]]],
        pos: Vec3,
        rotation: DIRECTION = "east",
        flip_x: bool = False,
        flip_y: bool = False,
        flip_z: bool = False,
    ) -> None:
        """Paste the block types in the cube `blocktypes` into the world at position `pos` where `pos` is the negative most corner of the cube along all three axes.
        Additional options can be used to change the rotation of blocks in the copied cube, however, no matter in which way the cube is rotated and/or flipped, `pos` will also be the most negative corner.
        Should be used in conjunction with :func:`copyBlockCube`.

        .. note::

           The :func:`copyBlockCube` function does only copy the block types/ids, no additional block data is included.

        .. code-block:: python

           start = Vec3(0, 0, 0)
           end = start.addX(5).addY(5).addZ(5)
           # copy a 6x6x6 block cube from origin in world
           blocks = world.copyBlockCube(start, end)
           # replace that space with the same blocks but rotated by 90 degrees
           world.pasteBlockCube(blocks, start, "south")
           # copy same original block at different point above origin
           world.pasteBlockCube(blocks, start.up(200))


        :param blocktypes: the cube of block types/ids that should be pasted, given as rows of x with columns of y with slices of depth z respectively
        :type blocktypes: list[list[list[str]]]
        :param pos: the most negative corner along all three axes of the cube where the cube should be pasted
        :type pos: Vec3
        :param rotation: the direction of the x axis of the cube to be pasted ("east" means copied x axis aligns with real x axis, i.e., the original orientation), defaults to "east"
        :type rotation: DIRECTION, optional
        :param flip_x: flip pasted blocks along x axis, defaults to False
        :type flip_x: bool, optional
        :param flip_y: flip pasted blocks along y axis, defaults to False
        :type flip_y: bool, optional
        :param flip_z: flip pasted blocks along z axis, defaults to False
        :type flip_z: bool, optional
        """
        pos = pos.floor()
        xlen, ylen, zlen = len(blocktypes), len(blocktypes[0]), len(blocktypes[0][0])
        xstride, ystride, zstride = ylen * zlen, zlen, 1
        blocks = [blocktype for xslice in blocktypes for yline in xslice for blocktype in yline]
        if rotation == "east":
            pass  # noting to do
        elif rotation == "south":
            # np.rot90(c, k=1, axes=(0,2)) == np.flip(c, axis=2).T
            zstride = -zstride
            xlen, xstride, zlen, zstride = zlen, zstride, xlen, xstride
        elif rotation == "west":
            xstride = -xstride
            zstride = -zstride
        elif rotation == "north":
            # np.rot90(c, k=3, axes=(0,2)) == np.flip(c.T, axis=2)
            xlen, xstride, zlen, zstride = zlen, zstride, xlen, xstride
            zstride = -zstride
        elif rotation == "up":
            ystride = -ystride
            xlen, xstride, ylen, ystride = ylen, ystride, xlen, xstride
        elif rotation == "down":
            xlen, xstride, ylen, ystride = ylen, ystride, xlen, xstride
            ystride = -ystride
        else:
            raise ValueError(f"Rotation should be a direction, was '{rotation}'")
        if flip_x:
            xstride = -xstride
        if flip_y:
            ystride = -ystride
        if flip_z:
            zstride = -zstride
        xrange = range(xlen) if xstride >= 0 else range(xlen - 1, -1, -1)
        yrange = range(ylen) if ystride >= 0 else range(ylen - 1, -1, -1)
        zrange = range(zlen) if zstride >= 0 else range(zlen - 1, -1, -1)
        for xindex, x in enumerate(xrange):
            for yindex, y in enumerate(yrange):
                for zindex, z in enumerate(zrange):
                    index = x * abs(xstride) + y * abs(ystride) + z * abs(zstride)
                    assert (
                        0 <= index < len(blocks)
                    ), f"{x=} {y=}, {z=} {xstride=} {ystride=} {zstride=} {index=} len={len(blocks)}"
                    self.setBlock(
                        blocks[index],
                        Vec3(pos.x + xindex, pos.y + yindex, pos.z + zindex),
                    )

    def spawnEntity(self, type: str, pos: Vec3) -> entity.Entity:
        """Spawn and return a new entitiy of given `type` at position `pos` in world.
        The entity has default settings and behavior.

        :param type: the valid entity type that should be spawned (must be spawnable without additional parameters)
        :type type: str
        :param pos: the position where to spawn the entitiy in the world
        :type pos: Vec3
        :return: the :class:`Entity` entity spawned
        :rtype: entity.Entity
        """
        response = self._stub.spawnEntity(
            pb.Entity(
                type=type,
                location=pb.EntityLocation(world=self._pb_world, pos=pb.Vec3f(**pos.asdict())),
            )
        )
        raise_on_error(response.status)
        entity = self._get_or_create_entity(response.entity.id)
        entity._type = response.entity.type
        return entity

    def spawnItems(self, pos: Vec3, type: str, amount: int = 1) -> None:
        """Spawn `amount` many collectable items of `type` at `pos`.

        :param pos: position where to spawn the items
        :type pos: Vec3
        :param type: the item type, e.g., ``"minecraft:arrow"``
        :type type: str
        :param amount: number of items to spawn, defaults to 1
        :type amount: int, optional
        """
        pos = pos.floor()
        self.runCommand(
            f'summon item {pos.x} {pos.y} {pos.z} {{Item:{{id:"{type}", Count:{amount}}}}}'
        )

    def getEntities(
        self, type: str | None = None, only_spawnable: bool = True
    ) -> list[entity.Entity]:
        """Get all (loaded) entities in the world.
        If a `type` is provided, only entities of that type are returned.
        By default only entities of types that could be spawned using :func:`spawnEntity` are returned.
        To get all entities (except players) set ``only_spawnable=False``, which will also return non-spawnable entities such as e.g. ``"falling_block"`` or ``"dropped_item"``.

        :param type: if provided returns only entities of that type, returns all types if None, defaults to None
        :type type: str | None, optional
        :param only_spawnable: if False, will also return non-spawnable entities, defaults to True
        :type only_spawnable: bool, optional
        :return: list of (loaded and filtered) entities in the world
        :rtype: list[entity.Entity]
        """
        return self._fetch_entities(not only_spawnable, False, type if type else "")

    def getEntitiesAround(
        self,
        pos: Vec3,
        distance: float,
        type: str | None = None,
        only_spawnable: bool = True,
    ) -> list[entity.Entity]:
        """Equivalent to :func:`getEntities`, however, is filtered to only return entities within `distance` around `pos`. Is more efficient that filtering the list manually.

        :param pos: position around which the entities are returned
        :type pos: Vec3
        :param distance: the maximum distance entities returned have around `pos`
        :type distance: float
        :param type: if provided returns only entities of that type, returns all types if None, defaults to None
        :type type: str | None, optional
        :param only_spawnable: if False, will also return non-spawnable entities, defaults to True
        :type only_spawnable: bool, optional
        :return: list of (loaded and filtered) entities in the world closer than `distance` to `pos`
        :rtype: list[entity.Entity]
        """
        entities = self._fetch_entities(not only_spawnable, True, type if type else "")
        return [e for e in entities if pos.distance(e.pos) <= distance]

    def removeEntities(self, type: str | None = None) -> None:
        """Remove all entities (except players) from the world, they do not drop anything.
        If `type` is provided remove only entities of that type.

        :param type: if provided removes only entities of that type, otherwise remove all entities, defaults to None
        :type type: str | None, optional
        """
        # TODO: support natively
        if type is None:
            self.runCommand("tp @e[type=!player] 0 -50000 0")
            self.runCommand("kill @e[type=!player]")
        elif isinstance(type, str):
            self.runCommand(f"tp @e[type={type}] 0 -50000 0")
            self.runCommand(f"kill @e[type={type}]")
        else:
            raise TypeError("Type should be of type str")


class World(_DefaultWorld, _HasStub, _EntityProvider):
    """Manipulating the world is the heart piece of the entire library.
    With this you can query blocks and world features and set them in turn, as well as finding and spawning entities in the world.
    This allows building on the server quickly and precisely with only a few commands.
    Note that all commands of :class:`World` will only manipulate that world, for example, :func:`getEntities` will *only* return entities in *this* world.

    Do not instantiate the :class:`World` class directly but use one of the following methods instead:

    .. code-block:: python

       world = mc.overworld
       world = mc.nether
       world = mc.end
       someotherworld = mc.getWorldByKey("mod_namespace:world_key")

    Once you have your world you can use it in a multitude of ways:

    .. code-block:: python

       world.pvp = False  # disable pvp only in this world
       ground_pos = world.getHeighestPos(0, 0)  # get heighest position on ground (= non-air) at origin
       block = world.getBlock(ground_pos)  # get the block type there
       world.setBlock("diamond_block", ground_pos)  # replace that block at location with diamond
       # set every second block in a line along the x axis to emerald
       world.setBlockList("emerald_block", [ground_pos.up(2).east(i) for i in range(0,20,2)])
       world.setBlockCube("oak_planks", ground_pos.up(50), ground_pos.up(50) + 9)  # set a 10 x 10 x 10 oak plank block 50 blocks above ground
       sheep = world.spawnEntity("sheep", ground_pos.up(1))  # spawn a sheep on that block
       entities = world.getEntities()  # get all (loaded) entities
       entities = world.getEntitiesAround(ground_pos, 20)  # get all  (loaded) entities around origin highest block in 20 block radius
       world.removeEntities("sheep")  # remove all (loaded) sheep
       blocks = world.copyBlockCube(Vec3(0,0,0), Vec3(5,5,5))  # copy all blocks between those two points (inclusive)
       world.pasteBlockCube(blocks, ground_pos.up(20))  # paste back the copied blocks 20 blocks above origin ground
       world.setBed(ground_pos.up(1))  # place a bed on top of diamond block

    .. note::

       When using the world functions on :class:`Minecraft` (``mc``) directly the 'default' world is used. The default world is defined by the server as the first world loaded by the server, which is usually the overworld.
       If you want to affect a specific world, use :class:`World` classes instead, such as ``mc.overworld``, ``mc.nether`` or ``mc.end``.
    """

    def __init__(
        self, stub: MinecraftStub, entity_provider: _EntityProvider, key: str, name: str
    ) -> None:
        super().__init__(stub)
        self._entity_provider = entity_provider
        self._key = key
        self._name = name

    def _get_or_create_entity(self, entity_id: str):
        return self._entity_provider._get_or_create_entity(entity_id)

    @property
    def _pb_world(self) -> pb.World:
        return pb.World(name=self.name)

    @property
    def key(self) -> str:
        """The key/id of this world, e.g., ``"minecraft:overworld"`` or ``"minecraft:the_nether"``"""
        return self._key

    @property
    def name(self) -> str:
        """The name of the folder/namespace the world resides in, e.g., ``"world"`` or ``"world_the_nether"``"""
        return self._name

    @property
    def pvp(self) -> bool:
        """True if pvp is enabled in this world. Can be set to enable or disable pvp in only this world."""
        response = self._stub.accessWorlds(pb.WorldRequest(worlds=[self._pb_world]))
        raise_on_error(response.status)
        return response.worlds[0].info.pvp

    @pvp.setter
    def pvp(self, value: bool) -> None:
        response = self._stub.accessWorlds(
            pb.WorldRequest(worlds=[pb.World(name=self.name, info=pb.WorldInfo(pvp=value))])
        )
        raise_on_error(response.status)

    def __repr__(self) -> str:
        # return f"{self.__class__.__name__}(name={self.name}, key={self.key})"
        return f"{self.__class__.__name__}(key={self.key})"

    def runCommand(self, command: str) -> None:
        """Run the `command` as if it was typed in chat as ``/``-command and executed in this specific world/dimension..

        .. code-block:: python

           world.runCommand("kill @e")  # kill all loaded entities in this world

        :param command: the command without the slash ``/``
        :type command: str
        """
        command = f"execute in {self.key} run " + command
        return super().runCommand(command)


class _WorldHub(_HasStub, _EntityProvider):
    """All functions regarding getting World objects and interacting with different worlds.

    .. note::

       What is called :class:`World` here is referred to as a dimension in game.

    """

    def __init__(self, stub: MinecraftStub) -> None:
        super().__init__(stub)
        self._world_by_name_cache = ThreadSafeSingeltonCache(None)

    @property
    def worlds(self) -> tuple[World, ...]:
        """Give a tuple of all worlds loaded on the server.
        Does not automatically call :func:`refreshWorlds`.

        :return: A tuple of all worlds loaded on the server
        :rtype: tuple[World, ...]
        """
        if not self._world_by_name_cache:
            self.refreshWorlds()
        return tuple(self._world_by_name_cache.values())

    @property
    def overworld(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:overworld"``.

        :return: The overworld world :class:`World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:overworld")

    @property
    def nether(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:the_nether"``.

        :return: The nether world :class:`World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:the_nether")

    @property
    def end(self) -> World:
        """Identical to :func:`getWorldByKey` with key ``"minecraft:the_end"``.

        :return: The end world :class:`World` object
        :rtype: World
        """
        return self.getWorldByKey("minecraft:the_end")

    def getWorldByKey(self, key: str) -> World:
        """The `key` of a world is the dimensions internal name/id.
        Typically a regular server has the following worlds/keys:

        - ``"minecraft:overworld"``

        - ``"minecraft:the_nether"``

        - ``"minecraft:the_end"``

        The ``"minecraft:"`` prefix may be omitted, e.g., ``"the_nether"``.

        If the given `key` does not exist an exception is raised.

        :param key: Internal name/id of the world, such as ``"minecraft:the_nether"`` or ``"the_nether"``
        :type key: str
        :return: The corresponding :class:`World` object
        :rtype: World
        """
        parts = key.split(":", maxsplit=1)
        if len(parts) == 1:
            key = "minecraft:" + key
        for world in self.worlds:
            if world.key == key:
                return world
        raise_on_error(pb.Status(code=pb.WORLD_NOT_FOUND, extra="key=" + key))

    def getWorldByName(self, name: str) -> World:
        """The `name` of a world is the folder or namespace the world resides in.
        The setting for the world the server opens is found in ``server.properties``.
        A typical, unmodified PaperMC_ server will save the worlds in the following folders:

        .. _PaperMC: https://papermc.io/

        - ``"world"``, for the overworld

        - ``"world_the_nether"``, for the nether

        - ``"world_the_end"``, for the end

        The name of the overworld (default ``world``) is used as the prefix for the other folders.

        If the given `name` does not exist an exception is raised.

        :param name: Foldername the world is saved in, such as ``world``
        :type name: str
        :return: The corresponding :class:`World` object
        :rtype: World
        """
        if not self._world_by_name_cache:
            self.refreshWorlds()
        world = self._world_by_name_cache.get(name)
        if world is None:
            raise_on_error(pb.Status(code=pb.WORLD_NOT_FOUND, extra="name=" + name))
        return world

    def refreshWorlds(self) -> None:
        """Fetches the currently loaded worlds from server and updates the world objects.
        This should only be called if the loaded worlds on the server change, for example, with the Multiverse Core Plugin.
        By default, the worlds will be refreshed on first use only.
        """
        response = self._stub.accessWorlds(pb.WorldRequest())
        raise_on_error(response.status)
        for world in response.worlds:
            factory = partial(World, self._stub, self, world.info.key)
            self._world_by_name_cache.get_or_create(world.name, factory)
