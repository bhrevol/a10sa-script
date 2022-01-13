"""Test cases for vorze commands."""
from typing import Tuple

import pytest
from buttplug.core import RotateSubcommand
from buttplug.core import SpeedSubcommand

from a10sa_script.command import VorzeRotateCommand
from a10sa_script.command import VorzeVibrateCommand


@pytest.mark.parametrize(
    "vorze, buttplug_speed",
    [
        (VorzeVibrateCommand(0), 0.0),
        (VorzeVibrateCommand(50), 0.5),
        (VorzeVibrateCommand(100), 1.0),
    ],
)
def test_vibrate_buttplug(vorze: VorzeVibrateCommand, buttplug_speed: float) -> None:
    """Test vibrate Buttplug roundtrip."""
    speed = vorze.speeds[0]
    assert speed == buttplug_speed
    with pytest.raises(ValueError):
        VorzeVibrateCommand.from_speeds([])
    assert vorze == VorzeVibrateCommand.from_speeds(vorze.speeds)
    assert vorze == VorzeVibrateCommand.from_speeds(
        [SpeedSubcommand(0, speed) for speed in vorze.speeds]
    )


@pytest.mark.parametrize(
    "vorze, row",
    [
        (VorzeVibrateCommand(0), (0,)),
        (VorzeVibrateCommand(50), (50,)),
        (VorzeVibrateCommand(100), (100,)),
    ],
)
def test_vibrate_csv(vorze: VorzeVibrateCommand, row: Tuple[int]) -> None:
    """Test vibrate CSV roundtrip."""
    assert vorze.to_csv() == row
    assert vorze == VorzeVibrateCommand.from_csv(row)


@pytest.mark.parametrize(
    "vorze, data",
    [
        (VorzeVibrateCommand(0), b"\x00"),
        (VorzeVibrateCommand(50), b"\x32"),
        (VorzeVibrateCommand(100), b"\x64"),
    ],
)
def test_vibrate_vcsx(vorze: VorzeVibrateCommand, data: bytes) -> None:
    """Test rotate VCSX roundtrip."""
    assert vorze.to_vcsx() == data
    assert vorze == VorzeVibrateCommand.from_vcsx(data)


@pytest.mark.parametrize(
    "vorze, buttplug_speed",
    [
        (VorzeRotateCommand(0, True), 0.0),
        (VorzeRotateCommand(0, False), 0.0),
        (VorzeRotateCommand(50, True), 0.5),
        (VorzeRotateCommand(50, False), 0.5),
        (VorzeRotateCommand(100, True), 1.0),
        (VorzeRotateCommand(100, False), 1.0),
    ],
)
def test_rotate_buttplug(vorze: VorzeRotateCommand, buttplug_speed: float) -> None:
    """Test rotate Buttplug roundtrip."""
    rotation = vorze.rotations[0]
    assert rotation == (buttplug_speed, vorze.clockwise)
    with pytest.raises(ValueError):
        VorzeRotateCommand.from_rotations([])
    assert vorze == VorzeRotateCommand.from_rotations(
        [RotateSubcommand(0, speed, clockwise) for speed, clockwise in vorze.rotations]
    )
    assert vorze == VorzeRotateCommand.from_rotations(vorze.rotations)


@pytest.mark.parametrize(
    "vorze, row",
    [
        (VorzeRotateCommand(0, True), (0, 0)),
        (VorzeRotateCommand(0, False), (1, 0)),
        (VorzeRotateCommand(50, True), (0, 50)),
        (VorzeRotateCommand(50, False), (1, 50)),
        (VorzeRotateCommand(100, True), (0, 100)),
        (VorzeRotateCommand(100, False), (1, 100)),
    ],
)
def test_rotate_csv(vorze: VorzeRotateCommand, row: Tuple[int, int]) -> None:
    """Test rotate CSV roundtrip."""
    assert vorze.to_csv() == row
    assert vorze == VorzeRotateCommand.from_csv(row)


@pytest.mark.parametrize(
    "vorze, data",
    [
        (VorzeRotateCommand(0, True), b"\x00"),
        (VorzeRotateCommand(0, False), b"\x80"),
        (VorzeRotateCommand(50, True), b"\x32"),
        (VorzeRotateCommand(50, False), b"\xb2"),
        (VorzeRotateCommand(100, True), b"\x64"),
        (VorzeRotateCommand(100, False), b"\xe4"),
    ],
)
def test_rotate_vcsx(vorze: VorzeRotateCommand, data: bytes) -> None:
    """Test rotate VCSX roundtrip."""
    assert vorze.to_vcsx() == data
    assert vorze == VorzeRotateCommand.from_vcsx(data)
