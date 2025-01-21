"""Base script module."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import BinaryIO
from typing import Generic
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import MutableSequence
from typing import TypeVar
from typing import overload

from sortedcontainers import SortedList
from typing import TypeAlias

from ..command import BaseCommand


_T = TypeVar("_T", bound=BaseCommand)


@dataclass
class ScriptCommand(Generic[_T]):
    """Timed script command.

    Attributes:
        offset: Offset from start of script in milliseconds.
        cmd: Command.
    """

    offset: int
    cmd: _T


_SC: TypeAlias = ScriptCommand


class BaseScript(MutableSequence[_SC[_T]]):
    """Base command script."""

    def __init__(
        self,
        commands: Iterable[_SC[_T]] | None = None,
        **kwargs: Any,
    ):
        """Construct a script.

        Arguments:
            commands: Initial set of commands for this script.
            kwargs: Additional kwargs.
        """
        self.commands = SortedList(commands, key=lambda cmd: cmd.offset)

    @overload
    def __getitem__(self, key: int) -> _SC[_T]:
        ...

    @overload
    def __getitem__(self, key: slice) -> MutableSequence[_SC[_T]]:
        ...

    def __getitem__(self, key: int | slice) -> _SC[_T] | MutableSequence[_SC[_T]]:
        return self.commands[key]

    def __setitem__(
        self,
        key: int | slice,
        value: _SC[_T] | Iterable[_SC[_T]],
    ) -> None:
        raise NotImplementedError

    def __delitem__(self, key: int | slice) -> None:
        del self.commands[key]

    def __len__(self) -> int:
        return len(self.commands)

    def __iter__(self) -> Iterator[_SC[_T]]:
        return iter(self.commands)

    def __reversed__(self) -> Iterator[_SC[_T]]:
        return reversed(self.commands)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BaseScript) and self.commands == other.commands

    def insert(self, index: int, command: _SC[_T]) -> None:
        """Raise not-implemented error (use add())."""
        raise NotImplementedError

    def add(self, command: _SC[_T]) -> None:
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

    def seek_iter(self, offset: int) -> Iterator[_SC[_T]]:
        """Return an iterator for commands starting at the specified offset.

        Arguments:
            offset: Time offset in milliseconds.

        Returns:
            Command iterator.
        """
        return self.commands.irange_key(offset)


class SerializableScript(BaseScript[_T]):
    """A command script which can be serialized."""

    @abstractmethod
    def dump(self, fp: BinaryIO) -> None:
        """Serialize script to file.

        Arguments:
            fp: A file-like object opened for writing.
        """

    @classmethod
    @abstractmethod
    def load(cls, fp: BinaryIO) -> "SerializableScript[_T]":
        """Deserialize script from file.

        Arguments:
            fp: A file-like object opened for reading.
        """
