from __future__ import annotations

import time

import win32api


class ToggleKeyHook:
    def __init__(self, virtualKeyCode: int, debounceMs: int) -> None:
        self.virtualKeyCode = virtualKeyCode
        self.debounceSec = max(0.0, debounceMs / 1000.0)
        self.lastPressed = False
        self.lastToggleAt = 0.0

    def consumeToggle(self) -> bool:
        state = win32api.GetAsyncKeyState(self.virtualKeyCode)
        pressed = bool(state & 0x8000)
        pressedSinceLastCall = bool(state & 0x0001)
        now = time.perf_counter()
        risingEdgePressed = pressed and not self.lastPressed
        shouldToggle = (pressedSinceLastCall or risingEdgePressed) and (
            (now - self.lastToggleAt) >= self.debounceSec
        )
        self.lastPressed = pressed
        if shouldToggle:
            self.lastToggleAt = now
        return shouldToggle
