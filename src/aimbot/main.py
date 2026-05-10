from __future__ import annotations

import argparse
import logging
import time

from .config import AppConfig, load_config
from .hooks.toggle_key import ToggleKeyHook
from .interface.detection_gui import DetectionGui
from .resource.capture import WindowCapture
from .resource.detector import PersonDetector
from .resource.mouse_controller import MouseController
from .utils.target_selector import AimSelection, TargetSelector


def _configureLogging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _runLoop(config: AppConfig) -> None:
    logger = logging.getLogger(__name__)
    capture = WindowCapture(config)
    detector = PersonDetector(config)
    selector = TargetSelector(config)
    controller = MouseController(config)
    gui = DetectionGui(config, detector.deviceLabel)
    toggleHook = ToggleKeyHook(
        virtualKeyCode=config.toggle.virtualKeyCode,
        debounceMs=config.toggle.debounceMs,
    )
    isAimbotEnabled = True
    lastLoopAt = time.perf_counter()
    logger.info("Aimbot loop started.")
    logger.info(
        "Window='%s', ROI=%s (%sx%s), model='%s', imageSize=%s",
        config.window.title,
        config.window.roiEnabled,
        config.window.roiWidth,
        config.window.roiHeight,
        config.detector.modelPath,
        config.detector.imageSize,
    )
    logger.info("Detector device: %s", detector.deviceInfo)
    if detector.deviceName == "cpu" and config.detector.preferGpu:
        logger.warning(
            "GPU was requested but CUDA is unavailable. Install CUDA-enabled PyTorch to use GTX 1060."
        )
    logger.info("Toggle key set to VK=%s (F12 expected: 123).", config.toggle.virtualKeyCode)
    logger.info(
        "Control tuning: mouseScale=%.2f, maxStep=%s, adaptiveNearStep=%s, adaptiveFarDistancePx=%.1f, adaptiveStepCurve=%.2f, deadzonePx=%s, slowRadiusPx=%s, minSlowScale=%.2f, boostEnabled=%s, boostStartPx=%.1f, boostMaxScale=%.2f",
        config.control.mouseScale,
        config.control.maxStep,
        config.control.adaptiveStepNearMaxStep,
        config.control.adaptiveStepFarDistancePx,
        config.control.adaptiveStepCurve,
        config.control.deadzonePx,
        config.control.slowRadiusPx,
        config.control.minSlowScale,
        config.control.boostEnabled,
        config.control.boostStartPx,
        config.control.boostMaxScale,
    )
    logger.info(
        "Detector tuning: conf=%.2f, imgsz=%s, minBoxHeightRatio=%.3f, excludeBottomRight=%s",
        config.detector.scoreThreshold,
        config.detector.imageSize,
        config.detector.minBoxHeightRatio,
        config.detector.excludeBottomRightEnabled,
    )
    logger.info(
        "Aim origin: offsetX=%s, offsetY=%s, showAimOrigin=%s",
        config.target.aimOriginOffsetX,
        config.target.aimOriginOffsetY,
        config.interface.showAimOrigin,
    )

    try:
        while True:
            if toggleHook.consumeToggle():
                isAimbotEnabled = not isAimbotEnabled
                logger.info("Aimbot toggled -> %s", "ENABLED" if isAimbotEnabled else "DISABLED")

            loopStartAt = time.perf_counter()
            frame = capture.grab()
            detections = detector.infer(frame)
            selected: AimSelection | None = selector.select(detections, frame.width, frame.height)
            if isAimbotEnabled and selected is not None:
                controller.moveAndAction(selected.delta)

            now = time.perf_counter()
            loopFps = 1.0 / max(1e-6, now - lastLoopAt)
            lastLoopAt = now

            keepRunning = gui.render(
                rgbFrame=frame.image,
                detections=detections,
                selectedDetection=selected.detection if selected else None,
                selectedPoint=selected.targetPoint if selected else None,
                aimOrigin=selected.aimOrigin if selected else (frame.width // 2, frame.height // 2),
                loopFps=loopFps,
                isAimbotEnabled=isAimbotEnabled,
            )
            if not keepRunning:
                break

            sleepBudget = config.control.loopSleepSec - (time.perf_counter() - loopStartAt)
            if sleepBudget > 0:
                time.sleep(sleepBudget)
    finally:
        gui.close()
        capture.close()


def run(configPath: str) -> None:
    config = load_config(configPath)
    while True:
        try:
            _runLoop(config)
            break
        except RuntimeError as exc:
            print(exc)
            time.sleep(1.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLO26n-based aimbot loop for AI experimentation.")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML.")
    return parser.parse_args()


def main() -> None:
    _configureLogging()
    args = parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
