from __future__ import annotations

import math
from dataclasses import dataclass

from ..config import AppConfig
from ..resource.detector import Detection


@dataclass
class AimDelta:
    dx: int
    dy: int


@dataclass
class AimSelection:
    detection: Detection
    targetPoint: tuple[int, int]
    aimOrigin: tuple[int, int]
    delta: AimDelta


class TargetSelector:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def select(self, detections: list[Detection], width: int, height: int) -> AimSelection | None:
        if not detections:
            return None

        bestDetection: Detection | None = None
        bestTargetPoint: tuple[int, int] | None = None
        bestDistance = float("inf")
        centerX = (width / 2.0) + self.config.target.aimOriginOffsetX
        centerY = (height / 2.0) + self.config.target.aimOriginOffsetY

        for detection in detections:
            targetX = int((detection.left + detection.right) / 2.0)
            bodyCenterY = (detection.top + detection.bottom) / 2.0
            targetY = int(
                bodyCenterY - ((detection.bottom - detection.top) * self.config.target.headOffsetRatio)
            )

            distance = math.hypot(centerX - targetX, centerY - targetY)
            if distance < bestDistance:
                bestDistance = distance
                bestDetection = detection
                bestTargetPoint = (targetX, targetY)

        if bestDetection is None or bestTargetPoint is None:
            return None

        scaledDx = int((bestTargetPoint[0] - centerX) * self.config.control.mouseScale)
        scaledDy = int((bestTargetPoint[1] - centerY) * self.config.control.mouseScale)
        return AimSelection(
            detection=bestDetection,
            targetPoint=bestTargetPoint,
            aimOrigin=(int(centerX), int(centerY)),
            delta=AimDelta(dx=scaledDx, dy=scaledDy),
        )
