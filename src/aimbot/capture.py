from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import pyautogui
import win32gui

from .config import AppConfig


@dataclass
class FrameData:
    image: np.ndarray
    width: int
    height: int


class WindowCapture:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def _window_rect(self) -> tuple[int, int, int, int]:
        hwnd = win32gui.FindWindow(None, self.config.window_title)
        if not hwnd:
            raise RuntimeError(f"Window not found: {self.config.window_title}")
        return win32gui.GetWindowRect(hwnd)

    def _region_from_rect(self, rect: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        if not self.config.roi_enabled:
            return x1, y1, width, height

        roi_w = min(self.config.roi_width, width)
        roi_h = min(self.config.roi_height, height)
        cx = x1 + width // 2
        cy = y1 + height // 2
        roi_x = cx - roi_w // 2
        roi_y = cy - roi_h // 2
        return roi_x, roi_y, roi_w, roi_h

    def grab(self) -> FrameData:
        rect = self._window_rect()
        region = self._region_from_rect(rect)
        image = np.array(pyautogui.screenshot(region=region))
        image = cv2.resize(
            image,
            (image.shape[1] // self.config.size_scale, image.shape[0] // self.config.size_scale),
        )
        return FrameData(image=image, width=image.shape[1], height=image.shape[0])
