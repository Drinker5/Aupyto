# pylint: disable=maybe-no-member
import logging
import asyncio
import ctypes
from src.logistics import Logistics
from src.local_checking import LocalChecking
from src.mining import Mining
from src.autopilot import Autopilot
import win32gui
import src.functions as functions
from src.LDPlayer960x540 import Coordinates
from src.player import Player
from src.sequence import Module
from src.delivering import Delivering
from src.bitmap_capture import ScreenCaputre
from datetime import timedelta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
PROC_TO_FIND = 'dnplayer.exe'


async def main():
    windows = functions.findWindow(PROC_TO_FIND)
    if len(windows) <= 0:
        print("Не нашел окна '%s'" % (PROC_TO_FIND))
        exit()

    num = 1
    print("Укажите окно куда делать привязку")
    point = 1
    for window in windows:
        print("[%d] %s (%d)" % (point, window[3], window[2]))
        point += 1

    try:
        num = int(input())
    except:
        num = 1

    selectedWindow = windows[num-1]
    print("Подключаюсь к %s" % (selectedWindow[3]))
    ctypes.windll.kernel32.SetConsoleTitleW(selectedWindow[3])
    #rect = win32gui.GetWindowRect(selectedWindow[0])
    #gamehwnd = win32gui.WindowFromPoint((rect[0] + Coordinates.delta[0], rect[1] + Coordinates.delta[1]))
    gamehwnd = win32gui.FindWindowEx(
        selectedWindow[0], None, "RenderWindow", None)

    bitmap_capture = ScreenCaputre(gamehwnd)
    player = Player(bitmap_capture, gamehwnd, selectedWindow[3])
    print("Укажите последовательность")
    sequences = [
        ['Delivering', Delivering(player)],
        ['Mining', Mining(player, [
            Module(position=4, cd=timedelta(seconds=1),
                   activation_time=timedelta(minutes=1), grid=12),
            Module(position=5, cd=timedelta(seconds=1),
                   activation_time=timedelta(minutes=1), grid=12)
        ], [
            Module(position=0, cd=timedelta(minutes=1),
                   activation_time=timedelta(seconds=10), grid=12)
        ])],
        ['Local Checking', LocalChecking(player)],
        ['Autopilot', Autopilot(player, [
            Module(position=0, cd=timedelta(seconds=60),
                   activation_time=timedelta(seconds=10)),
            Module(position=1, cd=timedelta(seconds=60),
                   activation_time=timedelta(seconds=10)),
            Module(position=2, cd=timedelta(seconds=60),
                   activation_time=timedelta(seconds=10)),
        ])],
        ['Logistics', Logistics(player)]
    ]
    i = 1
    for sequence in sequences:
        print("[%d] %s" % (i, sequence[0]))
        i += 1

    try:
        num = int(input())
    except:
        print("Ну нихуя непонятно же")
        raise

    sequence = sequences[num-1][1]
    sequence.enable()
    await sequence.loop_task
try:
    asyncio.get_event_loop().run_until_complete(main())
except Exception as e:
    print(e)

print("Press any key to exit...")
input()
