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
import src.functions as functions

class States(enum.Enum):
    DOCKED = 0
    UNDOCKED = 1
    WARPING = 2
    MINING = 3
    RETURN = 4


class MiningModel:
    to_UNDOCKED: Any
    to_WARPING: Any
    to_RETURN: Any
    to_MINING: Any
    to_DOCKED: Any

    state = None
    # to_RETURN: Any
    _mining_task = None
    _mining_task_start_time = None
    _not_friednly_count = 0
    check_times = 0
    _belts = 8
    _defence_modules = [
        Module(6, timedelta(seconds=1), timedelta(seconds=10), grid=12)
    ]
    _drones = [
        Module(2, timedelta(seconds=1), timedelta(seconds=10), grid=12)
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
            logging.info("cargo unloading")
            await asyncio.sleep(2)
            await self.player.click(Coordinates.quick_panel_first_button_rect, 6)

            ore_hold = self.player.find_ore_hold_menu_button()
            if ore_hold is None:
                await self.player.click(Coordinates.Inventory.staton_toggle_rect)
                ore_hold = self.player.find_ore_hold_menu_button()
                if ore_hold is None:
                    logging.error("ore hold not found")
                    return
            
            await self.player.click_relative(Coordinates.Inventory.left_menu_rect, ore_hold, 4)
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
        while self.player.get_autopilot_status() == AutopilotStatus.UNKNOWN:
            await asyncio.sleep(1)

        while self.player.get_autopilot_status() == AutopilotStatus.DISABLED:
            await self.player.toggle_autopilot()

        await self.player.click(Coordinates.Space.Bookmarks.bookmarks[0])
        await self.player.click(Coordinates.Space.Bookmarks.set_as_destination_button)
        await self.player.close_bookmarks()
        await self.player.click(Coordinates.Space.zoom_rect)

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

        if functions.chance(0.5):
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
                logging.info(local)
                self._not_friednly_count += 1
            else:
                self._not_friednly_count = 0

        if self._not_friednly_count > 2:
            winsound.Beep(frequency=2000, duration=250)
            self._not_friednly_count = 0
            await self.to_RETURN()
            self.is_safe_return = False

    async def start_mining(self):

        # Включаем майнеры
        for module in self.mining_modules:
            await module.click(self.player)

        # Активируем дронов
        if functions.chance(0.5):
            for drone in self._drones:
                await drone.click(self.player)

    async def approach_asteroid(self):
        await self.player.click(Coordinates.Space.Grid.open_grid_button)
        await self.player.change_grid_filter(8)
        asteroid_number = random.randint(0, 8)
        asteroid = Coordinates.Space.Grid.targets[asteroid_number]
        await self.player.grid_expand()
        await self.player.click(asteroid, 1)
        pos = self.player.get_approach_command_pos()
        if pos != None:
            await self.player.click_command(pos)

    async def on_enter_MINING(self):
        self._mining_task = asyncio.create_task(self.start_mining())
        self._mining_task_start_time = datetime.now()
        self.check_times = 0

    async def mining(self):
        await self.check_local()

        # включенный движок значит работающий approach
        # работающий approach значит астероид ещё живой
        if self.player.is_engine_enabled():
            self.check_times = 0
        else:
            if self._mining_task is None or self._mining_task.done():
                self.check_times += 1
                self._mining_task = asyncio.create_task(self.approach_asteroid())
        
        # белт может исчезнуть
        if self.check_times > 3: 
            await self.to_RETURN()
            self.is_safe_return = True

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
        await self.player.toggle_autopilot()
        self.autopilot.enable()

    async def returning(self):
        if self.player.is_docked_citadel():
            await self.to_DOCKED()
        
        elif self.player.is_docked():
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
