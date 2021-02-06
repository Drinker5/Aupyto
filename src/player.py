from collections import namedtuple
import win32gui
import enum
import asyncio
import random
from .LDPlayer960x540 import Coordinates, Images
import src.functions as functions
from transitions import Machine
from .bitmap_capture import IBitmapCapture
from PIL import Image, ImageChops, ImageFilter, ImageEnhance
import pytesseract
import re
import logging
from datetime import datetime, timedelta
#pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract'
from dataclasses import dataclass


@dataclass
class Local:
    alies: int
    fleet: int
    greens: int
    minuses: int
    pluses: int

    @property
    def all(self) -> int:
        return self.alies+self.fleet+self.greens+self.minuses+self.pluses

    @property
    def neutrals(self) -> int:
        return 5 - self.all

    @property
    def is_friendly(self) -> bool:
        if self.minuses > 0 or self.neutrals > 0:
            return False
        if self.all > 5: # recognize error
            return False

        return True


class AutopilotStatus(enum.Enum):
    UNKNOWN = 0
    DISABLED = 1
    ENABLED = 2
    STOPPED = 3


class MissionStatus(enum.Enum):
    UNKNOWN = 0
    FAILED = 1
    NORMAL = 2


class InfoStatus(enum.Enum):
    UNKNOWN = 0
    EMPTY = 1
    PREPARE_FOR_WARP = 2
    JUMP_TO = 3
    ARRIVING_AT = 4
    SHIP_STOPPING = 5


class Player:
    CONFIDENCE = 0.8
    randomSecondsToSleep = (0, 1)
    """Ну типа эмулятор-player"""

    def __init__(self, bitmap_capture: IBitmapCapture, hwnd, name="undefined"):
        self._bitmap_capture = bitmap_capture
        self.gamehwnd = hwnd
        self.name = name

    # region Space methods
    def get_info(self) -> InfoStatus:
        haystack = self.get_part_of_screen(Coordinates.Space.info_rect)
        haystack = haystack.quantize(colors=8)
        info_string = pytesseract.image_to_string(
            haystack, config='--psm 7')
        if re.match('ARRIVING', info_string):
            return InfoStatus.ARRIVING_AT
        elif re.match('PREPARE', info_string):
            return InfoStatus.PREPARE_FOR_WARP
        elif re.match('JUMP', info_string):
            return InfoStatus.JUMP_TO
        elif re.match('SHIP_STOPPING', info_string):
            return InfoStatus.SHIP_STOPPING
        elif info_string.strip() == "":
            return InfoStatus.EMPTY
        return InfoStatus.UNKNOWN

    def is_ship_stopped(self) -> bool:
        haystack = self.get_part_of_screen(Coordinates.window_rect)
        pixel = haystack.getpixel(Coordinates.Space.check_warp_pixel)
        return pixel == Coordinates.Space.not_in_warp_pixel_color

    def is_engine_enabled(self):
        pos = self.find_in_rect(
            Coordinates.Space.engine_100_rect,
            Images.engine_100, 0.99)
        return pos != None

    """
        module_number - номер модуля, счет права налево, снизу вверх
        grid - 8 или 12, количество модулей в сетке
    """
    async def click_module(self, module_number: int, grid: int = 8):
        await self.click(Coordinates.Space.modules[grid][module_number], 0.2)
    async def close_bookmarks(self):
        await self.click(Coordinates.Space.Bookmarks.close_bookmarks_button, 1)

    # def get_module_8_cd_info(self, module_number: int) -> str:
    #     haystack = self.get_part_of_screen(
    #         Coordinates.Space.modules_8[module_number])
    #     invertHayStack = ImageChops.invert(haystack)
    #     info_string = pytesseract.image_to_string(invertHayStack)
    #     return info_string.strip()
    # endregion

    # region Grid methods
    async def change_grid_filter(self, number):
        await self.click(Coordinates.Space.Grid.change_grid_dropdown_rect, 0.1)
        await self.click(Coordinates.Space.Grid.filters[number])

    async def grid_expand(self):
        await self.click(Coordinates.Space.Grid.change_grid_dropdown_rect, 0.1)
        await self.click(Coordinates.Space.Grid.change_grid_dropdown_rect, 0.1)

    def get_warp_command_pos(self):
        return self.find_in_rect(
            Coordinates.Space.Grid.target_commands_rect, Images.warp_command)

    def get_lock_command_pos(self):
        return self.find_in_rect(
            Coordinates.Space.Grid.target_commands_rect, Images.lock_command)

    def get_approach_command_pos(self):
        return self.find_in_rect(
            Coordinates.Space.Grid.target_commands_rect, Images.approach_command, 0.77)

    def get_locked_target_approach_command_pos(self):
        return self.find_in_rect(
            Coordinates.Space.Grid.locked_target_commands_rect, Images.approach_command, 0.77)

    async def click_command(self, pos):
        await self.click_relative(Coordinates.Space.Grid.target_commands_rect, pos)

    async def click_locked_target_command(self, pos):
        await self.click_relative(Coordinates.Space.Grid.locked_target_commands_rect, pos)

    async def select_locked_target(self, target_num):
        if target_num == 0:
            await self.click(Coordinates.Space.Grid.first_lockable_target_rect)
    # end region

    # region Menu methods
    async def open_inventory(self):
        await self.click(Coordinates.Menu.inventory_button)

    async def open_encounters(self):
        await self.click(Coordinates.Menu.encountersButton, 3)

    def is_inventory_visible(self):
        pos = self.find_in_rect(
            Coordinates.Menu.inventory_button, Images.inventory)
        return pos != None
    # endregion

    # region Encounters methods
    async def open_news(self):
        await self.click(Coordinates.Encounters.newsButton)

    async def open_journal(self):
        await self.click(Coordinates.Encounters.journalButton)

    async def select_first_accepted_mission(self):
        await self.click(Coordinates.Encounters.first_accepted_mission_rect)

    async def select_first_accepted_mission_react_button(self):
        await self.click(Coordinates.Encounters.first_accepted_mission_react_button)

    def is_any_news_in_journal(self):
        pos = self.find_in_rect(
            Coordinates.Encounters.journalButton, Images.journal_have_items)
        return pos != None

    def get_accepted_mission_status(self):
        pos = self.find_in_rect(
            Coordinates.Encounters.Journal.first_accepted_mission_rect, Images.journal_delivery_mission_failed, 0.99)
        if pos:
            return MissionStatus.FAILED
        pos = self.find_in_rect(
            Coordinates.Encounters.Journal.first_accepted_mission_rect, Images.journal_delivery_mission_normal, 0.99)
        if pos:
            return MissionStatus.NORMAL
        return MissionStatus.UNKNOWN

    def get_mission_time(self) -> str:
        haystack = self.get_part_of_screen(
            Coordinates.Encounters.Journal.time_rect)
        invertHayStack = ImageChops.invert(haystack)
        timeString = pytesseract.image_to_string(
            invertHayStack, config='--psm 6')
        res = re.match(r'.*(\d\d):(\d\d):(\d\d).*', timeString)
        if res is None:
            return None

        parse_result = "%s:%s:%s" % (res[1], res[2], res[3])
        logging.info('parsed mission time: %s' % (parse_result))
        return parse_result

    async def press_mission_begin(self):
        await self.click(Coordinates.Encounters.Journal.mission_begin_button)

    async def press_mission_abandon(self):
        await self.click(Coordinates.Encounters.Journal.mission_abandon_button)

    def get_mission_stage(self):
        haystack = self.get_part_of_screen(
            Coordinates.Encounters.Journal.stage_rect)
        invertHayStack = ImageChops.invert(haystack)
        timeString = pytesseract.image_to_string(
            invertHayStack, config='--psm 6')
        res = re.match(r'.*(\d)/\d.*', timeString)
        if res is None:
            return None
        parse_result = int(res[1])
        logging.info('parsed mission stage: %d' % (parse_result))
        return parse_result

    # endregion

    # region News methods
    def get_news_with_chains(self):
        haystack = self.get_part_of_screen(
            Coordinates.Encounters.News.news_rect)
        return self.find_needles_in_haystack(haystack, Images.news_chain, 0.95)

    async def accept_news(self, chain_box):
        news_rect = Coordinates.Encounters.News.news_rect
        delta = Coordinates.Encounters.News.accept_delta
        accept_rect = (
            news_rect[0] + chain_box[0] + delta[0],
            news_rect[1] + chain_box[1] + delta[1],
            0, 0)
        await self.click(accept_rect)

    async def refresh_news(self):
        await self.click(Coordinates.Encounters.News.refresh_button)

    def get_refresh_cooldown(self) -> timedelta:
        haystack = self.get_part_of_screen(
            Coordinates.Encounters.News.refresh_button)
        invertHayStack = ImageChops.invert(haystack)
        timeString = pytesseract.image_to_string(
            invertHayStack, config='--psm 6')
        #refresh = re.match(r'.*(Refresh).*', timeString)
        res = re.match(r'.*(\d\d):(\d\d):(\d\d).*', timeString)
        if res is None:
            return None

        logging.info('parsed refresh time: %s:%s:%s' %
                     (res[1], res[2], res[3]))
        return timedelta(hours=int(res[1]), minutes=int(res[2]), seconds=int(res[3]))
    # endregion

    # region Main methods
    def is_docked(self):
        pos = self.find_in_rect(
            Coordinates.undock_button, Images.docked)
        return pos != None

    async def press_undock_citadel_button(self):
        await self.click(Coordinates.undock_button_citadel)

    def is_docked_citadel(self):
        pos = self.find_in_rect(
            Coordinates.undock_button_citadel, Images.docked_citadel)
        return pos != None

    def is_npc_dialog_with_reply_showing(self):
        haystack = self.get_part_of_screen(
            Coordinates.npc_dialog_with_reply_rect)
        pos = self.find_needles_in_haystack(
            haystack, Images.npc_dialog_reply, 0.99)
        return len(pos) > 0

    async def press_npc_dialog_first_reply(self):
        await self.click(Coordinates.npc_dialog_first_reply_rect)

    async def press_npc_dialog(self):
        await self.click(Coordinates.npc_dialog_rect)

    def is_confirm_dialog_showing(self):
        pos = self.find_in_rect(
            Coordinates.dialog_confirm_button, Images.dialog_showing)
        return pos != None

    async def press_dialog_cancel_button(self):
        await self.click(Coordinates.dialog_cancel_button)

    async def press_dialog_confirm_button(self):
        await self.click(Coordinates.dialog_confirm_button)

    async def toggle_autopilot(self):
        await self.click(Coordinates.autopilot_rect)

    def get_autopilot_status(self) -> AutopilotStatus:
        pos = self.find_in_rect(
            Coordinates.autopilot_rect, Images.autopilot_disabled, 0.95)
        if pos:
            return AutopilotStatus.DISABLED
        pos = self.find_in_rect(
            Coordinates.autopilot_rect, Images.autopilot_enabled)
        if pos:
            return AutopilotStatus.ENABLED
        pos = self.find_in_rect(
            Coordinates.autopilot_rect, Images.autopilot_stopped)
        if pos:
            return AutopilotStatus.STOPPED
        return AutopilotStatus.UNKNOWN

    async def open_menu(self):
        await self.click(Coordinates.menuButton)

    async def close(self):
        await self.click(Coordinates.closeButton)

    async def press_first_quick_button(self):
        await self.click(Coordinates.quick_panel_first_button_rect)

    def get_inventory_load_percent(self):
        def binary_search(haystack: Image, y: int, pixel_color: tuple[int, int, int]):
            low = 0
            high = haystack.size[0] - 1
            mid = 0
            while low <= high:
                mid = (high + low) >> 1
                pixel = haystack.getpixel((mid, y))
                if pixel == pixel_color:
                    low = mid + 1
                elif high == mid:
                    return mid
                else:
                    high = mid
            return -1

        haystack = self.get_part_of_screen(
            Coordinates.quick_panel_first_button_rect)
        # haystack.save("test.png")
        pixel_color = (39, 102, 85)
        line_y = haystack.size[1]-1
        x = binary_search(haystack, line_y, pixel_color)
        if x == -1:
            return 1.0

        return round(x / haystack.size[0], 2)
    # endregion

    # region Local
    def get_local_window_position(self):
        pos = self.find_in_rect(
            Coordinates.Local.local_window_rect, Images.local_window, 0.90)
        if pos == None:
            return None
        return functions.get_relative_click_point(Coordinates.Local.local_window_rect, pos)

    def get_local(self) -> Local:
        pos = self.get_local_window_position()
        if pos == None:
            return None

        haystack = self.get_part_of_screen(
            functions.get_relative_click_point(
                pos,
                Coordinates.Local.users_relative_rect))
        confidence = 0.92
        allies = self.find_needles_in_haystack(
            haystack, Images.standings_ally, confidence)
        fleets = self.find_needles_in_haystack(
            haystack, Images.standings_fleet, confidence)
        greens = self.find_needles_in_haystack(
            haystack, Images.standings_green, confidence)
        minuses = self.find_needles_in_haystack(
            haystack, Images.standings_minus, confidence)
        pluses = self.find_needles_in_haystack(
            haystack, Images.standings_plus, confidence)
        return Local(
            alies=len(allies),
            fleet=len(fleets),
            greens=len(greens),
            minuses=len(minuses),
            pluses=len(pluses))

    """ Использует макрос на Keybind 'A' """
    async def scroll_local(self, times):
        i = 0
        while i < times:
            functions.keyboard(self.gamehwnd, 'A')
            await asyncio.sleep(2.5)
            i += 1
    # endregion

    # region Inventory methods
    async def press_item_hangar_button(self):
        await self.click(Coordinates.Inventory.item_hangar_button)

    async def press_select_all_button(self):
        await self.click(Coordinates.Inventory.select_all_button)

    def get_move_to_window_pos(self):
        pos = self.find_in_rect(
            Coordinates.window_rect,
            Images.move_to_window)
        return pos


    async def press_move_to_button(self):
        await self.click(Coordinates.Inventory.move_to_button, 1)

    async def press_move_to_item_hangar_button(self):
        await self.click(Coordinates.Inventory.move_to_item_hangar_button, 5)

    async def press_additional_cargo_open(self):
        pos = self.get_additional_cargo_position()
        if pos == None:
            logging.error("additional cargo not found")
        click_rect = functions.get_relative_click_point(
            Coordinates.Inventory.additional_cargo_search_rect, pos)

        await self.click(click_rect, 1)

    async def press_delivery_hold_additional_cargo(self):
        pos = self.get_delivery_hold_additional_cargo_position()
        if pos == None:
            logging.error("delivery hold not found")

        click_rect = functions.get_relative_click_point(
            Coordinates.Inventory.delivery_hold_additional_cargo_search_rect, pos)
        await self.click(click_rect)

    def is_select_all_active(self):
        pos = self.find_in_rect(
            Coordinates.Inventory.move_to_button,
            Images.move_to)
        return pos != None

    def get_additional_cargo_position(self):
        pos = self.find_in_rect(
            Coordinates.Inventory.additional_cargo_search_rect,
            Images.additional_cargo, 0.6)
        return pos

    def get_delivery_hold_additional_cargo_position(self):
        pos = self.find_in_rect(
            Coordinates.Inventory.delivery_hold_additional_cargo_search_rect,
            Images.delivery_hold)
        return pos

    async def press_ore_hold_button(self):
        await self.click(Coordinates.Inventory.ore_hold_button, 4)
    # endregion

    def get_part_of_screen(self, rect) -> Image:
        return self._bitmap_capture.get_part_of_image(rect)

    def find_in_rect(self, coordinates: tuple[int, int, int, int], image: Image, confidence=CONFIDENCE) -> tuple[int, int, int, int]:
        haystack = self.get_part_of_screen(coordinates)
        return functions.find_bitmap(haystack, image, confidence)

    def find_needle_in_haystack(self, haystack: Image, image: Image, confidence=CONFIDENCE) -> tuple[int, int, int, int]:
        return functions.find_bitmap(haystack, image, confidence)

    def find_needles_in_haystack(self, haystack: Image, image: Image, confidence=CONFIDENCE) -> list[(int, int, int, int)]:
        im1 = self.enchance_image(haystack)
        im2 = self.enchance_image(image)
        return functions.find_every_bitmap(im1, im2, confidence)

    def enchance_image(self, im: Image):
        im = im.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(2)
        return im

    async def click_relative(self, relative_rect, pos):
        click_rect = functions.get_relative_click_point(relative_rect, pos)
        await self.click(click_rect)

    async def click(self, rect, sleep: float = 2.0):
        functions.click(self.gamehwnd, rect)
        deltaSleep = self.randomSecondsToSleep[0] + \
            random.random() * self.randomSecondsToSleep[1]
        await asyncio.sleep(sleep + deltaSleep)
