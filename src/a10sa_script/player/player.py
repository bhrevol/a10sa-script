import asyncio
from abc import abstractmethod
from contextlib import AbstractAsyncContextManager
import time
from typing import TypeVar
from types import TracebackType

from loguru import logger

from ..command.base import BaseCommand
from ..script.base import BaseScript


T = TypeVar("T", bound=BaseCommand)


class ScriptPlayer(AbstractAsyncContextManager["ScriptPlayer[T]"]):
    """Base script player.

    Connects to the default playback device when used as an async context manager.
    """

    def __init__(self) -> None:
        self._offset: int = 0
        self._start_ms: float = 0.0
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._script: BaseScript[T] | None = None

    async def __aenter__(self) -> "ScriptPlayer[T]":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        self.pause()
        await self.join()
        await self.disconnect()
        return None

    @property
    def is_playing(self) -> bool:
        return self._task is not None

    @property
    def script(self) -> BaseScript[T] | None:
        return self._script

    async def connect(self) -> None:
        """Connect to playback device(s)."""

    async def disconnect(self) -> None:
        """Disconnect from playback device(s)."""

    async def load(self, script: BaseScript[T]) -> None:
        """Load the script to be played.

        Stops playback of any previously loaded script.
        """
        await self.join(cancel=True)
        self._script = script
        await self.seek(0)

    def play(self) -> None:
        """Start playback."""
        if self.is_playing:
            return
        if self._script is None:
            logger.error("No script is loaded.")
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        assert self._script is not None
        logger.debug("Started script playback.")
        self._start_ms = time.time() * 1000 - self._offset
        for command in self._script.seek_iter(self._offset):
            if command.offset != self._offset:
                offset = time.time() * 1000 - self._start_ms
                timeout = (command.offset - offset) / 1000
                if timeout > 0:
                    try:
                        await asyncio.wait_for(self._stop.wait(), timeout)
                        logger.debug("Script playback stopped.")
                        return
                    except TimeoutError:
                        pass
                elif timeout < 0:
                    logger.debug("Script desync: {:03f} s", timeout)
            await self.send(command.cmd)
            self._offset = command.offset
        logger.debug("Script playback finished.")

    def pause(self) -> None:
        """Pause playback.

        This signals that playback should be stopped. To wait for any playback tasks
        to complete, `join()` should be called after `pause()`.
        """
        if not self.is_playing:
            return
        self._stop.set()

    async def join(self, cancel: bool = False) -> None:
        """Wait for playback tasks to complete."""
        if self._task is not None:
            if cancel:
                self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                if cancel:
                    pass
            finally:
                self._task = None

    async def seek(self, offset: int) -> None:
        """Seek to the specified time offset.

        When playback is active, playback will continue from the specified offset. When
        playback is paused, the next call to `play()` will start playback from the specified
        offset.

        Arguments:
            offset: Time offset in milliseconds.
        """
        if self.is_playing:
            await self.join(cancel=True)
            self._offset = offset
            self.play()
        else:
            self._offset = offset

    def tell(self) -> int:
        """Return the current playback time offset in milliseconds."""
        if self.is_playing:
            return round(time.time() * 1000 - self._start_ms)
        return self._offset

    @abstractmethod
    async def send(self, command: T) -> None:
        """Send command to the playback device."""
        ...

    async def reset(self) -> None:
        """Reset the playback device to a default state and/or position."""
