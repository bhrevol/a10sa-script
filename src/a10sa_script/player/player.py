import asyncio
import time
from abc import abstractmethod
from contextlib import AbstractAsyncContextManager, AsyncExitStack
from types import TracebackType
from typing import TypeVar

from loguru import logger

from ..command.base import BaseCommand
from ..exceptions import A10SAError
from ..script.base import BaseScript
from ..utils import TaskGroup

T = TypeVar("T", bound=BaseCommand)


class ScriptPlayer(AbstractAsyncContextManager["ScriptPlayer[T]"]):
    """Base script player.

    Connects to the default playback device when used as an async context manager.
    """

    DEVICE_LATENCY: int = 0

    def __init__(self) -> None:
        self._offset: int = 0
        self._start_ms: float = 0.0
        self._play_task: asyncio.Task[None] | None = None
        self._send_task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._script: BaseScript[T] | None = None
        self._exit_stack: AsyncExitStack | None = None
        self._tg: TaskGroup | None = None
        self._command_queue: asyncio.Queue[T] | None = None
        self.delay = 0

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
        return self._play_task is not None

    @property
    def script(self) -> BaseScript[T] | None:
        return self._script

    async def connect(self) -> None:
        """Connect to playback device(s)."""
        if self._exit_stack is not None:
            return
        self._exit_stack = AsyncExitStack()
        self._tg = await self._exit_stack.enter_async_context(TaskGroup())
        self._command_queue = asyncio.Queue(maxsize=1)
        self._send_task = self._tg.create_task(self._send_commands())

    async def disconnect(self) -> None:
        """Disconnect from playback device(s)."""

        if self._exit_stack is None:
            return
        if self._send_task is not None:
            self._send_task.cancel()
            try:
                await self._send_task
            except asyncio.CancelledError:
                pass
            self._send_task = None
        await self._exit_stack.aclose()
        if self._command_queue is not None:
            await self._command_queue.join()
            self._command_queue = None
        self._tg = None
        self._exit_stack = None

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
        if self._tg is None:
            logger.error("Not connected")
            return
        self._stop.clear()
        self._play_task = self._tg.create_task(self._run())

    async def _run(self) -> None:
        assert self._script is not None
        assert self._tg is not None
        assert self._command_queue is not None
        logger.debug("Started script playback.")
        warned = False
        loop = asyncio.get_running_loop()
        self._start_ms = loop.time() * 1000 - self._offset
        for command in self._script.seek_iter(self._offset):
            while not self._stop.is_set():
                offset = loop.time() * 1000 - self._start_ms
                command_offset = command.offset - self.DEVICE_LATENCY + self.delay
                timeout = (command_offset - offset) / 1000
                if timeout > 0:
                    await asyncio.sleep(min(1.0, timeout))
                else:
                    break
            if self._stop.is_set():
                logger.debug("Script playback stopped.")
                halt = self.halt_command()
                if halt is not None:
                    await self._command_queue.put(halt)
                return
            try:
                self._command_queue.get_nowait()
                self._command_queue.task_done()
                if not warned:
                    logger.warning(
                        "script contains commands which will be dropped due to device latency"
                    )
                    warned = True
            except asyncio.QueueEmpty:
                pass
            await self._command_queue.put(command.cmd)
            self._offset = command.offset
        logger.debug("Script playback finished.")

    async def _send_commands(self) -> None:
        assert self._command_queue is not None
        try:
            while True:
                cmd = await self._command_queue.get()
                try:
                    await self.send(cmd)
                except A10SAError:
                    logger.exception("Dropped command")
                self._command_queue.task_done()
        finally:
            halt = self.halt_command()
            if halt:
                await self.send(halt)
            while not self._command_queue.empty():
                self._command_queue.get_nowait()
                self._command_queue.task_done()

    def pause(self) -> None:
        """Pause playback.

        This signals that playback should be stopped. To wait for any playback tasks
        to complete, `join()` should be called after `pause()`.
        """
        if not self.is_playing:
            return
        self._stop.set()

    async def join(self, cancel: bool = False) -> None:
        """Wait for script playback to complete."""
        if self._play_task is not None:
            if cancel:
                self._stop.set()
            try:
                await self._play_task
            finally:
                self._play_task = None

    async def seek(self, offset: int) -> None:
        """Seek to the specified time offset.

        When playback is active, playback will continue from the specified offset. When
        playback is paused, the next call to `play()` will start playback from the specified
        offset.

        Arguments:
            offset: Time offset in milliseconds.
        """
        if self.is_playing:
            loop = asyncio.get_running_loop()
            start = loop.time()
            await self.join(cancel=True)
            end = loop.time()
            offset -= round((end - start) * 1000)
            if offset < 0:
                offset = 0
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

    def halt_command(self) -> T | None:
        """Return a command to halt movement."""
        return None
