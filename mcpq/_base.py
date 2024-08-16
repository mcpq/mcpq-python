from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ._proto import MinecraftStub
from ._proto import minecraft_pb2 as pb
from .exception import raise_on_error

if TYPE_CHECKING:
    from .entity import Entity
    from .player import Player


class _HasStub:
    """General, server-wide commands and settings."""

    def __init__(self, stub: MinecraftStub) -> None:
        if not isinstance(stub, MinecraftStub):
            raise TypeError(f"Argument 'stub' must be of type MinecraftStub was '{type(stub)}'")
        self._stub = stub

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + "("
            + ", ".join(
                f"{var}={val!r}" for var, val in self.__dict__.items() if not var.startswith("_")
            )
            + ")"
        )

    def runCommand(self, command: str) -> None:
        """Run the `command` as if it was typed in chat as ``/``-command.
        The command is run with the highest possible permission and no other modifiers.

        .. code-block:: python

           mc.runCommand("kill @e")
           mc.runCommand("gamerule doDaylightCycle false")

        :param command: the command without the slash ``/``
        :type command: str
        """
        response = self._stub.runCommand(pb.CommandRequest(command=command))
        raise_on_error(response)


class _EntityProvider(ABC):
    @abstractmethod
    def _get_or_create_entity(self, entity_id: str) -> Entity:
        raise NotImplementedError


class _PlayerProvider(ABC):
    @abstractmethod
    def _get_or_create_player(self, name: str) -> Player:
        raise NotImplementedError
