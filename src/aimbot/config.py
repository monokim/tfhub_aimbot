from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AppConfig:
    data: dict[str, Any]

    @property
    def window_title(self) -> str:
        return str(self.data["window"]["title"])

    @property
    def roi_enabled(self) -> bool:
        return bool(self.data["window"]["roi"]["enabled"])

    @property
    def roi_width(self) -> int:
        return int(self.data["window"]["roi"]["width"])

    @property
    def roi_height(self) -> int:
        return int(self.data["window"]["roi"]["height"])

    @property
    def size_scale(self) -> int:
        return int(self.data["capture"]["size_scale"])

    @property
    def model_url(self) -> str:
        return str(self.data["detector"]["model_url"])

    @property
    def person_class(self) -> int:
        return int(self.data["detector"]["class_person"])

    @property
    def score_threshold(self) -> float:
        return float(self.data["detector"]["score_threshold"])

    @property
    def filter_ymin_min(self) -> float:
        return float(self.data["detector"]["filter"]["ymin_min"])

    @property
    def filter_ymax_min(self) -> float:
        return float(self.data["detector"]["filter"]["ymax_min"])

    @property
    def head_offset_ratio(self) -> float:
        return float(self.data["target"]["head_offset_ratio"])

    @property
    def mouse_scale(self) -> float:
        return float(self.data["control"]["mouse_scale"])

    @property
    def move_sleep_sec(self) -> float:
        return float(self.data["control"]["move_sleep_sec"])

    @property
    def click_hold_sec(self) -> float:
        return float(self.data["control"]["click_hold_sec"])

    @property
    def loop_sleep_sec(self) -> float:
        return float(self.data["control"]["loop_sleep_sec"])


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return AppConfig(data=data)
