# pylint: disable=maybe-no-member
from asyncio.tasks import sleep
from src.sequence import Module, Sequence
from .player import Player, MissionStatus
from transitions.extensions.asyncio import AsyncMachine
import asyncio
import enum
import logging
import random
import csv
from datetime import datetime, timedelta
from .autopilot import Autopilot
import src.functions as functions

class States(enum.Enum):
    CHILL = 0
    GETTING_NEXT_MISSION = 1
    ACCEPTING_NEWS = 3
    MISSION_SELECTED = 4
    CHECKING_MISSION = 5

    MISSION_STAGE_0 = 10
    MISSION_STAGE_1 = 11
    MISSION_STAGE_2 = 12
    MISSION_STAGE_3 = 13


class DeliveringModel:
    mission_complete_count = 0
    TIME_TO_ABANDON = '00:30:00'
    last_refresh_time = datetime.now() - timedelta(days=1)

    def __init__(self, player: Player):
        self.player = player
        self.start_time = datetime.now()
        self.mission_start_time = None
        self.autopilot = Autopilot(player, [
            Module(position=0, cd=timedelta(seconds=60),
                   activation_time=timedelta(seconds=10)),
            Module(position=1, cd=timedelta(seconds=60),
                   activation_time=timedelta(seconds=10)),
            Module(position=2, cd=timedelta(seconds=60),
                   activation_time=timedelta(seconds=10)),
        ])

    async def get_next_mission(self):
        await self.to_getting_next_mission()

    ''' пытаемся начать миссию,
        если есть просроченные миссии, они прокликиваются
        если нет миссий переходим в состояние NO_MISSIONS '''
    async def getting_next_mission(self):
        await self.player.open_menu()
        await self.player.open_encounters()
        if self.player.is_any_news_in_journal():
            await self.player.select_first_accepted_mission()
            time = self.player.get_mission_time()
            # значит нажали на просроченную миссию
            # или не успело прогрузится
            if time == None:
                await self.to_chill()
                await self.player.close()
                return

            if time > self.TIME_TO_ABANDON:
                await self.player.press_mission_begin()
                await self.to_mission_selected_state()
            else:  # срок, можно не успеть завершить, отменяем
                await self.player.press_mission_abandon()
                await self.player.press_dialog_confirm_button()
                await self.to_chill()
                await self.player.close()
        else:
            await self.to_accepting_news_state()
            await self.player.close()

    async def accepting_news(self):
        await self.player.open_menu()
        await self.player.open_encounters()
        await self.player.open_news()

        chain_boxes = self.player.get_news_with_chains()
        logging.info("seeing %d missions" % (len(chain_boxes)))
        if len(chain_boxes) > 0:
            box = chain_boxes[0]
            await self.player.accept_news(box)
            chain_boxes_after_picking = self.player.get_news_with_chains()

            while self.player.is_confirm_dialog_showing():
                await self.player.press_dialog_confirm_button()
            # если это была единственная новость, то обновим список заранее
            if len(chain_boxes_after_picking) <= 0:
                await self.player.refresh_news()
            await self.to_chill()
        else:
            delta = self.player.get_refresh_cooldown()
            if delta != None:
                logging.info("refresh waiting %d seconds" % (delta.seconds + 3))
                await asyncio.sleep(delta.seconds + 3)
            
            # afk перед рефрешом новостей
            if functions.chance(50):
                sleep_time = random.randint(30, 120)
                logging.info("afk sleeping %d seconds" % (sleep_time))
                await asyncio.sleep(sleep_time)
                
            await self.player.refresh_news()

        await self.player.close()

    async def checking_mission(self):
        stage = self.player.get_mission_stage()
        if stage == 0:
            await self.to_mission_stage_0_state()
        elif stage == 1:
            await self.to_mission_stage_1_state()
        elif stage == 2:
            await self.to_mission_stage_2_state()
        elif stage == 3:
            await self.to_mission_stage_3_state()
        else:
            logging.error('нераспарсил этап')
            await self.player.close()
            await self.player.close()
            await self.to_chill()

    async def complete_stage_0(self):
        self.mission_start_time = datetime.now()
        while not self.player.is_confirm_dialog_showing():
            await self.player.press_mission_begin()
        await self.player.press_dialog_cancel_button()
        await self.to_mission_stage_1_state()

    async def autopilot_time(self):
        while not self.player.is_engine_enabled():  # undocking
            await asyncio.sleep(1)
        self.autopilot.enable()
        while not self.player.is_docked():  # flying
            await asyncio.sleep(5)
        self.autopilot.disable()

    async def complete_stage_1(self):
        if self.mission_start_time == None:
            self.mission_start_time = datetime.now()

        # undock
        await self.player.press_mission_begin()
        await self.player.press_dialog_confirm_button()
        await self.player.press_dialog_confirm_button()
        await self.autopilot_time()
        await asyncio.sleep(5)  # ждём окошка диалога

        while not self.player.is_confirm_dialog_showing():
            await self.player.press_npc_dialog()

        # говорит чтобы принял груз, отменяем
        await self.player.press_dialog_cancel_button()

        # досылка груза в доп карго
        await self.player.open_menu()

        # npc диалог можеть всё ещё висеть
        while not self.player.is_inventory_visible():
            await self.player.press_npc_dialog()

        # после диалога груз автоматически попадает в доп. отсек
        # выбираем миссию для старта следующего этапа
        # меню уже было открыто выше
        await self.player.open_encounters()
        await self.player.select_first_accepted_mission()
        await self.to_mission_stage_2_state()

    # груз должен быть на борту

    async def complete_stage_2(self):
        if self.mission_start_time == None:
            self.mission_start_time = datetime.now()

        # undock
        await self.player.press_mission_begin()
        await self.player.press_dialog_confirm_button()
        await self.player.press_dialog_confirm_button()
        await self.autopilot_time()
        # ждём окошка диалога

        while not self.player.is_npc_dialog_with_reply_showing():
            await asyncio.sleep(3)

        # afk перед здачей миссии
        if functions.chance(50):
            sleep_time = random.randint(30, 120)
            logging.info("afk sleeping %d seconds" % (sleep_time))
            await asyncio.sleep(sleep_time)

        await self.player.press_npc_dialog_first_reply()

        await self.player.open_menu()
        while not self.player.is_inventory_visible():
            await self.player.press_npc_dialog()
        await self.player.close()

        self.mission_end_time = datetime.now()
        self.mission_complete_count += 1
        logging.info("За сессию пройдено миссий: %d" %
                     (self.mission_complete_count))
        session_time = datetime.now() - self.start_time
        days, seconds = session_time.days, session_time.seconds
        logging.info("Время сессии: %02d:%02d:%02d" % (
            days * 24 + seconds // 3600, (seconds % 3600) // 60, seconds % 60))

        if self.mission_start_time != None:
            mission_time = self.mission_end_time - self.mission_start_time
            days, seconds = mission_time.days, mission_time.seconds
            logging.info("Время выполнения миссии: %02d:%02d:%02d" % (
                days * 24 + seconds // 3600, (seconds % 3600) // 60, seconds % 60))

            with open('D:/temp/delivering.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow([self.player.name,
                                 self.mission_start_time,
                                 self.mission_end_time])

        await self.to_chill()

    async def complete_stage_3(self):
        await self.player.press_mission_begin()
        await self.player.press_npc_dialog()
        await self.player.press_npc_dialog()
        await self.player.press_npc_dialog()
        await self.player.close()

        self.mission_end_time = datetime.now()
        await self.to_chill()


class Delivering(Sequence):
    __transitions = [
        {'trigger': 'to_getting_next_mission',
         'source': States.CHILL,
         'dest': States.GETTING_NEXT_MISSION},

        {'trigger': 'to_mission_selected_state',
         'source': States.GETTING_NEXT_MISSION,
         'dest': States.MISSION_SELECTED},

        {'trigger': 'to_accepting_news_state',
         'source': States.GETTING_NEXT_MISSION,
         'dest': States.ACCEPTING_NEWS},

        {'trigger': 'check_mission',
         'source': States.MISSION_SELECTED,
         'dest': States.CHECKING_MISSION,
         'after': 'checking_mission'},

        {'trigger': 'to_mission_stage_0_state',
         'source': States.CHECKING_MISSION,
         'dest': States.MISSION_STAGE_0},

        {'trigger': 'to_mission_stage_1_state',
         'source': [States.CHECKING_MISSION, States.MISSION_STAGE_0],
         'dest': States.MISSION_STAGE_1},

        {'trigger': 'to_mission_stage_2_state',
         'source': [States.CHECKING_MISSION, States.MISSION_STAGE_1],
         'dest': States.MISSION_STAGE_2},

        {'trigger': 'to_mission_stage_3_state',
         'source': [States.CHECKING_MISSION],
         'dest': States.MISSION_STAGE_3},

        {'trigger': 'to_chill',
         'source': [States.GETTING_NEXT_MISSION,
                    States.ACCEPTING_NEWS,
                    States.CHECKING_MISSION,
                    States.MISSION_STAGE_2,
                    States.MISSION_STAGE_3],
         'dest': States.CHILL}
    ]

    def __init__(self, player: Player):
        self.player = player
        self.model = DeliveringModel(player)
        self._machine = AsyncMachine(self.model,
                                        states=States,
                                        transitions=self.__transitions,
                                        initial=States.CHILL,
                                        auto_transitions=False)

    def _enabled(self):
        logging.info("delivering enabled")

    def _disabled(self):
        logging.info("delivering disbled")

    async def _loop_func(self):
        if self.model.state is States.CHILL:
            await self.model.get_next_mission()

        if self.model.state is States.GETTING_NEXT_MISSION:
            await self.model.getting_next_mission()

        if self.model.state is States.ACCEPTING_NEWS:
            await self.model.accepting_news()

        if self.model.state is States.MISSION_SELECTED:
            await self.model.check_mission()

        if self.model.state is States.MISSION_STAGE_0:
            await self.model.complete_stage_0()

        if self.model.state is States.MISSION_STAGE_1:
            await self.model.complete_stage_1()

        if self.model.state is States.MISSION_STAGE_2:
            await self.model.complete_stage_2()

        if self.model.state is States.MISSION_STAGE_3:
            await self.model.complete_stage_3()