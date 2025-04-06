import io
import json
from pathlib import Path

import pytest

from a10sa_script.command.base import GenericLinearCommand
from a10sa_script.command.vorze import VorzeLinearCommand
from a10sa_script.script.base import ScriptCommand
from a10sa_script.script.funscript import FunscriptScript
from a10sa_script.script.vorze import VorzeLinearScript, VorzeScriptCommand

STANDARD_FUNSCRIPT = """{
	"version": "1.0",
	"inverted": false,
	"range": 90,
	"actions": [
        {"pos": 100, "at": 0},
		{"pos": 100, "at": 100},
		{"pos": 0, "at": 500},
        {"pos": 0, "at": 1000},
        {"pos": 75, "at": 1500}
	]
}"""
STANDARD_COMMANDS = [
    ScriptCommand(0, GenericLinearCommand(0, 1.0)),
    ScriptCommand(100, GenericLinearCommand(400, 0.0)),
    ScriptCommand(1000, GenericLinearCommand(500, 0.75)),
]
STANDARD_VORZE = [
    VorzeScriptCommand(100, VorzeLinearCommand(0, 30)),
    VorzeScriptCommand(1000, VorzeLinearCommand(150, 16)),
]

INVERTED_FUNSCRIPT = """{
	"version": "1.0",
	"inverted": true,
	"range": 90,
	"actions": [
		{"pos": 0, "at": 100},
		{"pos": 100, "at": 500},
        {"pos": 100, "at": 1000},
        {"pos": 25, "at": 1500}
	]
}"""
INVERTED_COMMANDS = [
    ScriptCommand(100, GenericLinearCommand(400, 0.0)),
    ScriptCommand(1000, GenericLinearCommand(500, 0.75)),
]
INVERTED_VORZE = [
    VorzeScriptCommand(100, VorzeLinearCommand(0, 30)),
    VorzeScriptCommand(1000, VorzeLinearCommand(150, 16)),
]


@pytest.mark.parametrize(
    "funscript, commands, inverted",
    [
        (STANDARD_FUNSCRIPT, STANDARD_COMMANDS, False),
        (INVERTED_FUNSCRIPT, INVERTED_COMMANDS, True),
    ],
)
def test_load(
    funscript: str, commands: list[ScriptCommand[GenericLinearCommand]], inverted: bool
) -> None:
    """Test loading from funscript."""
    orig = io.BytesIO(funscript.encode())
    orig.seek(0)
    script = FunscriptScript.load(orig)
    assert script == FunscriptScript(commands, inverted=inverted)


@pytest.mark.parametrize(
    "funscript, commands, inverted",
    [
        (STANDARD_FUNSCRIPT, STANDARD_COMMANDS, False),
        (INVERTED_FUNSCRIPT, INVERTED_COMMANDS, True),
    ],
)
def test_dump(
    funscript: str,
    commands: list[ScriptCommand[GenericLinearCommand]],
    inverted: bool,
    tmp_path: Path,
) -> None:
    """Test loading from funscript."""
    script = FunscriptScript(commands, inverted=inverted)
    new = tmp_path / "new.funscript"
    with open(new, "wb") as f:
        script.dump(f)
    assert json.loads(new.read_text()) == json.loads(funscript)


@pytest.mark.parametrize(
    "commands, vorze_commands, inverted",
    [
        (STANDARD_COMMANDS, STANDARD_VORZE, False),
        (INVERTED_COMMANDS, INVERTED_VORZE, True),
    ],
)
def test_funscript_to_vorze(
    commands: list[ScriptCommand[GenericLinearCommand]],
    vorze_commands: list[VorzeScriptCommand[VorzeLinearCommand]],
    inverted: bool,
) -> None:
    """Test converting funscript to Vorze CSV."""
    expected = VorzeLinearScript(vorze_commands)
    actual = FunscriptScript(commands, inverted=inverted).to_vorze()
    assert expected.commands == actual.commands
    assert expected == actual


@pytest.mark.parametrize(
    "commands, vorze_commands, inverted",
    [
        (STANDARD_COMMANDS, STANDARD_VORZE, False),
        (INVERTED_COMMANDS, INVERTED_VORZE, True),
    ],
)
def test_funscript_from_vorze(
    commands: list[ScriptCommand[GenericLinearCommand]],
    vorze_commands: list[VorzeScriptCommand[VorzeLinearCommand]],
    inverted: bool,
) -> None:
    """Test converting funscript from Vorze CSV."""
    expected = FunscriptScript(commands, inverted=inverted)
    actual = FunscriptScript.from_vorze(
        VorzeLinearScript(vorze_commands), inverted=inverted
    )
    assert len(expected.commands) == len(actual.commands)
    for i, expected_cmd in enumerate(expected.commands):
        actual_cmd = actual.commands[i]
        assert expected_cmd.offset == actual_cmd.offset
        assert expected_cmd.cmd.position == actual_cmd.cmd.position
        # allow 50ms range to account for loss of resolution
        assert abs(expected_cmd.cmd.duration - actual_cmd.cmd.duration) <= 50
