"""Test cases for generic scripts."""
from collections.abc import Sequence

import pytest

from a10sa_script.command import BaseCommand
from a10sa_script.script import BaseScript
from a10sa_script.script import ScriptCommand


class _TestCommand(BaseCommand):  # pragma: no cover
    def to_buttplug(self, *args, **kwargs):  # type: ignore
        raise NotImplementedError

    @classmethod
    def from_buttplug(cls, *args, **kwargs):  # type: ignore
        raise NotImplementedError


class _TestScript(BaseScript[_TestCommand]):  # pragma: no cover
    pass


@pytest.mark.parametrize("offsets", [(0, 50, 100), (50, 0, 100), (100, 50, 0)])
def test_script_generic(offsets: Sequence[int]) -> None:
    """Test generic MutableSequence behavior."""
    script = _TestScript([ScriptCommand(offset, _TestCommand()) for offset in offsets])
    assert len(script) == len(offsets)
    expected = sorted(offsets)
    assert [cmd.offset for cmd in script] == expected
    assert all(script[i].offset == expected[i] for i in range(len(offsets)))
    assert [cmd.offset for cmd in reversed(script)] == list(reversed(expected))
    del script[0]
    del expected[0]
    assert [cmd.offset for cmd in script] == expected


def test_script_disabled() -> None:
    """Test disabled MutableSequence functionality."""
    script = _TestScript([ScriptCommand(0, _TestCommand())])
    with pytest.raises(NotImplementedError):
        script[0] = ScriptCommand(0, _TestCommand())
    with pytest.raises(NotImplementedError):
        script.insert(0, ScriptCommand(0, _TestCommand()))
    with pytest.raises(NotImplementedError):
        script.reverse()


@pytest.mark.parametrize("new", [25, 50, 125])
def test_script_add(new: int) -> None:
    """Test command insertion."""
    offsets = [0, 50, 100]
    script = _TestScript([ScriptCommand(offset, _TestCommand()) for offset in offsets])
    script.add(ScriptCommand(new, _TestCommand()))
    assert [cmd.offset for cmd in script] == sorted(offsets + [new])


@pytest.mark.parametrize("start", [25, 50])
def test_script_seek(start: int) -> None:
    """Test seek iterator."""
    offsets = [0, 50, 100]
    script = _TestScript([ScriptCommand(offset, _TestCommand()) for offset in offsets])
    assert [cmd.offset for cmd in script.seek_iter(start)] == offsets[1:]
