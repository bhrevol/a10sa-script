"""Test cases for Vorze scripts."""

import io
from pathlib import Path

import pytest

from a10sa_script.command.vorze import VorzePositionCommand
from a10sa_script.command.vorze import VorzeRotateCommand
from a10sa_script.command.vorze import VorzeVibrateCommand
from a10sa_script.exceptions import ParseError
from a10sa_script.script.vorze import _T
from a10sa_script.script.vorze import VorzeLinearScript
from a10sa_script.script.vorze import VorzeRotateScript
from a10sa_script.script.vorze import VorzeScript
from a10sa_script.script.vorze import VorzeScriptCommand
from a10sa_script.script.vorze import VorzeVibrateScript


VIBRATE_CSV = """1870,57
1879,41
1888,0
1997,61
2005,0
"""
VIBRATE_COMMANDS = [
    VorzeScriptCommand(187000, VorzeVibrateCommand.from_speed(57)),
    VorzeScriptCommand(187900, VorzeVibrateCommand.from_speed(41)),
    VorzeScriptCommand(188800, VorzeVibrateCommand.from_speed(0)),
    VorzeScriptCommand(199700, VorzeVibrateCommand.from_speed(61)),
    VorzeScriptCommand(200500, VorzeVibrateCommand.from_speed(0)),
]

LINEAR_CSV = """458,146,9
468,0,1
789,200,17
794,0,3
822,146,27
825,0,23
"""
LINEAR_COMMANDS = [
    VorzeScriptCommand(45800, VorzePositionCommand.from_position_and_speed(146, 9)),
    VorzeScriptCommand(
        46800, VorzePositionCommand.from_position_and_speed(0, 1, start_position=146)
    ),
    VorzeScriptCommand(
        78900, VorzePositionCommand.from_position_and_speed(200, 17, start_position=0)
    ),
    VorzeScriptCommand(
        79400, VorzePositionCommand.from_position_and_speed(0, 3, start_position=200)
    ),
    VorzeScriptCommand(
        82200, VorzePositionCommand.from_position_and_speed(146, 27, start_position=0)
    ),
    VorzeScriptCommand(
        82500, VorzePositionCommand.from_position_and_speed(0, 23, start_position=146)
    ),
]

ROTATE_CSV = """1870,1,57
1879,0,41
1888,0,0
1997,1,61
2001,0,61
2005,0,0
"""
ROTATE_COMMANDS = [
    VorzeScriptCommand(187000, VorzeRotateCommand.from_speed(57, False)),
    VorzeScriptCommand(187900, VorzeRotateCommand.from_speed(41, True)),
    VorzeScriptCommand(188800, VorzeRotateCommand.from_speed(0, True)),
    VorzeScriptCommand(199700, VorzeRotateCommand.from_speed(61, False)),
    VorzeScriptCommand(200100, VorzeRotateCommand.from_speed(61, True)),
    VorzeScriptCommand(200500, VorzeRotateCommand.from_speed(0, True)),
]


@pytest.mark.parametrize(
    "script_cls, csv, commands",
    [
        (VorzeVibrateScript, VIBRATE_CSV, VIBRATE_COMMANDS),
        (VorzeLinearScript, LINEAR_CSV, LINEAR_COMMANDS),
        (VorzeRotateScript, ROTATE_CSV, ROTATE_COMMANDS),
    ],
)
def test_load(
    script_cls: type[VorzeScript[_T]], csv: str, commands: list[VorzeScriptCommand[_T]]
) -> None:
    """Test loading script from CSV."""
    orig = io.BytesIO(csv.encode("ascii"))
    orig.seek(0)
    script = script_cls.load(orig)
    expected = script_cls(commands)
    assert len(script.commands) == len(expected.commands)
    for i in range(len(expected.commands)):
        assert expected.commands[i].offset == script.commands[i].offset
        assert expected.commands[i].cmd.vorze_eq(script.commands[i].cmd)


@pytest.mark.parametrize(
    "script_cls, csv, commands",
    [
        (VorzeVibrateScript, VIBRATE_CSV, VIBRATE_COMMANDS),
        (VorzeLinearScript, LINEAR_CSV, LINEAR_COMMANDS),
        (VorzeRotateScript, ROTATE_CSV, ROTATE_COMMANDS),
    ],
)
def test_dump(
    script_cls: type[VorzeScript[_T]],
    csv: str,
    commands: list[VorzeScriptCommand[_T]],
    tmp_path: Path,
) -> None:
    """Test dumping script to CSV."""
    script = script_cls(commands)
    new = tmp_path / "new.csv"
    with open(new, "wb") as f:
        script.dump(f)
    assert new.read_text(encoding="utf-8-sig") == csv


@pytest.mark.parametrize(
    "script_cls", [VorzeVibrateScript, VorzeLinearScript, VorzeRotateScript]
)
def test_load_invalid(script_cls: type[VorzeScript[_T]]) -> None:
    """Test invalid CSV parsing."""
    orig = io.BytesIO(b"\x00")
    with pytest.raises(ParseError):
        orig.seek(0)
        script_cls.load(orig)
