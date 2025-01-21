"""Funjack funscript script module."""
import io
import json
from dataclasses import asdict
from dataclasses import dataclass
from typing import BinaryIO
from collections.abc import Iterator

from ..command import VorzeLinearCommand
from ..exceptions import ParseError
from .vorze import _SC
from .vorze import VorzeLinearScript
from .vorze import VorzeScriptCommand


@dataclass(frozen=True)
class _Action:
    at: int
    pos: int


class FunscriptScript(VorzeLinearScript):
    """Funscript/Vorze Piston script conversion.

    Commands are stored as Vorze Piston commands (and not Buttplug/funscript
    vector actions). This class is only suitable for converting scripts for
    Vorze Piston devices and should not be used as a general funscript
    serialization class.

    Note:
        Loss of resolution will occur upon each dump/load due to the
        conversion between Buttplug duration and Piston speed. Round trip
        conversion will not result in an exact match between the original and
        final script.
    """

    FUNSCRIPT_VERSION = "1.0"
    OFFSET_DENOM = 1
    CONVERSION_THRESHOLD_MS = 100

    def dump(self, fp: BinaryIO) -> None:
        """Serialize script to file.

        Arguments:
            fp: A file-like object opened for writing.
        """
        with io.TextIOWrapper(fp, newline="") as text_fp:
            data = {
                "version": self.FUNSCRIPT_VERSION,
                "inverted": False,
                "range": 90,
                "actions": [asdict(action) for action in self.actions()],
            }
            json.dump(data, text_fp)

    def actions(self) -> Iterator[_Action]:
        """Iterate over this script's commands as Funscript actions.

        Funscript movements consist of two actions - start point and end
        point. For movements which are close together in time offset, (i.e.
        high speed piston movements) speed->duration conversion can cause:

            - durations that are computed to end past the start of the next
              movement
            - end points that are too close in time to the next start point

        In both of these cases, we can drop the offending end point for the
        preceding action without affecting the actual movement pattern.

        The threshold used for determining whether to drop end points can be
        set via `FunscriptScript.CONVERSION_THRESHOLD_MS` (defaults to 100 ms).
        Note that this is only the threshold for dropping movement end points.
        There is no minimum restriction on the time offset difference between
        consecutive movement start points.

        Yields:
            Funscript actions in order.
        """
        pos = 1.0
        for i, cmd in enumerate(self.commands):
            start = _Action(cmd.offset, self.pos_from_vector(pos))
            duration, endpos = cmd.cmd.vectors(pos)[0]
            end = _Action(cmd.offset + duration, self.pos_from_vector(endpos))
            yield start
            try:
                next_cmd = self.commands[i + 1]
                if next_cmd.offset - end.at > self.CONVERSION_THRESHOLD_MS:
                    yield end
            except IndexError:
                yield end
            pos = endpos

    @classmethod
    def load(cls, fp: BinaryIO) -> "FunscriptScript":
        """Deserialize script from file.

        Arguments:
            fp: A file-like object opened for reading.

        Returns:
            Loaded command script.

        Raises:
            ParseError: A CSV parsing error occured.
        """
        try:
            data = json.load(fp)
        except json.JSONDecodeError as e:
            raise ParseError("Failed to parse file as funscript JSON.") from e
        inverted = data.get("inverted", False)
        commands: list[_SC[VorzeLinearCommand]] = []
        pos = 1.0
        offset = 0
        try:
            for i, action in enumerate(data.get("actions", [])):
                at = action["at"]
                newpos = cls.pos_to_vector(action["pos"], inverted)
                if newpos != pos or i == 0:
                    commands.append(
                        VorzeScriptCommand(
                            offset,
                            cls._command_cls().from_vectors(
                                [(at - offset, newpos)], pos
                            ),
                        )
                    )
                offset = at
                pos = newpos
        except KeyError as e:
            raise ParseError("Failed to parse file as funscript JSON.") from e
        return cls(commands)

    @staticmethod
    def pos_from_vector(pos: float) -> int:
        """Convert Buttplug vector position to funscript position."""
        return round(pos * 100)

    @staticmethod
    def pos_to_vector(pos: int, inverted: bool = False) -> float:
        """Convert funscript position to Buttplug vector position."""
        if inverted:
            pos = 100 - pos
        return pos / 100
