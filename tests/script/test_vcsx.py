"""Test cases for VCSX scripts."""
import io
from typing import List
from typing import Type

import pytest

from a10sa_script.command.vorze import VorzeRotateCommand
from a10sa_script.command.vorze import VorzeVibrateCommand
from a10sa_script.exceptions import ParseError
from a10sa_script.script.vcsx import VCSXCycloneScript
from a10sa_script.script.vcsx import VCSXOnaRhythmScript
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
        (VCSXCycloneScript, CYCLONE_DATA, CYCLONE_COMMANDS),
    ],
)
def test_load(
    script_cls: Type[VCSXScript[_T]],
    data: bytes,
    commands: List[VorzeScriptCommand[_T]],
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
        (VCSXCycloneScript, CYCLONE_DATA, CYCLONE_COMMANDS),
    ],
)
def test_cyclone_dump(
    script_cls: Type[VCSXScript[_T]],
    data: bytes,
    commands: List[VorzeScriptCommand[_T]],
) -> None:
    """Test dumping script to VCSX."""
    script = script_cls(commands)
    f = io.BytesIO()
    script.dump(f)
    assert f.getvalue() == data


@pytest.mark.parametrize(
    "script_cls, data",
    [(VCSXOnaRhythmScript, ONARHYTHM_DATA), (VCSXCycloneScript, CYCLONE_DATA)],
)
def test_rotate_load_invalid(script_cls: Type[VCSXScript[_T]], data: bytes) -> None:
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
