from __future__ import annotations

from ._parser_wrapper import parse_component
from ._types import ComponentData


# TODO: use BlockKey for materials/block types (add nbt as well)
class Block(str):
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
        """The type string of namespace:type without the namespace.

        :return: the string type of namespace:type of given block
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
        Looks like '[]' if no data/components are on the block.

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

    # TODO: fix this and add ComponentData
    # def addData(
    #     self, data: dict[str, bool | int | str] | str | Block
    # ) -> Block:
    #     if isinstance(data, Block):
    #         data = data.dataDict
    #     elif isinstance(data, str):
    #         if len(data) < 2 or data[0] != "[" or data[-1] != "]":
    #             raise ValueError("Expected data in form: '[key1=value1,key2=value2,...]'")
    #         if " " in data:
    #             raise ValueError("Did not expect spaces in data")
    #         # TODO: more checks?
    #         data = self._parse_data(data)

    #     combined = self.dataDict | data
    #     inner = ",".join(f"{key.lower()}={str(val).lower()}" for key, val in combined.items())
    #     return Block(f"{self.type}[{inner}]")

    def getData(self) -> ComponentData:
        return parse_component(self.datastr)

    def withId(self, type_id: str | Block) -> Block:
        dstr = self.datastr if self.hasData else ""
        if isinstance(type_id, Block):
            return Block(type_id.id + dstr)
        elif isinstance(type_id, str):
            return Block(type_id)
        else:
            raise ValueError(f"Unknown id type {type(type_id)}, expected str or Block")

    def withData(
        self,
        data: dict[str, bool | int | str] | str | ComponentData | Block | None = None,
    ) -> Block:
        if data is None:
            return Block(self.id)
        elif isinstance(data, Block):
            return Block(self.id + (data.datastr if data.hasData else ""))
        elif isinstance(data, ComponentData):
            return Block(self.id + (str(data) if data else ""))
        elif isinstance(data, str):
            d = parse_component(data)
            return Block(self.id + (str(d) if d else ""))
        elif isinstance(data, dict):
            d = ComponentData(data)
            return Block(self.id + (str(d) if d else ""))
        else:
            raise ValueError(
                f"Unknown data type {type(data)}, expected dict, str, Block,  ComponentData or None"
            )
