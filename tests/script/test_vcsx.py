"""Test cases for VCSX scripts."""
import io

import pytest

from a10sa_script.command.vorze import VorzeRotateCommand
from a10sa_script.exceptions import ParseError
from a10sa_script.script.vcsx import VCSXCycloneScript
from a10sa_script.script.vorze import VorzeScriptCommand


TEST_CYCLONE = (
    b"VCSX\x01Vorze_CycloneSA\x00\x01\x42"
    b"\x00\x00\x00\x05"  # 5 commands
    b"\x00\x00\x00\x00\x00"  # 0, 0, True
    b"\x00\x00\xB3\xFF\x86"  # 46079, 6, False
    b"\x00\x00\xB4\x63\x8D"  # 46179, 13, False
    b"\x00\x00\xB4\xC8\x14"  # 46280, 20, True
    b"\x00\x00\xB5\x0A\x1A"  # 46346, 26, True
)


TEST_COMMANDS = [
    VorzeScriptCommand(0, VorzeRotateCommand(0, True)),
    VorzeScriptCommand(46079, VorzeRotateCommand(6, False)),
    VorzeScriptCommand(46179, VorzeRotateCommand(13, False)),
    VorzeScriptCommand(46280, VorzeRotateCommand(20, True)),
    VorzeScriptCommand(46346, VorzeRotateCommand(26, True)),
]


def test_cyclone_load() -> None:
    """Test loading cyclone script from VCSX."""
    orig = io.BytesIO(TEST_CYCLONE)
    orig.seek(0)
    script = VCSXCycloneScript.load(orig)
    expected = VCSXCycloneScript(TEST_COMMANDS)
    assert script == expected


def test_cyclone_dump() -> None:
    """Test dumping cyclone script to VCSX."""
    script = VCSXCycloneScript(TEST_COMMANDS)
    f = io.BytesIO()
    script.dump(f)
    assert f.getvalue() == TEST_CYCLONE


def test_rotate_load_invalid() -> None:
    """Test invalid CSV parsing."""
    # invalid header magic
    orig = io.BytesIO(b"1234")
    with pytest.raises(ParseError):
        orig.seek(0)
        VCSXCycloneScript.load(orig)

    # invalid data
    orig = io.BytesIO(TEST_CYCLONE[:-3])
    with pytest.raises(ParseError):
        orig.seek(0)
        VCSXCycloneScript.load(orig)
