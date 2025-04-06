"""Funjack funscript script module."""
import io
import json
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any, BinaryIO
from collections.abc import Iterator

from loguru import logger

from ..command import GenericLinearCommand, VorzeLinearCommand
from ..exceptions import ParseError
from .base import BaseScript, ScriptCommand, SerializableScript
from .vorze import VorzeLinearScript, VorzeScriptCommand


@dataclass(frozen=True)
class _Action:
    at: int
    pos: int


class FunscriptScript(SerializableScript[GenericLinearCommand]):
    """Funscript linear (Piston) script.

    Commands are stored as native Buttplug/funscript vector actions.

    Arguments:
        inverted: True if this script starts at max position instead of min position.
            Inversion is only applied on serialization, internal Buttplug vector positions
            are never inverted.

    Note:
        Loss of resolution will occur when converting to/from Vorze script format due to
        the conversion between Buttplug duration and Piston speed. Round trip conversion
        will not result in an exact match between the original and final script.
    """

    FUNSCRIPT_VERSION = "1.0"
    OFFSET_DENOM = 1
    CONVERSION_THRESHOLD_MS = 100

    def __init__(self, *args: Any, inverted: bool = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.inverted = inverted

    @property
    def initial_position(self) -> float:
        """Return initial position for this script.

        Funjack spec defines the default position for non-inverted scripts to be the
        bottom (entrance) end of the device. For inverted scripts, it defaults to the
        opposite end of the device. Some scripts define an explicit initial position at
        time offset 0.
        """
        try:
            initial_cmd = self.commands[0]
            linear_cmd = initial_cmd.cmd
            if initial_cmd.offset == 0 and linear_cmd.duration == 0:
                return linear_cmd.position
        except IndexError:
            pass
        return 1.0 if self.inverted else 0.0

    def dump(self, fp: BinaryIO) -> None:
        """Serialize script to file.

        Arguments:
            fp: A file-like object opened for writing.
        """
        with io.TextIOWrapper(fp, newline="") as text_fp:
            data = {
                "version": self.FUNSCRIPT_VERSION,
                "inverted": self.inverted,
                "range": 90,
                "actions": [asdict(action) for action in self.actions()],
            }
            json.dump(data, text_fp)

    def actions(self) -> Iterator[_Action]:
        """Iterate over this script's commands as Funscript actions.

        Yields:
            Funscript actions in order.
        """
        pos = self.initial_position
        offset = 0
        for i, cmd in enumerate(self.commands):
            if cmd.offset != offset:
                duration = cmd.offset - offset
                if duration < 0:
                    logger.warning(
                        "Script command overrun: command at {} starts before prior action completes at {}",
                        cmd.offset,
                        offset,
                    )
                else:
                    yield _Action(
                        cmd.offset, self.vector_to_funscript(pos, self.inverted)
                    )
            linear_cmd = cmd.cmd
            offset = cmd.offset + linear_cmd.duration
            pos = linear_cmd.position
            yield _Action(offset, self.vector_to_funscript(pos, self.inverted))

    @classmethod
    def load(cls, fp: BinaryIO) -> "FunscriptScript":
        """Deserialize script from file.

        Arguments:
            fp: A file-like object opened for reading.

        Returns:
            Loaded command script.

        Raises:
            ParseError: A JSON parsing error occured.
        """
        try:
            data = json.load(fp)
        except json.JSONDecodeError as e:
            raise ParseError("Failed to parse file as funscript JSON.") from e
        inverted = data.get("inverted", False)
        commands: list[ScriptCommand[GenericLinearCommand]] = []
        offset = 0
        pos = 1.0 if inverted else 0.0
        try:
            for action in data.get("actions", []):
                at = action["at"]
                next_pos = cls.funscript_to_vector(action["pos"], inverted)
                if pos != next_pos:
                    commands.append(
                        ScriptCommand(
                            offset, GenericLinearCommand(at - offset, next_pos)
                        )
                    )
                pos = next_pos
                offset = at
        except KeyError as e:
            raise ParseError("Failed to parse file as funscript JSON.") from e
        return cls(commands, inverted=inverted)

    @staticmethod
    def vector_to_funscript(pos: float, inverted: bool = False) -> int:
        """Convert Buttplug vector position to funscript position."""
        pos = round(pos * 100)
        if inverted:
            pos = 100 - pos
        return pos

    @staticmethod
    def funscript_to_vector(pos: int, inverted: bool = False) -> float:
        """Convert funscript position to Buttplug vector position."""
        if inverted:
            pos = 100 - pos
        return pos / 100

    @classmethod
    def from_vorze(
        cls, script: BaseScript[VorzeLinearCommand], inverted: bool = False
    ) -> "FunscriptScript":
        """Convert Vorze Piston script to funscript.

        Arguments:
            script: Script to be converted.
            inverted: True if the resulting funscript should be inverted.

        Note:
            Conversion will result in loss of resolution due to the conversion between
            Buttplug duration and Piston speed.
        """
        commands: list[ScriptCommand[GenericLinearCommand]] = []
        pos = 1.0
        if not inverted:
            # Vorze scripts always start at the top of the device. Funscript defaults to
            # bottom of the device for non-inverted scripts, so we insert an explicit
            # initial position at offset 0.
            commands.append(ScriptCommand(0, GenericLinearCommand(0, pos)))
        for cmd in script.commands:
            piston_cmd = cmd.cmd
            vectors = piston_cmd.vectors(pos)
            linear_cmd = GenericLinearCommand.from_vectors(vectors)
            commands.append(ScriptCommand(cmd.offset, linear_cmd))
            pos = linear_cmd.position
        return cls(commands, inverted=inverted)

    def to_vorze(self) -> VorzeLinearScript:
        """Convert funscript to Vorze Piston script.

        Note:
            Conversion will result in loss of resolution due to the conversion between
            Buttplug duration and Piston speed. Inversion is never preserved when
            converting to Vorze Piston script (Vorze scripts always start at min
            position).
        """
        if self.inverted:
            logger.warning(
                "Converting inverted funscript, Vorze CSV will not be inverted."
            )
        pos = self.initial_position
        commands: list[VorzeScriptCommand[VorzeLinearCommand]] = []
        for i, cmd in enumerate(self.commands):
            linear_cmd = cmd.cmd
            if linear_cmd.duration:
                piston_cmd = VorzeLinearCommand.from_vectors(linear_cmd.vectors, pos)
                commands.append(VorzeScriptCommand(cmd.offset, piston_cmd))
            pos = linear_cmd.position
        return VorzeLinearScript(commands)
