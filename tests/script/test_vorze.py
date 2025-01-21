"""Test cases for Vorze scripts."""
import io
from pathlib import Path

import pytest

from a10sa_script.command.vorze import VorzeLinearCommand
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
    VorzeScriptCommand(187000, VorzeVibrateCommand(57)),
    VorzeScriptCommand(187900, VorzeVibrateCommand(41)),
    VorzeScriptCommand(188800, VorzeVibrateCommand(0)),
    VorzeScriptCommand(199700, VorzeVibrateCommand(61)),
    VorzeScriptCommand(200500, VorzeVibrateCommand(0)),
]

LINEAR_CSV = """458,146,9
468,0,1
789,200,17
794,0,3
822,146,27
825,0,23
"""
LINEAR_COMMANDS = [
    VorzeScriptCommand(45800, VorzeLinearCommand(146, 9)),
    VorzeScriptCommand(46800, VorzeLinearCommand(0, 1)),
    VorzeScriptCommand(78900, VorzeLinearCommand(200, 17)),
    VorzeScriptCommand(79400, VorzeLinearCommand(0, 3)),
    VorzeScriptCommand(82200, VorzeLinearCommand(146, 27)),
    VorzeScriptCommand(82500, VorzeLinearCommand(0, 23)),
]

ROTATE_CSV = """1870,1,57
1879,0,41
1888,0,0
1997,1,61
2001,0,61
2005,0,0
"""
ROTATE_COMMANDS = [
    VorzeScriptCommand(187000, VorzeRotateCommand(57, False)),
    VorzeScriptCommand(187900, VorzeRotateCommand(41, True)),
    VorzeScriptCommand(188800, VorzeRotateCommand(0, True)),
    VorzeScriptCommand(199700, VorzeRotateCommand(61, False)),
    VorzeScriptCommand(200100, VorzeRotateCommand(61, True)),
    VorzeScriptCommand(200500, VorzeRotateCommand(0, True)),
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
    assert script == expected


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
