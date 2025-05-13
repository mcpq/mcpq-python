from __future__ import annotations

from typing import Mapping

from ._types import ComponentData, NbtCompound


class Block(str):
    """:class:`Block` is a subtype of python `str`, so supports all standard string operations.
    Additionally, it supports methods to manipulate block :class:`ComponentData` in component-format_ and name and namespace parts of a block.

    .. _component-format: https://minecraft.wiki/w/Data_component_format

    .. note::

       While the class is called `Block` it can also be used for items, item stacks and even entities in commands or for serialization.

    .. code::

       from mcpq import Minecraft, Vec3, Block
       mc = Minecraft()

       # you can turn a normal string into a block like so:
       block = Block("namespace:name[componentkey1=componentvalue1]")
       block = Block("acacia_stairs[facing=east]")  # namespace 'minecraft:' can be ommited
       print(block)
       # >>> "acacia_stairs[facing=east]"  # note, 'Block()' is not shown, direct string

       # block comparison and ordering is always done on the id:
       bs = [Block("minecraft:stone"), Block("other:block_name"), Block("air"), Block("another:name")]
       print(sorted(bs))
       # >>> ['another:name', 'air', 'stone', 'other:block_name']
       # sorted first by namespace: 'another', 'minecraft' and 'other'
       # and then by name, so 'air' < 'stone'

       # similarly comparison to strings with or without namespace will succeed
       # while component data is ignored for normal comparison
       block = Block("acacia_stairs[facing=east]")
       assert block == "acacia_stairs" and block == "minecraft:acacia_stairs"
       # if you want to compare component data as well, use equals()
       block.equals("acacia_stairs")  # false
       block.equals("acacia_stairs[half=top,facing=east]")  # false
       block.equals("acacia_stairs[facing=east]")  # true
       block.equals('acacia_stairs[facing="east"]')  # true

    Note that constructing a :class:`Block` using the ``Block(...)`` constructor does *not* perform any checking at all, such that invalid or unknown blocks could be constructed.
    To actually check if the type of the block exists on the server, use the :class:`MaterialFilter` class and use :func:`withData` and :func:`withMergeData` for setting component data on blocks:

    .. code::

       from mcpq import Minecraft
       mc = Minecraft()

       # returns the block and raises an error if the block does not exist
       block = mc.blocks.getById("acacia_stairs")
       # similarly, if you want "any wool block" you could use
       wool_block = mc.blocks.endswith("wool").first()  # returns None if no block exists

       # afterwards you can set the component data directly
       waterlogged_block = block.withData({"waterlogged": True})

    Checkout :func:`withData` and :func:`withMergeData` for more examples regarding component data.
    """

    def __new__(cls, value):
        if isinstance(value, str):
            return super().__new__(cls, value.removeprefix("minecraft:"))
        return super().__new__(cls, str(value).removeprefix("minecraft:"))

    def __repr__(self) -> str:
        if "[" in self:
            return f"'{self.type}{self.datastr}'"
        return f"'{self.type}'"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Block):
            return self.id == value.id
        if isinstance(value, str):
            return self.id == value or self.type == value or super().__eq__(value)
        return super().__eq__(value)

    def __ne__(self, value: object) -> bool:
        return not self == value

    def __le__(self, value: str) -> bool:
        if isinstance(value, Block):
            return self.id <= value.id
        return self.id <= value

    def __ge__(self, value: str) -> bool:
        if isinstance(value, Block):
            return self.id >= value.id
        return self.id >= value

    def __lt__(self, value: str) -> bool:
        if isinstance(value, Block):
            return self.id < value.id
        return self.id < value

    def __gt__(self, value: str) -> bool:
        if isinstance(value, Block):
            return self.id > value.id
        return self.id > value

    @property
    def id(self) -> str:
        """The full ``namespace:name`` of the block as string.

        :return: the string ``namespace:name`` of given block (including "minecraft" prefix)
        :rtype: str
        """
        rest = self[: self.index("[")] if "[" in self else self[:]
        if ":" in rest:
            return rest
        return "minecraft:" + rest

    @property
    def type(self) -> str:
        """Similar to the :attr:`.id` but excluding the "minecraft" namespace but including non-vanilla namespaces. This is a valid block id as the "minecraft" namespace is assumed by default if no namespace is provided.

        :return: the block :attr:`.name` of ``namespace:name`` of given vanilla block or the :attr:`.id` of non-vanilla block
        :rtype: str
        """
        # prefix removed in __new__
        if "[" in self:
            return self[: self.index("[")]
        return str(self)

    @property
    def name(self) -> str:
        """The name string of ``namespace:name`` excluding the namespace.

        .. caution::

           The returned string might not be a valid block id without its namespace if the namespace is something other than "minecraft"!
           Use :attr:`.type` instead, which will remove the "minecraft" prefix but not other namespaces.

        :return: the string type of ``namespace:name`` of given block without the namespace
        :rtype: str
        """
        t = self.type
        if ":" in t:
            return t[t.index(":") :]
        return t

    @property
    def namespace(self) -> str:
        """The namespace string of ``namespace:name``. This returns "minecraft" for vanilla blocks.

        :return: the string namespace of ``namespace:name`` of given block
        :rtype: str
        """
        if ":" in self:
            return self[: self.index(":")]
        return "minecraft"

    @property
    def datastr(self) -> str:
        """The data/components string of given block in form '[component1=value1,component2=value2]'.
        Looks like ``'[]'`` if this block has no component data.

        :return: the string data/components of ``namespace:name[component1=value1,...]`` of given block
        :rtype: str
        """
        if "[" in self:
            return self[self.index("[") :]
        return "[]"

    @property
    def hasData(self) -> bool:
        """Check if the string has component data, but does not actually parse the data. For that use :func:`getData`."""
        # TODO: remove white spaces?
        return len(self.datastr) > 2

    def asBlockStateForItem(self) -> Block:
        """Return the current Block with its data as a ``block_state`` component. This can be used to give players placeable blocks as items with certain component data.

        .. code::

           from mcpq import Minecraft
           mc = Minecraft()
           b = mc.blocks.endswith("_stairs").first().withData({"waterlogged": True})
           mc.getPlayer().giveItems(b.asBlockStateForItem())  # give player a waterlogged stair to place
        """
        nd = ComponentData()
        state = nd.get_or_create_nbt("block_state")
        # TODO: block_state seemingly only accepts string type values...
        for key, val in self.getData().items():
            if isinstance(val, bool):
                val = str(val).lower()
            state.string[key] = val
        return Block(self.type + str(nd))

    def equals(self, value: object) -> bool:
        """Check if `value` equals self, i.e., compare id and component data.
        Component data will be parsed and compared via equality for this.

        .. note::

           Normal equality ``==`` will only compare id for checking against strings.

        :param value: the string or :class:`Block` to compare against
        :type value: object
        :return: whether the supplied Block has the same id and component data
        :rtype: bool
        """
        if isinstance(value, str):
            value = Block(value)
        if isinstance(value, Block):
            return self.id == value.id and self.getData() == value.getData()
        return super().__eq__(value)

    def getData(self) -> ComponentData:
        """Parse and return :attr:`datastr` as :class:`ComponentData`.
        Is equivalent to ``ComponentData.parse(self.datastr)``.

        :return: this block's parsed string component data
        :rtype: ComponentData
        """
        return ComponentData.parse(self.datastr)

    def withId(self, type_id: str | Block) -> Block:
        """Return a new :class:`Block` with the given `type_id` as its id but with the (copied) :class:`ComponentData` of this block.

        .. code::

           from mcpq import Block
           b = Block("acacia_stairs[waterlogged=true]")
           sb = Block("oak_sign")
           watersign = b.withId("oak_sign")
           watersign = b.withId(sb)  # replace the id of b with id of sb
           print(watersign)  # in both cases:
           # >>> "oak_sign[waterlogged=true]"

        :param type_id: the (block) id that should replace this block's
        :type type_id: str | Block
        :return: a new block with this block's component data and the new id
        :rtype: Block
        """
        dstr = self.datastr if self.hasData else ""
        if isinstance(type_id, Block):
            return Block(type_id.type + dstr)
        elif isinstance(type_id, str):
            return Block(Block(type_id).type + dstr)
        else:
            raise ValueError(f"Unknown id type {type(type_id).__name__}, expected str or Block")

    def withData(
        self,
        data: dict[str, bool | int | str]
        | str
        | ComponentData
        | NbtCompound
        | Block
        | None = None,
    ) -> Block:
        """Return a new :class:`Block` with the `id` of this block but replace the :class:`ComponentData` of the form ``[key1=value1,key2=value2]`` on this block with the given data.
        The given data may have the form of a dict, :class:`ComponentData`, :class:`Block` or string and will be parsed and/or converted as required.
        If `data` is None the component data is deleted instead.

        .. code::

           from mcpq import Block, NBT
           b = Block("acacia_stairs[facing=east]")
           waterstairs = b.withData({"waterlogged": True})  # convert to component data
           waterstairs = b.withData("[waterlogged=true]")  # parse string and use component data
           wb = Block("other_block[waterlogged=true]")
           waterstairs = b.withData(wb)  # id of b + data of wb
           waterstairs = b.withData(wb.getData())  # use data of wb
           nbt = NBT({"waterlogged": True})
           waterstairs = b.withData(nbt.asComponentData())  # convert nbt to component data
           print(waterstairs)  # in all 5 cases: ('facing=east' is overwritten)
           # >>> "acacia_stairs[waterlogged=true]"

           # to delete the component data
           print(b.withData())
           # >>> "acacia_stairs"

        :param data: component data that should replace this block's, defaults to None
        :type data: dict[str, bool  |  int  |  str] | str | ComponentData | Block | None, optional
        :return: a new block with this block's id and the new component data
        :rtype: Block
        """
        if data is None:
            return Block(self.type)
        elif isinstance(data, Block):
            return Block(self.type + (data.datastr if data.hasData else ""))
        elif isinstance(data, ComponentData):
            return Block(self.type + (str(data) if data else ""))
        elif isinstance(data, NbtCompound):
            return Block(self.type + (str(data.asComponentData()) if data else ""))
        elif isinstance(data, str):
            d = ComponentData.parse(data)
            return Block(self.type + (str(d) if d else ""))
        elif isinstance(data, Mapping):
            d = ComponentData(data)
            return Block(self.type + (str(d) if d else ""))
        else:
            raise ValueError(
                f"Unknown data type {type(data).__name__}, expected dict, str, Block, ComponentData or None"
            )

    def withMergeData(
        self, data: dict[str, bool | int | str] | str | ComponentData | Block
    ) -> Block:
        """Return a new :class:`Block` with the `id` of this block but merge the given :class:`ComponentData` of the form ``[key1=value1,key2=value2]`` onto the one on this block.
        The given data may have the form of a dict, :class:`ComponentData`, :class:`Block` or string and will be parsed and/or converted as required.

        .. code::

           from mcpq import Block, NBT
           b = Block("acacia_stairs[facing=east,half=top]")
           newstairs = b.withMergeData({"waterlogged": True, "half": "bottom"})  # convert to component data
           newstairs = b.withMergeData("[waterlogged=true,half=bottom]")  # parse string and use component data
           wb = Block("other_block[waterlogged=true,half=bottom]")
           newstairs = b.withMergeData(wb)  # id of b + merge data of wb
           newstairs = b.withMergeData(wb.getData())  # merge data of wb
           nbt = NBT({"waterlogged": True, "half": "bottom"})
           newstairs = b.withMergeData(nbt.asComponentData())  # convert nbt to component data
           print(newstairs)  # in all 5 cases:
           # >>> 'acacia_stairs[facing="east",half="bottom",waterlogged=true]'

        :param data: component data that should be merged onto this block's
        :type data: dict[str, bool  |  int  |  str] | str | ComponentData | Block
        :return: a new block with this block's id and data with the new component data merged on top of it
        :rtype: Block
        """
        if isinstance(data, Block):
            d = data.getData()
        elif isinstance(data, ComponentData):
            d = data
        elif isinstance(data, NbtCompound):
            d = data.asComponentData()
        elif isinstance(data, str):
            d = ComponentData.parse(data)
        elif isinstance(data, Mapping):
            d = ComponentData(data)
        else:
            raise ValueError(
                f"Unknown data type {type(data).__name__}, expected dict, str, Block or ComponentData"
            )

        return self.withData(self.getData() | d)
