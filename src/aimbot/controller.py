from __future__ import annotations

import time

import win32api
import win32con

from .config import AppConfig
from .target_selector import AimDelta


class MouseController:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def move_and_click(self, delta: AimDelta) -> None:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, delta.dx, delta.dy, 0, 0)
        time.sleep(self.config.move_sleep_sec)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, delta.dx, delta.dy, 0, 0)
        time.sleep(self.config.click_hold_sec)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, delta.dx, delta.dy, 0, 0)
