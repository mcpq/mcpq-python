from __future__ import annotations

from ._abc import _ServerInterface
from ._proto import minecraft_pb2 as pb
from .exception import raise_on_error


class _HasServer:
    def __init__(self, server: _ServerInterface) -> None:
        self._server = server


class _SharedBase(_HasServer):
    """General, server-wide commands and settings."""

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
        Returns immediately without waiting for the command to finish executing.

        .. code-block:: python

           mc.runCommand("kill @e")
           mc.runCommand("gamerule doDaylightCycle false")

        :param command: the command without the slash ``/``
        :type command: str
        """
        response = self._server.stub.runCommandWithOptions(pb.CommandRequest(command=command))
        raise_on_error(response.status)

    def runCommandBlocking(self, command: str) -> str:
        """Run the `command` as if it was typed in chat as ``/``-command and return the response from the server.
        The command is run with the highest possible permission and no other modifiers.
        Blocks and waits for the command to finish executing returning the command's result.

        .. code-block:: python

           response = mc.runCommand("locate biome mushroom_fields")

        .. caution::

           The plugin that is built against the ``spigot-Bukkit API`` does *not* fully support the return of command output,
           specifically the capturing of output of vanilla commands.
           Instead it only supports the capturing of Bukkit commands, which can be seen with ``mc.runCommandBlocking("help Bukkit").split("\\n")``

        :param command: the command without the slash ``/``
        :type command: str
        :return: the console output of the command
        :rtype: str
        """
        response = self._server.stub.runCommandWithOptions(
            pb.CommandRequest(command=command, blocking=True, output=True)
        )
        raise_on_error(response.status)
        return response.output
