import win32gui
import win32com.client
import pythoncom
import PIL.ImageGrab
import ctypes
from pywintypes import error as PyWinError
import logging
from .Screenshot import Screenshot
from ..errors import (
    ProcessNotFoundException,
    parse_pywin_error,
)


PROCESS_LABEL = "女神Online光速版"


class GameController:
    def __init__(self, process_label=PROCESS_LABEL):
        self.window_handle = win32gui.FindWindow(None, process_label)
        if self.window_handle == 0:
            raise ProcessNotFoundException(
                f"Cannot find process with name {process_label}"
            )
        self.activate_game()

    def get_window_dimension(self):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            x1, y1, x2, y2 = win32gui.GetWindowRect(self.window_handle)
            return (x1, y1), (x2, y2)
        except PyWinError as e:
            logging.exception("Failed to retrieve window dimension")
            raise parse_pywin_error(e)

    def activate_game(self):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            (x1, y1), (x2, y2) = self.get_window_dimension()
            win32gui.MoveWindow(
                self.window_handle,
                x1,
                y1,
                x2 - x1,
                y2 - y1,
                True
            )
            win32gui.SetForegroundWindow(self.window_handle)
        except PyWinError as e:
            logging.exception("Failed to activate game")
            raise parse_pywin_error(e)

    def take_screenshot(self):
        pythoncom.CoInitialize()
        self.activate_game()
        (x1, y1), (x2, y2) = self.get_window_dimension()
        return Screenshot(PIL.ImageGrab.grab(bbox=(
            x1,
            y1,
            x2,
            y2
        )))
