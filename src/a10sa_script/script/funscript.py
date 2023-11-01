"""Funjack funscript script module."""
import io
import json
from typing import BinaryIO
from typing import Dict
from typing import List
from typing import Optional

from ..command import VorzeLinearCommand
from ..exceptions import ParseError
from .vorze import _SC
from .vorze import VorzeLinearScript
from .vorze import VorzeScriptCommand


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

    def dump(self, fp: BinaryIO) -> None:
        """Serialize script to file.

        Arguments:
            fp: A file-like object opened for writing.
        """
        with io.TextIOWrapper(fp, newline="") as text_fp:
            actions: List[Dict[str, int]] = []
            pos = 1.0
            for cmd in self.commands:
                # Generate two funscript position updates for every movement
                # (one for start position and one for end position).
                actions.append({"at": cmd.offset, "pos": self.pos_from_vector(pos)})
                duration, newpos = cmd.cmd.vectors(pos)[0]
                actions.append(
                    {"at": cmd.offset + duration, "pos": self.pos_from_vector(newpos)}
                )
                pos = newpos
            self._fixup_actions(actions)
            data = {
                "version": self.FUNSCRIPT_VERSION,
                "inverted": False,
                "range": 90,
                "actions": actions,
            }
            json.dump(data, text_fp)

    @staticmethod
    def _fixup_actions(actions: List[Dict[str, int]]) -> None:
        max_offset: Optional[int] = None
        for i in range(len(actions) - 1, -1, -1):
            action = actions[i]
            if max_offset is None:
                max_offset = action["at"]
                continue
            if action["at"] >= max_offset:
                # For actions which are close together (i.e. high speed piston
                # movements) speed conversion can result in durations that are
                # computed to end past the start of the next movement. When
                # this happens we just drop the end position update for the
                # offending movement.
                del actions[i]
            else:
                max_offset = action["at"]

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
        commands: List[_SC[VorzeLinearCommand]] = []
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
