"""Test cases for VCSX scripts."""
import io

import pytest

from a10sa_script.command.vorze import VorzeLinearCommand
from a10sa_script.command.vorze import VorzeRotateCommand
from a10sa_script.command.vorze import VorzeVibrateCommand
from a10sa_script.exceptions import ParseError
from a10sa_script.script.vcsx import VCSXCycloneScript
from a10sa_script.script.vcsx import VCSXOnaRhythmScript
from a10sa_script.script.vcsx import VCSXPistonScript
from a10sa_script.script.vcsx import VCSXScript
from a10sa_script.script.vorze import _T
from a10sa_script.script.vorze import VorzeScriptCommand


ONARHYTHM_DATA = (
    b"VCSX\x01Vorze_OnaRhythm\x00\x01\x42"
    b"\x00\x00\x00\x03"  # 3 commands
    b"\x00\x00\x00\x00\x00"  # 0, 0, True
    b"\x00\x00\xB4\xC8\x14"  # 46280, 20
    b"\x00\x00\xB5\x0A\x1A"  # 46346, 26
)
ONARHYTHM_COMMANDS = [
    VorzeScriptCommand(0, VorzeVibrateCommand(0)),
    VorzeScriptCommand(46280, VorzeVibrateCommand(20)),
    VorzeScriptCommand(46346, VorzeVibrateCommand(26)),
]

PISTON_DATA = (
    b"VCSX\x01Vorze_Piston\x00\x02\x57\x42"
    b"\x00\x00\x00\06"  # 6 commands
    b"\x00\x00\xB3\x16\x00\x92\x09"  # 45846, 146, 9
    b"\x00\x00\xB6\xDD\x00\x00\x01"  # 46813, 0, 1
    b"\x00\x01\x34\x40\x00\xC8\x11"  # 78912, 200, 17
    b"\x00\x01\x36\x35\x00\x00\x03"  # 79413, 0, 3
    b"\x00\x01\x41\x06\x00\x92\x1B"  # 82182, 146, 27
    b"\x00\x01\x42\x32\x00\x00\x17"  # 82482, 0, 23
)
PISTON_COMMANDS = [
    VorzeScriptCommand(45846, VorzeLinearCommand(146, 9)),
    VorzeScriptCommand(46813, VorzeLinearCommand(0, 1)),
    VorzeScriptCommand(78912, VorzeLinearCommand(200, 17)),
    VorzeScriptCommand(79413, VorzeLinearCommand(0, 3)),
    VorzeScriptCommand(82182, VorzeLinearCommand(146, 27)),
    VorzeScriptCommand(82482, VorzeLinearCommand(0, 23)),
]

CYCLONE_DATA = (
    b"VCSX\x01Vorze_CycloneSA\x00\x01\x42"
    b"\x00\x00\x00\x05"  # 5 commands
    b"\x00\x00\x00\x00\x00"  # 0, 0, True
    b"\x00\x00\xB3\xFF\x86"  # 46079, 6, False
    b"\x00\x00\xB4\x63\x8D"  # 46179, 13, False
    b"\x00\x00\xB4\xC8\x14"  # 46280, 20, True
    b"\x00\x00\xB5\x0A\x1A"  # 46346, 26, True
)
CYCLONE_COMMANDS = [
    VorzeScriptCommand(0, VorzeRotateCommand(0, True)),
    VorzeScriptCommand(46079, VorzeRotateCommand(6, False)),
    VorzeScriptCommand(46179, VorzeRotateCommand(13, False)),
    VorzeScriptCommand(46280, VorzeRotateCommand(20, True)),
    VorzeScriptCommand(46346, VorzeRotateCommand(26, True)),
]


@pytest.mark.parametrize(
    "script_cls, data, commands",
    [
        (VCSXOnaRhythmScript, ONARHYTHM_DATA, ONARHYTHM_COMMANDS),
        (VCSXPistonScript, PISTON_DATA, PISTON_COMMANDS),
        (VCSXCycloneScript, CYCLONE_DATA, CYCLONE_COMMANDS),
    ],
)
def test_load(
    script_cls: type[VCSXScript[_T]],
    data: bytes,
    commands: list[VorzeScriptCommand[_T]],
) -> None:
    """Test loading script from VCSX."""
    orig = io.BytesIO(data)
    orig.seek(0)
    script = script_cls.load(orig)
    expected = script_cls(commands)
    assert script == expected


@pytest.mark.parametrize(
    "script_cls, data, commands",
    [
        (VCSXOnaRhythmScript, ONARHYTHM_DATA, ONARHYTHM_COMMANDS),
        (VCSXPistonScript, PISTON_DATA, PISTON_COMMANDS),
        (VCSXCycloneScript, CYCLONE_DATA, CYCLONE_COMMANDS),
    ],
)
def test_dump(
    script_cls: type[VCSXScript[_T]],
    data: bytes,
    commands: list[VorzeScriptCommand[_T]],
) -> None:
    """Test dumping script to VCSX."""
    script = script_cls(commands)
    f = io.BytesIO()
    script.dump(f)
    assert f.getvalue() == data


@pytest.mark.parametrize(
    "script_cls, data",
    [
        (VCSXOnaRhythmScript, ONARHYTHM_DATA),
        (VCSXPistonScript, PISTON_DATA),
        (VCSXCycloneScript, CYCLONE_DATA),
    ],
)
def test_rotate_load_invalid(script_cls: type[VCSXScript[_T]], data: bytes) -> None:
    """Test invalid VCSX parsing."""
    # invalid header magic
    orig = io.BytesIO(b"\x00")
    with pytest.raises(ParseError):
        orig.seek(0)
        script_cls.load(orig)

    # invalid data
    orig = io.BytesIO(data[:-3])
    with pytest.raises(ParseError):
        orig.seek(0)
        script_cls.load(orig)
