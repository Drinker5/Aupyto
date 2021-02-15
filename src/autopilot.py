# pylint: disable=maybe-no-member
from collections import namedtuple
from numpy.lib.function_base import place
from src.sequence import Module, Sequence
from .player import Player, InfoStatus
from transitions.extensions.asyncio import AsyncMachine
from transitions import Machine
import asyncio
import enum
import logging
import csv
from datetime import date, datetime, timedelta
from collections import namedtuple
import random
import src.functions as functions

class AutopilotModel:
    def __init__(self, player: Player, modules: list[Module]):
        self.player = player
        self._modules = modules
        self.module_activation_ban_time = datetime.min

    ''' шансовый true в percentах '''

    async def as_fast_as_can(self):
        for module in self._modules:
            await module.click(self.player)

    ''' активирует модули по рандомной очереди, 
        выбирает первый доступный модуль (без КД) '''
    async def prepare_for_warp_logic(self):
        modules = self._modules

        if functions.chance(50):
            modules.reverse()

        # включаем если последняя активация была более 10 секунд назад
        # эмулируем одно нажатие модуля на 1 варп
        if self.module_activation_ban_time < datetime.now():
            ban = timedelta(seconds=10)
            # эмулиуем афк 10% на варп, на 2 минуты
            if functions.chance(10):
                ban = timedelta(minutes=2)
            elif functions.chance(33):
                # эмулируем активацию всех модулей 33%
                for module in modules:
                    await module.click(self.player)
            else:
                # активируем один
                for module in modules:
                    if await module.click(self.player):
                        break
            self.module_activation_ban_time = datetime.now() + ban


class Algorithm(enum.Enum):
    DELIVERY = 0
    RUN_FOR_IT = 1


class Autopilot(Sequence):

    def __init__(self, player: Player, modules: list[Module], algo: Algorithm = Algorithm.DELIVERY):
        self.player = player
        self.model = AutopilotModel(player, modules)
        self.algo = algo

    def _enabled(self):
        logging.info("Autopilot enabled %s" %(self.algo))

    def _disabled(self):
        logging.info("Autopilot disbled")

    async def _loop_func(self):
        if self.player.is_engine_enabled():
            if self.algo == Algorithm.DELIVERY:
                await self.model.prepare_for_warp_logic()

            if self.algo == Algorithm.RUN_FOR_IT:
                await self.model.as_fast_as_can()
