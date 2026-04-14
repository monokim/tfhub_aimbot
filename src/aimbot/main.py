from __future__ import annotations

import argparse
import time

from .capture import WindowCapture
from .config import load_config
from .controller import MouseController
from .detector import PersonDetector
from .target_selector import TargetSelector


def run(config_path: str) -> None:
    config = load_config(config_path)
    capture = WindowCapture(config)
    detector = PersonDetector(config)
    selector = TargetSelector(config)
    controller = MouseController(config)

    while True:
        try:
            frame = capture.grab()
            detections = detector.infer(frame)
            print(f"Detected: {len(detections)}")
            delta = selector.select(detections, frame.width, frame.height)
            if delta is not None:
                controller.move_and_click(delta)
            time.sleep(config.loop_sleep_sec)
        except RuntimeError as exc:
            print(exc)
            time.sleep(1.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refactored aimbot loop (v2 scaffold).")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
