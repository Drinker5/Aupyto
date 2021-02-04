from abc import ABCMeta, abstractmethod
import asyncio
from datetime import datetime, timedelta
from src.player import Player
from dataclasses import dataclass


@dataclass
class Module:
    position: int
    cd: timedelta
    activation_time: timedelta
    grid: int = 8
    last_run: datetime = datetime.min

    @property
    def is_available(self) -> bool:
        date = self.last_run + self.cd + self.activation_time
        return date < datetime.now()

    def activate(self):
        self.last_run = datetime.now()

    async def click(self, player: Player):
        if self.is_available:
            self.activate()
            await player.click_module(self.position, self.grid)
            return True
        return False


class Sequence:
    __metaclass__ = ABCMeta
    _sleep_time: float = 1.0
    loop_task: asyncio.Task
    start_time: datetime
    end_time: datetime

    def enable(self):
        self.__start_loop()

    @abstractmethod
    def _enabled(self):
        pass

    def disable(self):
        self.__stop_loop()

    @abstractmethod
    def _disabled(self):
        pass

    def __start_loop(self):
        async def loop():
            try:
                while True:
                    await self._loop_func()
                    await asyncio.sleep(self._sleep_time)
            except asyncio.CancelledError:
                # self.disable()
                raise

        self.loop_task = asyncio.create_task(loop())
        self.start_time = datetime.now()
        self._enabled()

    @abstractmethod
    async def _loop_func(self):
        raise NotImplementedError

    def __stop_loop(self):
        if self.loop_task != None:
            self.loop_task.cancel()
            self.end_time = datetime.now()
            self._disabled()
