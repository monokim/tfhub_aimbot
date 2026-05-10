from __future__ import annotations

from dataclasses import dataclass

import cv2
import mss
import numpy as np
import win32gui

from ..config import AppConfig


@dataclass
class FrameData:
    image: np.ndarray
    width: int
    height: int


class WindowCapture:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.screenGrabber = mss.mss()

    def _windowRect(self) -> tuple[int, int, int, int]:
        hwnd = win32gui.FindWindow(None, self.config.window.title)
        if not hwnd:
            raise RuntimeError(f"Window not found: {self.config.window.title}")
        return win32gui.GetWindowRect(hwnd)

    def _regionFromRect(self, rect: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1

        if not self.config.window.roiEnabled:
            return x1, y1, width, height

        roiWidth = min(self.config.window.roiWidth, width)
        roiHeight = min(self.config.window.roiHeight, height)
        centerX = x1 + width // 2
        centerY = y1 + height // 2
        roiX = centerX - roiWidth // 2
        roiY = centerY - roiHeight // 2
        return roiX, roiY, roiWidth, roiHeight

    def grab(self) -> FrameData:
        rect = self._windowRect()
        regionX, regionY, regionWidth, regionHeight = self._regionFromRect(rect)
        monitor = {
            "left": regionX,
            "top": regionY,
            "width": max(1, regionWidth),
            "height": max(1, regionHeight),
        }

        rawImage = self.screenGrabber.grab(monitor)
        frameBgra = np.asarray(rawImage, dtype=np.uint8)
        frameRgb = cv2.cvtColor(frameBgra, cv2.COLOR_BGRA2RGB)

        if self.config.capture.sizeScale > 1:
            targetWidth = max(1, frameRgb.shape[1] // self.config.capture.sizeScale)
            targetHeight = max(1, frameRgb.shape[0] // self.config.capture.sizeScale)
            frameRgb = cv2.resize(frameRgb, (targetWidth, targetHeight), interpolation=cv2.INTER_LINEAR)

        return FrameData(image=frameRgb, width=frameRgb.shape[1], height=frameRgb.shape[0])

    def close(self) -> None:
        self.screenGrabber.close()

