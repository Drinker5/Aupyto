from abc import ABCMeta, abstractmethod
import autopy
import win32gui
import win32ui
import win32con
from .LDPlayer960x540 import Coordinates
from PIL import Image


class IBitmapCapture:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_part_of_image(self, rect) -> Image:
        raise NotImplementedError


class ScreenCaputre(IBitmapCapture):
    _hwnd: int

    def __init__(self, hwnd: int):
        self._hwnd = hwnd

    """https://stackoverflow.com/questions/19695214/python-screenshot-of-inactive-window-printwindow-win32gui"""
    def get_part_of_image(self, rect) -> Image:
        x = rect[0]
        y = rect[1]
        width = rect[2]
        height = rect[3]

        # create a device context
        desktop_dc = win32gui.GetWindowDC(self._hwnd)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)

        # create a memory based device context
        mem_dc = img_dc.CreateCompatibleDC()

        # create a bitmap object
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)

        # copy the screen into our memory device context
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (x, y), win32con.SRCCOPY)

        # save the bitmap to a file
        bmpinfo = screenshot.GetInfo()
        bmpstr = screenshot.GetBitmapBits(True)
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        #im.save('test.png')
        # free our objects
        win32gui.DeleteObject(screenshot.GetHandle())
        mem_dc.DeleteDC()
        img_dc.DeleteDC()
        win32gui.ReleaseDC(self._hwnd, desktop_dc)
        return im


class ImageCapture(IBitmapCapture):
    _bitmap: Image

    def __init__(self, imagePath: str):
        self._bitmap = Image.open(imagePath)

    def get_part_of_image(self, rect) -> Image:
        x1 = rect[0] + Coordinates.delta[0]
        y1 = rect[1] + Coordinates.delta[1]
        x2 = x1 + rect[2]
        y2 = y1 + rect[3]
        return self._bitmap.crop((x1, y1, x2, y2))
