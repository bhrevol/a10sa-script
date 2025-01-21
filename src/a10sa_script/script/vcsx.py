"""LPEG/Afesta VCSX script module."""
from abc import abstractmethod
from typing import Any
from typing import BinaryIO
from typing import ClassVar
from collections.abc import Iterable

from ..command.vorze import VorzeLinearCommand
from ..command.vorze import VorzeRotateCommand
from ..command.vorze import VorzeVibrateCommand
from ..exceptions import ParseError
from ..utils import to_u32
from ..utils import to_uint
from .base import SerializableScript
from .vorze import _SC
from .vorze import _T
from .vorze import VorzeScriptCommand


class VCSXScript(SerializableScript[_T]):
    """Generic LPEG VCSX script.

    Note:
        LPEG VCSX is a container for Vorze's binary BLE command format.
    """

    VCSX_MAGIC: ClassVar[bytes]
    VCSX_DEFAULT_VERSION: ClassVar[bytes]

    def __init__(
        self,
        commands: Iterable[_SC[_T]] | None = None,
        version: bytes | None = None,
        **kwargs: Any,
    ):
        """Construct a script.

        Arguments:
            commands: Initial set of commands for this script.
            version: VCSX version.
            kwargs: Additional kwargs.
        """
        super().__init__(commands, **kwargs)
        self.version = version or self.VCSX_DEFAULT_VERSION

    @classmethod
    @abstractmethod
    def _command_cls(cls) -> type[_T]:
        """Return command class for this script."""

    def dump(self, fp: BinaryIO) -> None:
        """Serialize script to file.

        Arguments:
            fp: A file-like object opened for writing.
        """
        fp.write(self.VCSX_MAGIC + self.version + to_u32(len(self)))
        for cmd in self.commands:
            fp.write(to_u32(cmd.offset) + cmd.cmd.to_vcsx())

    @classmethod
    def load(cls, fp: BinaryIO) -> "VCSXScript[_T]":
        """Deserialize script from file.

        Arguments:
            fp: A file-like object opened for reading.

        Returns:
            Loaded command script.

        Raises:
            ParseError: A CSV parsing error occured.
        """
        try:
            magic = fp.read(len(cls.VCSX_MAGIC))
            if magic != cls.VCSX_MAGIC:
                raise ParseError("Invalid VCSX header")
            version = fp.read(len(cls.VCSX_DEFAULT_VERSION))
            size = to_uint(fp.read(4))
            cmd_cls = cls._command_cls()
            return cls(
                (
                    VorzeScriptCommand(
                        to_uint(fp.read(4)),
                        cmd_cls.from_vcsx(fp.read(cmd_cls.vcsx_size())),
                    )
                    for i in range(size)
                ),
                version=version,
            )
        except (OSError, ValueError) as e:
            raise ParseError("Failed to parse file as VCSX data.") from e


class VCSXOnaRhythmScript(VCSXScript[VorzeVibrateCommand]):
    """VCSX OnaRhythm script."""

    VCSX_MAGIC = b"VCSX\x01Vorze_OnaRhythm\x00"
    VCSX_DEFAULT_VERSION = b"\x01\x42"

    @classmethod
    def _command_cls(cls) -> type[VorzeVibrateCommand]:
        """Return command class for this script."""
        return VorzeVibrateCommand


class VCSXPistonScript(VCSXScript[VorzeLinearCommand]):
    """VCSX Piston script."""

    VCSX_MAGIC = b"VCSX\x01Vorze_Piston\x00"
    VCSX_DEFAULT_VERSION = b"\x02\x57\x42"

    @classmethod
    def _command_cls(cls) -> type[VorzeLinearCommand]:
        """Return command class for this script."""
        return VorzeLinearCommand


class VCSXCycloneScript(VCSXScript[VorzeRotateCommand]):
    """VCSX Cyclone SA script."""

    VCSX_MAGIC = b"VCSX\x01Vorze_CycloneSA\x00"
    VCSX_DEFAULT_VERSION = b"\x01\x42"

    @classmethod
    def _command_cls(cls) -> type[VorzeRotateCommand]:
        """Return command class for this script."""
        return VorzeRotateCommand
