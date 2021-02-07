from asyncio.tasks import sleep
from typing import Any

from transitions.core import State
from src.LDPlayer960x540 import Coordinates
from src.sequence import Module, Sequence
from .player import AutopilotStatus, InfoStatus, Player, MissionStatus
from transitions.extensions.asyncio import AsyncMachine
import asyncio
import enum
import logging
import random
import csv
from datetime import date, datetime, timedelta
from .autopilot import Algorithm, Autopilot
import winsound


class LocalChecking(Sequence):
    _not_friednly_count: int = 0

    def __init__(self, player: Player):
        self.player = player

    def _enabled(self):
        logging.info("local checking enabled")

    def _disabled(self):
        logging.info("local checking disbled")

    async def _loop_func(self):
        local = self.player.get_local()
        if local != None and not self.player.is_docked():
            if not local.is_friendly:
                winsound.Beep(frequency=2500, duration=100)
                self._not_friednly_count += 1
            else:
                self._not_friednly_count = 0

        if self._not_friednly_count > 2:
            winsound.Beep(frequency=2000, duration=250)
            self._not_friednly_count = 0
