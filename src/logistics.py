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
    LOAD = 0
    TRAVEL = 1
    UNLOAD = 2
    RETURN = 3


class Modes(enum.Enum):
    CARGOHOLD = 0
    MINERAL = 1


class LogisticsModel:
    state = None
    to_LOAD: Any
    to_TRAVEL: Any
    to_UNLOAD: Any
    to_RETURN: Any
    travel_bookmark_position = -1
    return_bookmark_position = -1
    mode: Modes

    def __init__(self, player: Player):
        self.player = player
        self.machine = AsyncMachine(self,
                                    states=States,
                                    initial=States.LOAD)

    mineral_loaded = False

    async def on_enter_LOAD(self):
        self.mineral_loaded = False

    async def load(self):
        # уже загружен
        if self.player.get_inventory_load_percent() >= 0.99:
            await self.to_TRAVEL()
            return

        await self.player.click(Coordinates.quick_panel_first_button_rect, 6)
        await self.player.press_item_hangar_button()
        if not self.player.is_item_compact_mode():
            await self.player.click(Coordinates.Inventory.item_mode_button)

        await self.player.click(Coordinates.Inventory.compact_items_grid[0])
        move_to_pos = self.player.get_selected_item_move_to_button_position()
        if move_to_pos == None:
            logging.info('move to button not found')
            await self.player.close()
            await self.player.close()
            return

        await self.player.click(move_to_pos)

        if self.player.get_move_to_window_pos() == None:
            logging.info("move to window not found")
            await self.player.close()
            await self.player.close()
            return

        if self.mode == Modes.MINERAL and not self.mineral_loaded:
            await self.load_mineral()
            self.mineral_loaded = True
            return

        await self.player.click(Coordinates.Inventory.item_move_to_ships[0])

        if self.player.is_load_amount_window_showing():
            await self.player.click(Coordinates.Inventory.move_to_load_maximum_point)
            await self.player.click(Coordinates.Inventory.move_to_load_ok_button)
        else:
            # не загрузилось полностью
            await self.player.close()
            return
        await self.player.close()
        # загрузились
        await self.to_TRAVEL()

    async def load_mineral(self):
        await self.player.click(Coordinates.Inventory.item_move_to_ships_additional_cargo[0])
        await self.player.click(Coordinates.Inventory.item_move_to_selected_ship_additional_cargo)
        if self.player.is_load_amount_window_showing():
            await self.player.click(Coordinates.Inventory.move_to_load_maximum_point)
            await self.player.click(Coordinates.Inventory.move_to_load_ok_button)
        # else не загрузилось полностью ну и пофиг
        await self.player.close()

    async def __autopilot_and_undock(self, pos):
        if pos <= 0:
            pos = 1

        if self.player.get_autopilot_status() == AutopilotStatus.DISABLED:
            await self.player.toggle_autopilot()
        await self.player.click(Coordinates.Space.Bookmarks.start_autopilot_buttons[pos-1])
        if not self.player.is_confirm_dialog_showing():
            logging.warn('confirm window not found')
            return

        await self.player.press_dialog_confirm_button()

    async def on_enter_TRAVEL(self):
        if self.travel_bookmark_position == -1:
            print("ENTER TRAVEL BOOKMARK POSITION (start from 1): ")
            try:
                num = int(input())
                self.travel_bookmark_position = num
            except:
                print("input error")
                raise

        await self.__autopilot_and_undock(self.travel_bookmark_position)
        await asyncio.sleep(10)

    async def travel(self):
        if self.player.is_docked() or self.player.is_docked_citadel():
            logging.info('docked')
            await asyncio.sleep(5)
            await self.to_UNLOAD()

    async def unload(self):
        await self.player.click(Coordinates.quick_panel_first_button_rect, 6)
        await self.player.click(Coordinates.Inventory.staton_toggle_rect, 1)
        await self.player.click(Coordinates.Inventory.active_ship_with_toggled_station_rect)
        await self.player.click(Coordinates.Inventory.select_all_button)
        await self.player.click(Coordinates.Inventory.move_to_button, 1)
        await self.player.click(Coordinates.Inventory.move_to_item_hangar_button)

        if self.mode == Modes.MINERAL:
            mineral_hold = self.player.find_mineral_hold_menu_button()
            if mineral_hold is None:
                logging.error("ore hold not found")
            else:
                await self.player.click_relative(Coordinates.Inventory.left_menu_rect, mineral_hold, 4)
                while not self.player.is_select_all_active():
                    await self.player.press_select_all_button()
                while self.player.get_move_to_window_pos() == None:
                    await self.player.press_move_to_button()
                await self.player.press_move_to_item_hangar_button()
                await self.player.close()

        await self.player.close()
        await self.to_RETURN()

    async def on_enter_RETURN(self):
        if self.return_bookmark_position == -1:
            print("ENTER RETURN BOOKMARK POSITION (start from 1): ")
            try:
                num = int(input())
                self.return_bookmark_position = num
            except:
                print("input error")
                raise

        await self.__autopilot_and_undock(self.return_bookmark_position)
        await asyncio.sleep(10)

    async def returna(self):
        if self.player.is_docked() or self.player.is_docked_citadel():
            logging.info('docked')
            await asyncio.sleep(5)
            await self.to_LOAD()


class Logistics(Sequence):
    def __init__(self, player: Player):
        self.player = player
        self.model = LogisticsModel(player)

    def _enabled(self):
        print("Укажите режим")
        modes = [
            ['Cargo', Modes.CARGOHOLD],
            ['Mineral', Modes.MINERAL]
        ]
        i = 1
        for mode in modes:
            print("[%d] %s" % (i, mode[0]))
            i += 1

        try:
            num = int(input())
        except:
            print("Ну нихуя непонятно же")
            raise
        self.model.mode = modes[num-1][1]
        logging.info("logistics enabled")

    def _disabled(self):
        logging.info("logistics disbled")

    async def _loop_func(self):
        if self.model.state is States.LOAD:
            await self.model.load()

        if self.model.state is States.TRAVEL:
            await self.model.travel()

        if self.model.state is States.UNLOAD:
            await self.model.unload()

        if self.model.state is States.RETURN:
            await self.model.returna()
