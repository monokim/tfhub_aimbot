from __future__ import annotations

import math
import time

import win32api
import win32con

from ..config import AppConfig
from ..utils.target_selector import AimDelta


class MouseController:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def _scaleAxis(self, value: int, scale: float) -> int:
        if value == 0:
            return 0
        scaledValue = int(round(value * scale))
        if scaledValue == 0:
            return 1 if value > 0 else -1
        return scaledValue

    def _clamp(self, value: int, stepLimit: int) -> int:
        safeStepLimit = max(1, stepLimit)
        return max(-safeStepLimit, min(safeStepLimit, value))

    def _resolveAdaptiveStepLimit(self, distance: float) -> int:
        nearStep = max(1, self.config.control.adaptiveStepNearMaxStep)
        farStep = max(nearStep, self.config.control.maxStep)
        farDistancePx = max(1.0, self.config.control.adaptiveStepFarDistancePx)
        stepCurve = max(0.5, self.config.control.adaptiveStepCurve)
        distanceRatio = min(1.0, distance / farDistancePx)
        curvedRatio = distanceRatio**stepCurve
        blendedStep = nearStep + ((farStep - nearStep) * curvedRatio)
        return int(round(blendedStep))

    def _applyCloseRangeDamping(self, delta: AimDelta) -> AimDelta:
        deadzonePx = max(0, self.config.control.deadzonePx)
        slowRadiusPx = max(deadzonePx + 1, self.config.control.slowRadiusPx)
        minSlowScale = max(0.05, min(1.0, self.config.control.minSlowScale))
        distance = math.hypot(delta.dx, delta.dy)

        if distance <= deadzonePx:
            return AimDelta(dx=0, dy=0)
        if distance >= slowRadiusPx:
            return delta

        ratio = distance / float(slowRadiusPx)
        dampScale = max(minSlowScale, ratio)
        return AimDelta(
            dx=self._scaleAxis(delta.dx, dampScale),
            dy=self._scaleAxis(delta.dy, dampScale),
        )

    def _applyBoost(self, delta: AimDelta) -> AimDelta:
        if not self.config.control.boostEnabled:
            return delta

        distance = math.hypot(delta.dx, delta.dy)
        startPx = max(1.0, self.config.control.boostStartPx)
        if distance <= startPx:
            return delta

        scale = min(self.config.control.boostMaxScale, distance / startPx)
        boostedDx = int(delta.dx * scale)
        boostedDy = int(delta.dy * scale)
        return AimDelta(dx=boostedDx, dy=boostedDy)

    def move(self, delta: AimDelta) -> None:
        dampedDelta = self._applyCloseRangeDamping(delta)
        if dampedDelta.dx == 0 and dampedDelta.dy == 0:
            return

        boostedDelta = self._applyBoost(dampedDelta)
        boostedDistance = math.hypot(boostedDelta.dx, boostedDelta.dy)
        adaptiveStepLimit = self._resolveAdaptiveStepLimit(boostedDistance)
        moveDx = self._clamp(boostedDelta.dx, adaptiveStepLimit)
        moveDy = self._clamp(boostedDelta.dy, adaptiveStepLimit)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, moveDx, moveDy, 0, 0)
        if self.config.control.moveSleepSec > 0:
            time.sleep(self.config.control.moveSleepSec)

    def click(self) -> None:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        if self.config.control.clickHoldSec > 0:
            time.sleep(self.config.control.clickHoldSec)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def moveAndAction(self, delta: AimDelta) -> None:
        self.move(delta)
        if self.config.control.autoFire:
            self.click()
