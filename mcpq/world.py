from __future__ import annotations

from . import entity
from ._abc import _ServerInterface
from ._base import _HasServer, _SharedBase
from ._proto import minecraft_pb2 as pb
from ._types import CARDINAL, COLOR, DIRECTION
from ._util import warning
from .exception import raise_on_error
from .nbt import NBT, Block, EntityType
from .vec3 import Vec3

MAX_BLOCKS = 50000  # TODO: replace with block stream


class _DefaultWorld(_SharedBase, _HasServer):
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
       ground_pos = mc.getHeighestPos(0, 0)  # get position of heighest ground at origin
       block = mc.getBlock(ground_pos)  # get the block type there
       mc.setBlock("diamond_block", ground_pos)  # replace that block at location with diamond
       mc.setBlockList("emerald_block", [ground_pos.up(2).east(i) for i in range(0,20,2)])  # set every second block in a line along the x axis to emerald
       # set a 10 x 10 x 10 oak plank block 50 blocks above ground
       mc.setBlockCube("oak_planks", ground_pos.up(50), ground_pos.up(50) + 9)
       # spawn a sheep on that block
       sheep = mc.spawnEntity("sheep", ground_pos.up(1))
       entities = mc.getEntities()  # get all (loaded) entities
       # get all  (loaded) entities around origin highest block in 20 block radius
       entities = mc.getEntitiesAround(ground_pos, 20)
       mc.removeEntities("sheep")  # remove all (loaded) sheep
       # copy all blocks between those two points (inclusive)
       blocks = mc.copyBlockCube(Vec3(0,0,0), Vec3(5,5,5))
       # paste back the copied blocks 20 blocks above origin ground
       mc.pasteBlockCube(blocks, ground_pos.up(20))
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
        self, include_non_spawnable: bool, with_locations: bool, entity_type: str | EntityType
    ) -> list[entity.Entity]:
        if entity_type and not isinstance(entity_type, EntityType):
            entity_type = EntityType(entity_type).type
        request = pb.EntityRequest(
            worldwide=pb.EntityRequest.WorldEntities(
                world=self._pb_world,
                type=entity_type,
                includeNotSpawnable=include_non_spawnable,
            ),
            withLocations=with_locations,
        )
        response = self._server.stub.getEntities(request)
        raise_on_error(response.status)
        entities = []
        for e in response.entities:
            if include_non_spawnable and e.type == "player":
                # TODO: players are also included in getEntities(includeNotSpawnable=True) call
                continue
            nativeE = self._server.get_or_create_entity(e.id)
            if with_locations:
                nativeE._inject_update(e)
            else:
                # update only type
                nativeE._type = EntityType(e.type)
            entities.append(nativeE)
        return entities

    @property
    def pvp(self) -> bool:
        """True if any world on the server has pvp enabled.
        Can be set to enable or disable pvp on all worlds on the server.
        """
        response = self._server.stub.accessWorlds(pb.WorldRequest())
        raise_on_error(response.status)
        return any(world.info.pvp for world in response.worlds)

    @pvp.setter
    def pvp(self, value: bool) -> None:
        response = self._server.stub.accessWorlds(
            pb.WorldRequest(
                worlds=[
                    pb.World(name=world.name, info=pb.WorldInfo(pvp=value))
                    for world in self._server.get_worlds()
                ]
            )
        )
        raise_on_error(response.status)

    def getHighestPos(self, x: int, z: int) -> Vec3:
        """The position of the highest non-air block with given `x` and `z` in the world.

        :return: The position of the highest non-air block with given `x` and `z`
        :rtype: Vec3
        """
        response = self._server.stub.getHeight(pb.HeightRequest(world=self._pb_world, x=x, z=z))
        raise_on_error(response.status)
        pos = Vec3(response.block.pos.x, response.block.pos.y, response.block.pos.z)
        return pos

    def getHeight(self, x: int, z: int) -> int:
        "Equivalent to the y value of :func:`getHighestPos` with `x` and `z`."
        return self.getHighestPos(x, z).y  # type: ignore

    def getBlock(self, pos: Vec3) -> Block:
        """The block :class:`Block` type/id at position `pos` in world.

        .. note::

           The function does only query the block type/id, no block component data is not queried.
           To query block component data use :func:`getBlockWithData`.

        :param pos: position to query block from
        :type pos: Vec3
        :return: block type/id at queried position
        :rtype: Block
        """
        pos = pos.floor()
        response = self._server.stub.getBlock(
            pb.BlockRequest(world=self._pb_world, pos=pb.Vec3(x=pos.x, y=pos.y, z=pos.z))
        )
        raise_on_error(response.status)
        return Block(response.info.blockType)

    def getBlockWithData(self, pos: Vec3) -> Block:
        """The block :class:`Block` at position `pos` in world including block component data.

        :param pos: position to query block from
        :type pos: Vec3
        :return: block type/id and component data at queried position
        :rtype: Block
        """
        pos = pos.floor()
        response = self._server.stub.getBlock(
            pb.BlockRequest(
                world=self._pb_world,
                pos=pb.Vec3(x=pos.x, y=pos.y, z=pos.z),
                withData=True,
            ),
        )
        raise_on_error(response.status)
        return Block(response.info.blockType + response.info.blockData)

    def getBlockList(self, positions: list[Vec3]) -> list[Block]:
        """The list of all block :class:`Block` types/ids at given `positions` in world in the same order.

        .. note::

           The function does only query the block type/ids, no block component data is not queried.

        :param positions: list of positions to query
        :type positions: list[Vec3]
        :return: list of block types/ids at given positions (same order)
        :rtype: list[Block]
        """
        # TODO: natively support this operation
        return [self.getBlock(pos) for pos in positions]

    def getBlockListWithData(self, positions: list[Vec3]) -> list[Block]:
        """The list of all block :class:`Block` at given `positions` in world with component data in the same order.

        :param positions: list of positions to query
        :type positions: list[Vec3]
        :return: list of block type/ids and component data at given positions (same order)
        :rtype: list[Block]
        """
        # TODO: natively support this operation
        return [self.getBlockWithData(pos) for pos in positions]

    def setBlock(self, blocktype: str | Block, pos: Vec3) -> None:
        """Change the block at position `pos` to `blocktype` in world.
        This will overwrite any block at that position.

        :param blocktype: the valid block type/id or :class:`Block` to set the block to
        :type blocktype: str | Block
        :param pos: the position where the block should be set
        :type pos: Vec3
        """
        pos = pos.floor()
        pb_info = (
            pb.BlockInfo(blockType=blocktype.type, blockData=blocktype.datastr)
            if isinstance(blocktype, Block) and blocktype.hasData
            else pb.BlockInfo(blockType=blocktype)
        )
        response = self._server.stub.setBlock(
            pb.Block(
                world=self._pb_world,
                info=pb_info,
                pos=pb.Vec3(x=pos.x, y=pos.y, z=pos.z),
            )
        )
        raise_on_error(response)

    def setBlockList(self, blocktype: str | Block, positions: list[Vec3]) -> None:
        """Change all blocks at `positions` to `blocktype` in world.
        This will overwrite all blocks at the given positions.
        This is more efficient that using :func:`setBlock` multiple times with the same `blocktype`.

        :param blocktype: the valid block type/id to set the blocks to
        :type blocktype: str | Block
        :param positions: the positions where the blocks should be set
        :type positions: list[Vec3]
        """
        pb_info = (
            pb.BlockInfo(blockType=blocktype.type, blockData=blocktype.datastr)
            if isinstance(blocktype, Block) and blocktype.hasData
            else pb.BlockInfo(blockType=blocktype)
        )
        for chunk in (
            positions[index : index + MAX_BLOCKS] for index in range(0, len(positions), MAX_BLOCKS)
        ):
            floored = (pos.floor() for pos in chunk)
            response = self._server.stub.setBlocks(
                pb.Blocks(
                    world=self._pb_world,
                    info=pb_info,
                    pos=[pb.Vec3(x=pos.x, y=pos.y, z=pos.z) for pos in floored],
                )
            )
            raise_on_error(response)

    def setBlockCube(self, blocktype: str | Block, pos1: Vec3, pos2: Vec3) -> None:
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
        :type blocktype: str | Block
        :param pos1: the position of one corner of the cube
        :type pos1: Vec3
        :param pos2: the position of the opposite corner of the cube
        :type pos2: Vec3
        """
        pos1, pos2 = pos1.floor(), pos2.floor()
        pb_info = (
            pb.BlockInfo(blockType=blocktype.type, blockData=blocktype.datastr)
            if isinstance(blocktype, Block) and blocktype.hasData
            else pb.BlockInfo(blockType=blocktype)
        )
        response = self._server.stub.setBlockCube(
            pb.Blocks(
                world=self._pb_world,
                info=pb_info,
                pos=[
                    pb.Vec3(x=pos1.x, y=pos1.y, z=pos1.z),
                    pb.Vec3(x=pos2.x, y=pos2.y, z=pos2.z),
                ],
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
        # must place head first, otherwise foot breaks
        self.setBlock(Block(f"{color}_bed[part=head,facing={direction}]"), pos2)
        self.setBlock(Block(f"{color}_bed[part=foot,facing={direction}]"), pos)

    def setSign(
        self,
        pos: Vec3,
        text: list[str | NBT | dict] | str,
        *,
        color: COLOR = "black",
        glowing: bool = False,
        direction: CARDINAL | int = "south",
        sign_block: str | Block = "oak_sign",
    ) -> None:
        """Place a sign block at `pos` with `text` overwriting any block there.
        `text` can be a list of at most 8 elements, where each element is a line of text on the sign; the first 4 on the front and the second 4 on the back.
        Lists with fewer than 8 elements are allowed and result in empty following lines.
        `text` may also be a string in which case the above list is built by splitting the string on newlines.
        The elements in the list may also be :class:`NBT` instances of the form:
        ``{selector: "@p", color: "red", bold: false, italic: false, underlined: false, strikethrough: false, obfuscated: false, text: "A Line of Text"}``
        The material and type of sign can be set with `sign_block` - it can be a sign, wall_sign, or hanging_sign of any given wood material.

        .. code-block:: python

           pos = Vec3(0, 120, 0) # position where to place sign
           mc.setSign(pos, "Hello Minecraft") # front line 1
           mc.setSign(pos, "Hello\\nMinecraft") # front line 1 and 2
           mc.setSign(pos, ["Hello", "Minecraft"]) # front line 1 and 2
           mc.setSign(pos, ["", "Hello", "Minecraft"]) # front line 2 and 3
           # back line 6 and 7
           mc.setSign(pos, ["", "", "", "",  "", "Hello", "Minecraft"])
           # everything beyond line 8 (back line 4) is not on sign anymore
           mc.setSign(pos, ["", "", "", "",  "", "", "", "",  "NOT ON SIGN"])
           # line-wise customization with NBT compounds or dicts
           mc.setSign(pos, [{"text": "Hello", "color": "red"}, NBT({"text": "Minecraft", "bold": True})])

           valid_signs = mc.blocks.endswith("_sign")
           mc.setSign(..., sign_block="spruce_sign")
           mc.setSign(..., sign_block="jungle_wall_sign")
           mc.setSign(..., sign_block="acacia_hanging_sign")
           mc.setSign(..., sign_block="acacia_hanging_sign[attached=true]")
           mc.setSign(..., sign_block=Block("oak_sign").withData({"waterlogged": True}))

           mc.setSign(pos, "\\nHello\\nMinecraft\\n", direction="east", color="green", glowing=True)

        :param pos: the position where the sign should be set
        :type pos: Vec3
        :param text: the text to put on sign either as list of at most 8 elements, where the first 4 are text on the front and the second set of 4 are the text on the back of the sign, or as a string, where said list is produced by splitting on newlines. Elements of the list may also be NBT compounds instead of strings.
        :type text: list[str | NBT | dict[str, Any]] | str
        :param color: the base color of the text on the sign, can be overwritten on a per-line basis by providing `NBT({"text":"...","color":"red"})` NBT compounds, defaults to "black"
        :type color: COLOR, optional
        :param glowing: whether or not the text should use the glowing effect, defaults to False
        :type glowing: bool, optional
        :param direction: the cardinal direction the sign should be facing, for non-wall signs can also be an integer between 0-15, defaults to "south"
        :type direction: CARDINAL | int, optional
        :param sign_block: the block type/id of the sign that should be placed, should end with "_sign", defaults to "oak_sign"
        :type sign_block: str | Block, optional
        """
        # TODO: mc version
        pos = pos.floor()
        if isinstance(text, str):
            text = text.split("\n")
        else:
            text = list(text)
        if not isinstance(sign_block, Block):
            sign_block = Block(sign_block)
        if direction is not None:
            facing = sign_block.getData()
            if sign_block.type.endswith("_wall_sign"):
                # use 'facing' (CARDINAL)
                if not isinstance(direction, str):
                    raise TypeError(
                        f"Wall signs can only face a cardinal direction expected type str got {type(direction)}"
                    )
                facing.string["facing"] = direction
            else:
                # use 'rotation' (int 0-15)
                if isinstance(direction, str):
                    direction = {"south": 0, "west": 4, "north": 8, "east": 12}[direction]
                facing.int["rotation"] = direction
            sign_block = sign_block.withData(facing)

        messages = []
        for msg in text[:8]:
            if isinstance(msg, NBT):
                messages.append(msg)
            elif isinstance(msg, dict):
                messages.append(NBT(msg))
            else:
                n = NBT()
                n.string["text"] = msg
                messages.append(n)
        messages.extend([NBT({"text": ""})] * (8 - len(messages)))
        assert len(messages) == 8

        nbt = NBT()
        front = nbt.get_or_create_nbt("front_text")
        back = nbt.get_or_create_nbt("back_text")
        front.get_or_create_list("messages").string.extend(messages[:4])
        back.get_or_create_list("messages").string.extend(messages[4:8])
        front.byte["has_glowing_text"] = 1 if glowing else 0
        back.byte["has_glowing_text"] = 1 if glowing else 0
        front.string["color"] = color
        back.string["color"] = color
        # using /setblock will not change nbt data if identical block is already there
        # cmd = f"setblock {pos.x} {pos.y} {pos.z} {sign_block}{nbt} replace"
        cmd = f"data merge block {pos.x} {pos.y} {pos.z} {nbt}"
        self.setBlock(sign_block, pos)
        self.runCommand(cmd)

    def copyBlockCube(
        self, pos1: Vec3, pos2: Vec3, withData: bool = False
    ) -> list[list[list[Block]]]:
        """Get all block types in a cube between `pos1` and `pos2` inclusive.
        Should be used in conjunction with :func:`pasteBlockCube`.

        :param pos1: the position of one corner of the cube
        :type pos1: Vec3
        :param pos2: the position of the opposite corner of the cube
        :type pos2: Vec3
        :param withData: whether block component data should be queried, defaults to False
        :type withData: bool, optional
        :return: the block types in the cube given as rows of x with columns of y with slices of depth z respectively
        :rtype: list[list[list[Block]]]
        """
        pos1, pos2 = pos1.map_pairwise(min, pos2), pos1.map_pairwise(max, pos2)
        pos1, pos2 = pos1.floor(), pos2.floor()
        getfunc = self.getBlockWithData if withData else self.getBlock
        return [
            [
                [getfunc(Vec3(x, y, z)) for z in range(pos1.z, pos2.z + 1)]
                for y in range(pos1.y, pos2.y + 1)
            ]
            for x in range(pos1.x, pos2.x + 1)
        ]

    def pasteBlockCube(
        self,
        blocktypes: list[list[list[str | Block]]],
        pos: Vec3,
        rotation: DIRECTION = "east",
        flip_x: bool = False,
        flip_y: bool = False,
        flip_z: bool = False,
    ) -> None:
        """Paste the block types in the cube `blocktypes` into the world at position `pos` where `pos` is the negative most corner of the cube along all three axes.
        Additional options can be used to change the rotation of blocks in the copied cube, however, no matter in which way the cube is rotated and/or flipped, `pos` will also be the most negative corner.
        Should be used in conjunction with :func:`copyBlockCube`.

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
        :type blocktypes: list[list[list[str | Block]]]
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

    def spawnEntity(self, type: str | EntityType, pos: Vec3) -> entity.Entity:
        """Spawn and return a new entitiy of given `type` at position `pos` in world.
        The entity has default settings and behavior.

        :param type: the valid entity type that should be spawned (must be spawnable without additional parameters)
        :type type: str | EntityType
        :param pos: the position where to spawn the entitiy in the world
        :type pos: Vec3
        :return: the :class:`Entity` entity spawned
        :rtype: entity.Entity
        """
        pos = pos.map(float)
        if isinstance(type, EntityType) and type.hasData:
            raise NotImplementedError(
                f"spawnEntity does not support additional component data on entity: {type}"
            )
        response = self._server.stub.spawnEntity(
            pb.Entity(
                type=type.type if isinstance(type, EntityType) else type,
                location=pb.EntityLocation(
                    world=self._pb_world, pos=pb.Vec3f(x=pos.x, y=pos.y, z=pos.z)
                ),
            )
        )
        raise_on_error(response.status)
        entity = self._server.get_or_create_entity(response.entity.id)
        entity._type = EntityType(response.entity.type)
        return entity

    def spawnItems(self, type: str | Block, pos: Vec3, amount: int = 1) -> None:
        """Spawn `amount` many collectable items of `type` at `pos`.

        :param type: the item type as string or :class:`Block`, e.g., ``"minecraft:arrow"`` with potential component data
        :type type: str | Block
        :param pos: position where to spawn the items
        :type pos: Vec3
        :param amount: number of items to spawn, defaults to 1
        :type amount: int, optional
        """
        if isinstance(type, Vec3) and isinstance(pos, str):
            warning(
                "Used spawnItems with wrong parameter order, expected first type: str | Block then pos: Vec3"
            )
            type, pos = pos, type
        pos = pos.floor()
        if not isinstance(type, Block):
            type = Block(type)
        mc_version = self._server.get_mc_version()
        if mc_version and mc_version < (1, 20, 5):
            nbt = NBT({"Item": {"id": type.type, "Count": f"{int(amount)}b"}})
        else:
            nbt = NBT({"Item": {"id": type.type, "Count": int(amount)}})
            data = type.getData()
            if data:
                nbt["Item"]["components"] = data.asCompound()
        self.runCommand(f"summon item {pos.x} {pos.y} {pos.z} {nbt}")

    def getEntities(
        self, type: str | EntityType | None = None, only_spawnable: bool = True
    ) -> list[entity.Entity]:
        """Get all (loaded) entities in the world.
        If a `type` is provided, only entities of that type are returned.
        By default only entities of types that could be spawned using :func:`spawnEntity` are returned.
        To get all entities (except players) set ``only_spawnable=False``, which will also return non-spawnable entities such as e.g. ``"falling_block"`` or ``"dropped_item"``.

        :param type: if provided returns only entities of that type, returns all types if None, defaults to None
        :type type: str | EntityType | None, optional
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
        type: str | EntityType | None = None,
        only_spawnable: bool = True,
    ) -> list[entity.Entity]:
        """Equivalent to :func:`getEntities`, however, is filtered to only return entities within `distance` around `pos`. Is more efficient that filtering the list manually.

        :param pos: position around which the entities are returned
        :type pos: Vec3
        :param distance: the maximum distance entities returned have around `pos`
        :type distance: float
        :param type: if provided returns only entities of that type, returns all types if None, defaults to None
        :type type: str | EntityType | None, optional
        :param only_spawnable: if False, will also return non-spawnable entities, defaults to True
        :type only_spawnable: bool, optional
        :return: list of (loaded and filtered) entities in the world closer than `distance` to `pos`
        :rtype: list[entity.Entity]
        """
        entities = self._fetch_entities(not only_spawnable, True, type if type else "")
        return [e for e in entities if pos.distance(e.pos) <= distance]

    def removeEntities(self, type: str | EntityType | None = None) -> None:
        """Remove all entities (except players) from the world, they do not drop anything.
        If `type` is provided remove only entities of that type.

        :param type: if provided removes only entities of that type, otherwise remove all entities, defaults to None
        :type type: str | EntityType | None, optional
        """
        # TODO: support natively
        if type is None:
            self.runCommand("tp @e[type=!player] 0 -50000 0")
            self.runCommand("kill @e[type=!player]")
        elif isinstance(type, EntityType):
            self.runCommand(f"tp @e[type={type.type}] 0 -50000 0")
            self.runCommand(f"kill @e[type={type.type}]")
        elif isinstance(type, str):
            self.runCommand(f"tp @e[type={type}] 0 -50000 0")
            self.runCommand(f"kill @e[type={type}]")
        else:
            raise TypeError("Type should be of type str")


class World(_DefaultWorld, _SharedBase, _HasServer):
    """Manipulating the world is the heart piece of the entire library.
    With this you can query blocks and world features and set them in turn, as well as finding and spawning entities in the world.
    This allows building on the server quickly and precisely with only a few commands.
    Note that all commands of :class:`World` will only manipulate that world, for example, :func:`getEntities` will *only* return entities in *this* world.

    Do not instantiate the :class:`World` class directly but use one of the following methods instead:

    .. code-block:: python

       worlds = mc.worlds
       world = mc.overworld
       world = mc.nether
       world = mc.end
       someotherworld = mc.getWorldByKey("mod_namespace:world_key")

    Once you have your world you can use it in a multitude of ways:

    .. code-block:: python

       world.pvp = False  # disable pvp only in this world
       ground_pos = world.getHeighestPos(0, 0)  # get position of heighest ground at origin
       block = world.getBlock(ground_pos)  # get the block type there
       world.setBlock("diamond_block", ground_pos)  # replace that block at location with diamond
       # set every second block in a line along the x axis to emerald
       world.setBlockList("emerald_block", [ground_pos.up(2).east(i) for i in range(0,20,2)])
       # set a 10 x 10 x 10 oak plank block 50 blocks above ground
       world.setBlockCube("oak_planks", ground_pos.up(50), ground_pos.up(50) + 9)
       sheep = world.spawnEntity("sheep", ground_pos.up(1))  # spawn a sheep on that block
       entities = world.getEntities()  # get all (loaded) entities
       # get all  (loaded) entities around origin highest block in 20 block radius
       entities = world.getEntitiesAround(ground_pos, 20)
       world.removeEntities("sheep")  # remove all (loaded) sheep
       # copy all blocks between those two points (inclusive)
       blocks = world.copyBlockCube(Vec3(0,0,0), Vec3(5,5,5))
       # paste back the copied blocks 20 blocks above origin ground
       world.pasteBlockCube(blocks, ground_pos.up(20))
       world.setBed(ground_pos.up(1))  # place a bed on top of diamond block

    .. note::

       When using the world functions on :class:`Minecraft` (``mc``) directly the 'default' world is used. The default world is defined by the server as the first world loaded by the server, which is usually the overworld.
       If you want to affect a specific world, use :class:`World` classes instead, such as ``mc.overworld``, ``mc.nether`` or ``mc.end``.
    """

    def __init__(self, server: _ServerInterface, key: str, name: str) -> None:
        super().__init__(server)
        self._key = key
        self._name = name

    @property
    def _pb_world(self) -> pb.World:
        return pb.World(name=self.name)

    @property
    def key(self) -> str:
        """The key/id of this world, e.g., ``"minecraft:overworld"`` or ``"minecraft:the_nether"``"""
        return self._key

    @property
    def name(self) -> str:
        """The name of the folder/namespace the world resides in, e.g., ``"world"`` or ``"world_the_end"``"""
        return self._name

    @property
    def pvp(self) -> bool:
        """True if pvp is enabled in this world. Can be set to enable or disable pvp in only this world."""
        response = self._server.stub.accessWorlds(pb.WorldRequest(worlds=[self._pb_world]))
        raise_on_error(response.status)
        return response.worlds[0].info.pvp

    @pvp.setter
    def pvp(self, value: bool) -> None:
        response = self._server.stub.accessWorlds(
            pb.WorldRequest(worlds=[pb.World(name=self.name, info=pb.WorldInfo(pvp=value))])
        )
        raise_on_error(response.status)

    def __repr__(self) -> str:
        # return f"{self.__class__.__name__}(name={self.name}, key={self.key})"
        return f"{self.__class__.__name__}(key={self.key})"

    def runCommand(self, command: str) -> None:
        """Run the `command` as if it was typed in chat as ``/``-command and executed in this specific world/dimension.
        Returns immediately without waiting for the command to finish executing.

        .. code-block:: python

           world.runCommand("kill @e")  # kill all loaded entities in this world

        :param command: the command without the slash ``/``
        :type command: str
        """
        command = f"execute in {self.key} run " + command
        return super().runCommand(command)

    def runCommandBlocking(self, command: str) -> str:
        """Run the `command` as if it was typed in chat as ``/``-command and executed in this specific world/dimension.
        Blocks and waits for the command to finish executing returning the command's result.

        .. code-block:: python

           response = world.runCommandBlocking("locate biome mushroom_fields")

        .. caution::

           The plugin that is built against the ``spigot-Bukkit API`` does *not* fully support the return of command output,
           specifically the capturing of output of vanilla commands.
           Instead it only supports the capturing of Bukkit commands, which can be seen with ``mc.runCommandBlocking("help Bukkit").split("\\n")``

        :param command: the command without the slash ``/``
        :type command: str
        :return: the console output of the command
        :rtype: str
        """
        command = f"execute in {self.key} run " + command
        return super().runCommandBlocking(command)
