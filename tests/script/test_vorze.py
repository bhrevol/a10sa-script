"""Test cases for Vorze scripts."""
import io
from pathlib import Path

import pytest

from a10sa_script.command.vorze import VorzeRotateCommand
from a10sa_script.exceptions import ParseError
from a10sa_script.script.vorze import VorzeRotateScript
from a10sa_script.script.vorze import VorzeScriptCommand


TEST_CSV = """1870,1,57
1879,0,41
1888,0,0
1997,1,61
2001,0,61
2005,0,0
"""

TEST_COMMANDS = [
    VorzeScriptCommand(187000, VorzeRotateCommand(57, False)),
    VorzeScriptCommand(187900, VorzeRotateCommand(41, True)),
    VorzeScriptCommand(188800, VorzeRotateCommand(0, True)),
    VorzeScriptCommand(199700, VorzeRotateCommand(61, False)),
    VorzeScriptCommand(200100, VorzeRotateCommand(61, True)),
    VorzeScriptCommand(200500, VorzeRotateCommand(0, True)),
]


def test_rotate_load() -> None:
    """Test loading rotate script from CSV."""
    orig = io.BytesIO(TEST_CSV.encode("ascii"))
    orig.seek(0)
    script = VorzeRotateScript.load(orig)
    expected = VorzeRotateScript(TEST_COMMANDS)
    assert script == expected


def test_rotate_dump(tmp_path: Path) -> None:
    """Test dumping rotate script to CSV."""
    script = VorzeRotateScript(TEST_COMMANDS)
    new = tmp_path / "new.csv"
    with open(new, "wb") as f:
        script.dump(f)
    assert new.read_text() == TEST_CSV


def test_rotate_load_invalid() -> None:
    """Test invalid CSV parsing."""
    orig = io.BytesIO(b"1234")
    with pytest.raises(ParseError):
        orig.seek(0)
        VorzeRotateScript.load(orig)
