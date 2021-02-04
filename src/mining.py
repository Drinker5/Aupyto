# pylint: disable=maybe-no-member

from asyncio.tasks import sleep
from typing import Any

from transitions.core import State
from src.LDPlayer960x540 import Coordinates
from src.sequence import Module, Sequence
from .player import AutopilotStatus, InfoStatus, Player, MissionStatus
from transitions.extensions.asyncio import AsyncMachine
from transitions import Machine
import asyncio
import enum
import logging
import random
import csv
from datetime import date, datetime, timedelta
from .autopilot import Algorithm, Autopilot
import winsound


class States(enum.Enum):
    DOCKED = 0
    UNDOCKED = 1
    WARPING = 2
    MINING = 3
    RETURN = 4


class MiningModel:
    state = None
    # to_RETURN: Any
    _mining_task = None
    _mining_task_start_time = None
    _not_friednly_count = 0
    _belts = 8
    _defence_modules = [
        Module(6, timedelta(seconds=1), timedelta(seconds=10), grid=12)
    ]

    def __init__(self, player: Player,
                 mining_modules: list[Module],
                 autopilot: Autopilot):
        self.player = player
        self.mining_modules = mining_modules
        self.machine = AsyncMachine(self,
                                    states=States,
                                    initial=States.DOCKED)
        self.autopilot = autopilot

    # region DOCKED State
    async def on_enter_DOCKED(self):
        await asyncio.sleep(random.randint(3, 10))
        if not self.is_safe_return:
            print("Ну чё, можно вылетать? ...")
            input()


    async def docked(self):
        if self.player.get_inventory_load_percent() > 0.01:
            await self.player.press_first_quick_button()
            await asyncio.sleep(4)
            await self.player.press_ore_hold_button()
            while not self.player.is_select_all_active():
                await self.player.press_select_all_button()
            while self.player.get_move_to_window_pos() == None:
                await self.player.press_move_to_button()
            await self.player.press_move_to_item_hangar_button()
            await self.player.close()
            await self.player.close()

        await self.player.press_undock_citadel_button()
        await asyncio.sleep(5)
        while self.player.get_autopilot_status() == AutopilotStatus.UNKNOWN:
            await asyncio.sleep(1)
        await self.to_UNDOCKED()
    # endregion

    # region UNDOCKED State
    async def on_enter_UNDOCKED(self):
        await asyncio.sleep(random.randint(5, 8))

        # Предполагаем что автопилот выключен
        #status = self.player.get_autopilot_status()
        # if status == AutopilotStatus.DISABLED:
        await self.player.toggle_autopilot()
        await asyncio.sleep(2)
        await self.player.click(Coordinates.Space.Bookmarks.bookmarks[0])
        await self.player.click(Coordinates.Space.Bookmarks.set_as_destination_button)
        await self.player.close_bookmarks()

    async def undocked(self):
        await self.player.click(Coordinates.Space.Grid.open_grid_button)
        await self.player.change_grid_filter(7)
        pos = None
        while pos == None:
            await self.player.grid_expand()
            belt_number = random.randint(0, self._belts - 1)
            belt = Coordinates.Space.Grid.targets[belt_number]
            await self.player.click(belt, 1)
            pos = self.player.get_warp_command_pos()

        await self.player.click_command(pos)

        for module in self._defence_modules:
            await module.click(self.player)

        self.start_warping_time = datetime.now()
        asyncio.create_task(self.player.scroll_local(3))
        await self.to_WARPING()
    # endregion

    # region MINING State
    async def check_local(self):
        local = self.player.get_local()
        if local != None:
            # print(local)
            if not local.is_friendly:
                winsound.Beep(frequency=2500, duration=100)
                self._not_friednly_count += 1
            else:
                self._not_friednly_count = 0

        if self._not_friednly_count > 2:
            winsound.Beep(frequency=2000, duration=250)
            self._not_friednly_count = 0
            await self.to_RETURN()
            self.is_safe_return = False

    async def start_mining(self):
        for module in self.mining_modules:
            await module.click(self.player)

        async def approach_asteroid():
            await self.player.click(Coordinates.Space.Grid.open_grid_button)
            await self.player.change_grid_filter(8)
            pos = None
            # check_times = 0
            while pos == None:
                asteroid_number = random.randint(0, 8)
                asteroid = Coordinates.Space.Grid.targets[asteroid_number]
                await self.player.grid_expand()
                await self.player.click(asteroid, 1)
                pos = self.player.get_approach_command_pos()
                # не работает
                # check_times += 1
                # # Проверка что астероиды закончились
                # if check_times > 10: 
                #     await self.to_RETURN()
                #     self.is_safe_return = True
                #     return

            await self.player.click_command(pos)

        await approach_asteroid()
        while True:
            # включенный движок значит работающий approach
            # работающий approach значит астероид ещё живой
            if self.player.is_engine_enabled():
                await asyncio.sleep(10)
            else:
                await approach_asteroid()

    async def on_enter_MINING(self):
        self._mining_task = asyncio.create_task(self.start_mining())
        self._mining_task_start_time = datetime.now()

    async def mining(self):
        await self.check_local()
        if self.player.get_inventory_load_percent() >= 1.0:
            await self.to_RETURN()
            self.is_safe_return = True

        if self._mining_task_start_time + timedelta(minutes=30) < datetime.now():
            logging.info("Слишком долго копаем, возвращаемся")
            await self.to_RETURN()
            self.is_safe_return = True

    async def on_exit_MINING(self):
        self._mining_task.cancel()

    # endregion

    # region WARPING State
    async def warping(self):
        stopped = self.player.is_ship_stopped()
        too_long_warp = self.start_warping_time + \
            timedelta(seconds=60) < datetime.now()
        if stopped or too_long_warp:
            await self.to_MINING()
    # endregion

    # region RETURN State
    async def on_enter_RETURN(self):
        self.autopilot.enable()
        await self.player.toggle_autopilot()

    async def returning(self):
        if self.player.is_docked_citadel():
            await self.to_DOCKED()

    def on_exit_RETURN(self):
        self.autopilot.disable()
    # endregion


class Mining(Sequence):

    def __init__(self, player: Player,
                 mining_modules: list[Module],
                 autopilot_modules: list[Module]):
        self.player = player
        self.model = MiningModel(
            player,
            mining_modules,
            Autopilot(player, autopilot_modules, algo=Algorithm.RUN_FOR_IT))

    def _enabled(self):
        logging.info("mining enabled")

    def _disabled(self):
        logging.info("mining disbled")

    async def _loop_func(self):
        if self.model.state is States.DOCKED:
            await self.model.docked()

        if self.model.state is States.UNDOCKED:
            await self.model.undocked()

        if self.model.state is States.WARPING:
            await self.model.warping()

        if self.model.state is States.MINING:
            await self.model.mining()

        if self.model.state is States.RETURN:
            await self.model.returning()
