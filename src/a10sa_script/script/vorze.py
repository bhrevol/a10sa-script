"""Vorze CSV script module."""
import csv
import io
from abc import abstractmethod
from dataclasses import dataclass
from typing import BinaryIO
from typing import TypeVar

from typing import TypeAlias

from ..command.vorze import BaseVorzeCommand
from ..command.vorze import VorzeLinearCommand
from ..command.vorze import VorzeRotateCommand
from ..command.vorze import VorzeVibrateCommand
from ..exceptions import ParseError
from .base import ScriptCommand
from .base import SerializableScript


_T = TypeVar("_T", bound=BaseVorzeCommand)


@dataclass
class VorzeScriptCommand(ScriptCommand[_T]):
    """Timed Vorze script command."""


_SC: TypeAlias = VorzeScriptCommand


class VorzeScript(SerializableScript[_T]):
    """Generic Vorze CSV script.

    Note:
        Vorze CSVs time offsets are integers in tenths of a second. Internally
        we store offsets in milliseconds so loss of resolution will occur when
        converting to CSV.
    """

    OFFSET_DENOM = 100

    @classmethod
    @abstractmethod
    def _command_cls(cls) -> type[_T]:
        """Return command class for this script."""

    def dump(self, fp: BinaryIO) -> None:
        """Serialize script to file.

        Arguments:
            fp: A file-like object opened for writing.
        """
        text_fp = io.TextIOWrapper(fp, newline="", encoding="utf-8-sig")
        try:
            writer = csv.writer(text_fp)
            writer.writerows(
                (self.offset_from_ms(cmd.offset),) + tuple(cmd.cmd.to_csv())
                for cmd in self.commands
            )
        finally:
            text_fp.detach()

    @classmethod
    def load(cls, fp: BinaryIO) -> "VorzeScript[_T]":
        """Deserialize script from file.

        Arguments:
            fp: A file-like object opened for reading.

        Returns:
            Loaded command script.

        Raises:
            ParseError: A CSV parsing error occured.
        """
        try:
            reader = csv.reader(io.TextIOWrapper(fp, newline="", encoding="utf-8-sig"))
            return cls(
                VorzeScriptCommand(
                    cls.offset_to_ms(int(row[0])),
                    cls._command_cls().from_csv(row[1:]),
                )
                for row in reader
            )
        except (csv.Error, ValueError) as e:
            raise ParseError("Failed to parse file as Vorze CSV.") from e

    @classmethod
    def offset_from_ms(cls, offset_ms: int) -> int:
        """Convert millisecond time offset to Vorze CSV offsets."""
        return round(offset_ms / cls.OFFSET_DENOM)

    @classmethod
    def offset_to_ms(cls, offset_csv: int) -> int:
        """Convert Vorze CSV time offsets to millisecond offsets."""
        return offset_csv * cls.OFFSET_DENOM


class VorzeVibrateScript(VorzeScript[VorzeVibrateCommand]):
    """Vorze vibration commands script.

    Note:
        Script format for Vorze OnaRhythm devices (i.e Rocket+1D).
    """

    @classmethod
    def _command_cls(cls) -> type[VorzeVibrateCommand]:
        """Return command class for this script."""
        return VorzeVibrateCommand


class VorzeLinearScript(VorzeScript[VorzeLinearCommand]):
    """Vorze linear commands script.

    Note:
        Script format for Piston devices.
    """

    @classmethod
    def _command_cls(cls) -> type[VorzeLinearCommand]:
        """Return command class for this script."""
        return VorzeLinearCommand


class VorzeRotateScript(VorzeScript[VorzeRotateCommand]):
    """Vorze rotation commands script.

    Note:
        Shared script format for both Cyclone and UFO devices.
    """

    @classmethod
    def _command_cls(cls) -> type[VorzeRotateCommand]:
        """Return command class for this script."""
        return VorzeRotateCommand
