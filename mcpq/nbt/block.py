from __future__ import annotations

from typing import Mapping

from ._types import ComponentData


# TODO: use BlockKey for materials/block types (add nbt as well)
class Block(str):
    """:class:`Block` is a subtype of python `str`, so supports all standard string operations.
    Additionally, it supports methods to manipulate block :class:`ComponentData` in component-format_ and type and namespace parts of a block.

    .. _component-format: https://minecraft.wiki/w/Data_component_format

    .. note::

       While the class is called `Block` it can also be used for items, item stacks and even entities in commands or for serialization.`

    .. code::

       from mcpq import Minecraft, Vec3, Block
       mc = Minecraft()

       # you can turn a normal string into a block like so:
       block = Block("namespace:type[componentkey1=componentvalue1]")
       block = Block("acacia_stairs[facing=east]")  # namespace 'minecraft:' can be ommited
       print(block)
       # >>> "acacia_stairs[facing=east]"  # note, 'Block()' is not shown, direct string

       # block comparison and ordering is always done on the id:
       bs = [Block("minecraft:stone"), Block("other:block_name"), Block("air"), Block("another:type")]
       print(sorted(bs))
       # >>> ['another:type', 'air', 'stone', 'other:block_name']
       # sorted first by namespace: 'another', 'minecraft' and 'other'
       # and then by type, so 'air' < 'stone'

       # similarly comparison to strings with or without namespace will succeed
       # while component data is ignored for normal comparison
       block = Block("acacia_stairs[facing=east]")
       assert block == "acacia_stairs" and block == "minecraft:acacia_stairs"
       # if you want to compare component data as well, use equals()
       block.equals("acacia_stairs")  # false
       block.equals("acacia_stairs[half=top,facing=east]")  # false
       block.equals("acacia_stairs[facing=east]")  # true
       block.equals('acacia_stairs[facing="east"]')  # true


    """

    def __repr__(self) -> str:
        if "[" in self:
            return f"'{self.type}{self.datastr}'"
        return f"'{self.type}'"

    # TODO: repr/str

    def __eq__(self, value: object) -> bool:
        # TODO: is this good equal?
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
        """Namespace and type as namespace:type string.

        :return: the string namespace:type of given block
        :rtype: str
        """
        rest = self[: self.index("[")] if "[" in self else self[:]
        if ":" in rest:
            return rest
        return "minecraft:" + rest

    @property
    def type(self) -> str:
        """The type string of namespace:type without the 'minecraft:' namespace but including non-vanilla namespaces.

        :return: the string type of minecraft:type of given block or the id if non-vanilla block
        :rtype: str
        """
        if "[" in self:
            return self[: self.index("[")].removeprefix("minecraft:")
        return self.removeprefix("minecraft:")

    @property
    def namespace(self) -> str:
        """The namespace string of namespace:type. Is 'minecraft' if block is vanilla.

        :return: the string namespace of namespace:type of given block
        :rtype: str
        """
        if ":" in self:
            return self[: self.index(":")]
        return "minecraft"

    @property
    def datastr(self) -> str:
        """The data/components string of given block in form '[component1=value1,component2=value2]'.
        Looks like ``'[]'`` if this block has no component data.

        :return: the string data/components of namespace:type[component1=value1,...] of given block
        :rtype: str
        """
        if "[" in self:
            return self[self.index("[") :]
        return "[]"

    @property
    def hasData(self) -> bool:
        # TODO: remove white spaces?
        return len(self.datastr) > 2

    def asBlockStateForItem(self) -> Block:
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
        """Parse and return :class:`datastr` as :class:`ComponentData`.
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
        data: dict[str, bool | int | str] | str | ComponentData | Block | None = None,
    ) -> Block:
        """Return a new :class:`Block` with the `id` of this block but replace the :class:`ComponentData` of the form ``[key1=value1,key2=value2]`` on this block with the given data.
        The given data may have the form of a dict, :class:`ComponentData`, :class:`Block` or string and will be parsed and/or converted as required.
        If `data` is None the component data is deleted instead.

        .. code::

           from mcpq import Block
           b = Block("acacia_stairs[facing=east]")
           wb = Block("other_block[waterlogged=true]")
           waterstairs = b.withData({"waterlogged": True})  # convert to component data
           waterstairs = b.withData("[waterlogged=true]")  # parse string and use component data
           waterstairs = b.withData(wb)  # id of b + data of wb
           waterstairs = b.withData(wb.getData())  # use data of wb
           print(waterstairs)  # in all 4 cases: ('facing=east' is overwritten)
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

           from mcpq import Block
           b = Block("acacia_stairs[facing=east,half=top]")
           wb = Block("other_block[waterlogged=true,half=bottom]")
           newstairs = b.withMergeData({"waterlogged": True, "half": "bottom"})  # convert to component data
           newstairs = b.withMergeData("[waterlogged=true,half=bottom]")  # parse string and use component data
           newstairs = b.withMergeData(wb)  # id of b + merge data of wb
           newstairs = b.withMergeData(wb.getData())  # merge data of wb
           print(newstairs)  # in all 4 cases:
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
        elif isinstance(data, str):
            d = ComponentData.parse(data)
        elif isinstance(data, Mapping):
            d = ComponentData(data)
        else:
            raise ValueError(
                f"Unknown data type {type(data).__name__}, expected dict, str, Block or ComponentData"
            )

        return self.withData(self.getData() | d)
