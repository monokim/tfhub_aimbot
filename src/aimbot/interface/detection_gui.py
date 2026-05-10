from __future__ import annotations

import time

import cv2

from ..config import AppConfig
from ..resource.detector import Detection


class DetectionGui:
    def __init__(self, config: AppConfig, deviceLabel: str) -> None:
        self.config = config
        self.deviceLabel = deviceLabel
        self.enabled = config.interface.enabled
        self.windowName = config.interface.windowName
        self.frameDelaySec = 1.0 / float(config.interface.maxFps)
        self.lastFrameAt = 0.0
        if self.enabled:
            cv2.namedWindow(self.windowName, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.windowName, 1024, 720)

    def render(
        self,
        rgbFrame,
        detections: list[Detection],
        selectedDetection: Detection | None,
        selectedPoint: tuple[int, int] | None,
        aimOrigin: tuple[int, int],
        loopFps: float,
        isAimbotEnabled: bool,
    ) -> bool:
        if not self.enabled:
            return True

        now = time.perf_counter()
        if (now - self.lastFrameAt) < self.frameDelaySec:
            self._pollKeys()
            return True
        self.lastFrameAt = now

        canvas = rgbFrame.copy()
        for detection in detections:
            cv2.rectangle(
                canvas,
                (detection.left, detection.top),
                (detection.right, detection.bottom),
                (0, 180, 255),
                1,
            )

        if selectedDetection is not None:
            cv2.rectangle(
                canvas,
                (selectedDetection.left, selectedDetection.top),
                (selectedDetection.right, selectedDetection.bottom),
                (0, 255, 0),
                2,
            )

        originX = max(0, min(canvas.shape[1] - 1, int(aimOrigin[0])))
        originY = max(0, min(canvas.shape[0] - 1, int(aimOrigin[1])))
        center = (originX, originY)
        if self.config.interface.showAimOrigin:
            cv2.drawMarker(canvas, center, (255, 255, 255), cv2.MARKER_CROSS, 16, 1)

        if selectedPoint is not None:
            cv2.line(canvas, center, selectedPoint, (0, 255, 0), 1)
            cv2.circle(canvas, selectedPoint, 4, (0, 255, 0), -1)

        stateLabel = "ACTIVE" if isAimbotEnabled else "PAUSED"
        cv2.putText(
            canvas,
            f"{stateLabel} | fps={loopFps:.1f} | det={len(detections)} | {self.deviceLabel}",
            (10, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            "Keys: [F12] toggle aimbot  [Q] quit",
            (10, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(self.windowName, cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))
        return self._pollKeys()

    def _pollKeys(self) -> bool:
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            return False
        return True

    def close(self) -> None:
        if self.enabled:
            cv2.destroyWindow(self.windowName)
