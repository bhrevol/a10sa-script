"""Test cases for VCSX scripts."""

import io

import pytest

from a10sa_script.command.vorze import VorzePositionCommand
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
    b"\x00\x00\xb4\xc8\x14"  # 46280, 20
    b"\x00\x00\xb5\x0a\x1a"  # 46346, 26
)
ONARHYTHM_COMMANDS = [
    VorzeScriptCommand(0, VorzeVibrateCommand.from_speed(0)),
    VorzeScriptCommand(46280, VorzeVibrateCommand.from_speed(20)),
    VorzeScriptCommand(46346, VorzeVibrateCommand.from_speed(26)),
]

PISTON_DATA = (
    b"VCSX\x01Vorze_Piston\x00\x02\x57\x42"
    b"\x00\x00\x00\06"  # 6 commands
    b"\x00\x00\xb3\x16\x00\x92\x09"  # 45846, 146, 9
    b"\x00\x00\xb6\xdd\x00\x00\x01"  # 46813, 0, 1
    b"\x00\x01\x34\x40\x00\xc8\x11"  # 78912, 200, 17
    b"\x00\x01\x36\x35\x00\x00\x03"  # 79413, 0, 3
    b"\x00\x01\x41\x06\x00\x92\x1b"  # 82182, 146, 27
    b"\x00\x01\x42\x32\x00\x00\x17"  # 82482, 0, 23
)
PISTON_COMMANDS = [
    VorzeScriptCommand(45846, VorzePositionCommand.from_position_and_speed(146, 9)),
    VorzeScriptCommand(
        46813, VorzePositionCommand.from_position_and_speed(0, 1, start_position=146)
    ),
    VorzeScriptCommand(
        78912, VorzePositionCommand.from_position_and_speed(200, 17, start_position=0)
    ),
    VorzeScriptCommand(
        79413, VorzePositionCommand.from_position_and_speed(0, 3, start_position=200)
    ),
    VorzeScriptCommand(
        82182, VorzePositionCommand.from_position_and_speed(146, 27, start_position=0)
    ),
    VorzeScriptCommand(
        82482, VorzePositionCommand.from_position_and_speed(0, 23, start_position=146)
    ),
]

CYCLONE_DATA = (
    b"VCSX\x01Vorze_CycloneSA\x00\x01\x42"
    b"\x00\x00\x00\x05"  # 5 commands
    b"\x00\x00\x00\x00\x00"  # 0, 0, True
    b"\x00\x00\xb3\xff\x86"  # 46079, 6, False
    b"\x00\x00\xb4\x63\x8d"  # 46179, 13, False
    b"\x00\x00\xb4\xc8\x14"  # 46280, 20, True
    b"\x00\x00\xb5\x0a\x1a"  # 46346, 26, True
)
CYCLONE_COMMANDS = [
    VorzeScriptCommand(0, VorzeRotateCommand.from_speed(0, True)),
    VorzeScriptCommand(46079, VorzeRotateCommand.from_speed(6, False)),
    VorzeScriptCommand(46179, VorzeRotateCommand.from_speed(13, False)),
    VorzeScriptCommand(46280, VorzeRotateCommand.from_speed(20, True)),
    VorzeScriptCommand(46346, VorzeRotateCommand.from_speed(26, True)),
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
    assert len(expected.commands) == len(script.commands)
    for i in range(len(expected.commands)):
        assert expected[i].offset == script[i].offset
        assert expected[i].cmd.vorze_eq(script[i].cmd)


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
