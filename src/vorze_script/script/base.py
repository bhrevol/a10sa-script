"""Base script module."""
from dataclasses import dataclass
from typing import Iterable
from typing import Iterator
from typing import MutableSequence
from typing import Optional

from sortedcontainers import SortedList

from ..command import BaseCommand


@dataclass
class ScriptCommand:
    """Timed script command.

    Attributes:
        offset: Offset from start of script in milliseconds.
        cmd: Command.
    """

    offset: int
    cmd: BaseCommand


class BaseScript(MutableSequence[ScriptCommand]):
    """Base command script."""

    def __init__(
        self,
        commands: Optional[Iterable[ScriptCommand]] = None,
    ):
        """Construct a script.

        Arguments:
            commands: Initial set of commands for this script.
        """
        self.commands = SortedList(commands, key=lambda cmd: cmd.offset)

    def __getitem__(self, key: int) -> ScriptCommand:
        return self.commands[key]

    def __setitem__(self, key: int, value: ScriptCommand) -> None:
        raise NotImplementedError

    def __delitem__(self, key: int) -> None:
        del self.commands[key]

    def __len__(self) -> int:
        return len(self.commands)

    def __iter__(self) -> Iterator[ScriptCommand]:
        return iter(self.commands)

    def __reversed__(self) -> Iterator[ScriptCommand]:
        return reversed(self.commands)

    def insert(self, command: ScriptCommand):
        """Add a command to this script.

        Commands will be inserted in the proper location based on time offset.

        Arguments:
            command: Command to insert.
        """
        self.commands.add(command)

    def reverse(self) -> None:
        """Raise not-implemented error.

        In place reversal is not supported (script will always be sorted).
        """
        raise NotImplementedError

    def seek_iter(self, offset: int) -> Iterator[ScriptCommand]:
        """Return an iterator for commands starting at the specified offset.

        Arguments:
            offset: Time offset in milliseconds.

        Returns:
            Command iterator.
        """
        return self.commands.irange_key(offset)
