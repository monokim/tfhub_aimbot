from __future__ import annotations

import math
from dataclasses import dataclass

from .config import AppConfig
from .detector import Detection


@dataclass
class AimDelta:
    dx: int
    dy: int


class TargetSelector:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def select(self, detections: list[Detection], width: int, height: int) -> AimDelta | None:
        if not detections:
            return None

        best_idx = 0
        best_dist = float("inf")
        centers: list[tuple[float, float]] = []

        for idx, box in enumerate(detections):
            center_x = ((box.right - box.left) / 2) + box.left
            center_y = ((box.bottom - box.top) / 2) + box.top
            centers.append((center_x, center_y))
            dist = math.sqrt((width / 2 - center_x) ** 2 + (height / 2 - center_y) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx

        target = detections[best_idx]
        target_center = centers[best_idx]
        dx = target_center[0] - width / 2
        dy = target_center[1] - height / 2 - (target.bottom - target.top) * self.config.head_offset_ratio

        scale = self.config.mouse_scale * self.config.size_scale
        return AimDelta(dx=int(dx * scale), dy=int(dy * scale))
