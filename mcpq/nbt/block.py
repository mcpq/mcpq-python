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

    # def withData(self, data: dict[str, bool | int | str] | str | ComponentData) -> Block:
    #     return Block(self.id).addData(data)
