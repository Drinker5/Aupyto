import asyncio
import win32gui
import win32api
import win32con
import win32process
import pyautogui
from PIL import Image
import random


def findWindowCallback(hwnd, extra):
    windows = extra[0]
    proc_name_2_find = extra[1]

    if not win32gui.IsWindowVisible(hwnd):
        return
    text = win32gui.GetWindowText(hwnd)
    if text == '':
        return
    tId, pId = win32process.GetWindowThreadProcessId(hwnd)
    try:
        handle = win32api.OpenProcess(
            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pId)
    except:
        return

    proc_name = win32process.GetModuleFileNameEx(handle, 0)
    #print("Found \'%s\' (hwnd: %d, tid: %d, pid: %d) '%s'" % (text, hwnd, tId, pId, proc_name))
    if proc_name.find(proc_name_2_find) == -1:
        return

    windows.append((hwnd, tId, pId, text))


def findWindow(proc_name_2_find):
    windows = []
    win32gui.EnumWindows(findWindowCallback, [windows, proc_name_2_find])
    return windows


def find_bitmap(haystack: Image, needle: Image, confidence: float) -> tuple[int, int, int, int]:
    return pyautogui.locate(needle, haystack, grayscale=False, confidence=confidence)


def find_every_bitmap(haystack: Image, needle: Image, confidence: float) -> list[(int, int, int, int)]:
    return list(pyautogui.locateAll(needle, haystack, grayscale=False, confidence=confidence))


def get_relative_click_point(search_rect: tuple[int, int, int, int], found_pos: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (search_rect[0] + found_pos[0],
            search_rect[1] + found_pos[1],
            found_pos[2],
            found_pos[3])


def get_click_point(rect, base=(0, 0)):
    rand = 0.2 + random.random() * 0.6
    delta = (int(rect[2]*rand), int(rect[3]*rand))
    return (base[0] + rect[0] + delta[0],
            base[1] + rect[1] + delta[1])


def click(hwnd, rect):
    x, y = get_click_point(rect)
    lparam = createLParam(int(x), int(y))
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 1, lparam)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

def keyboard(hwnd, char):
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, ord(char), 0)
    win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, ord(char), 0)

def createLParam_from_point(point: tuple[int, int]):
    return createLParam(int(point[0]), int(point[1]))


def createLParam(lo: int, hi: int):
    return (hi << 16) | (lo & 0xffff)

def chance(percent: float):
    if percent > 1:
        percent /= 100.0
    return random.random() < percent

def levenshtein_distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]