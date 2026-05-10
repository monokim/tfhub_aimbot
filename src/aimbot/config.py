from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class WindowConfig:
    title: str
    roiEnabled: bool
    roiWidth: int
    roiHeight: int


@dataclass
class CaptureConfig:
    sizeScale: int


@dataclass
class DetectorConfig:
    modelPath: str
    personClassId: int
    scoreThreshold: float
    imageSize: int
    preferGpu: bool
    useHalfPrecision: bool
    minBoxHeightRatio: float
    excludeBottomRightEnabled: bool
    excludeBottomStartRatio: float
    excludeRightStartRatio: float


@dataclass
class TargetConfig:
    headOffsetRatio: float
    aimOriginOffsetX: int
    aimOriginOffsetY: int


@dataclass
class ControlConfig:
    mouseScale: float
    maxStep: int
    adaptiveStepNearMaxStep: int
    adaptiveStepFarDistancePx: float
    adaptiveStepCurve: float
    deadzonePx: int
    slowRadiusPx: int
    minSlowScale: float
    moveSleepSec: float
    clickHoldSec: float
    loopSleepSec: float
    autoFire: bool
    boostEnabled: bool
    boostStartPx: float
    boostMaxScale: float


@dataclass
class InterfaceConfig:
    enabled: bool
    windowName: str
    maxFps: int
    showAimOrigin: bool


@dataclass
class ToggleConfig:
    virtualKeyCode: int
    debounceMs: int


@dataclass
class AppConfig:
    window: WindowConfig
    capture: CaptureConfig
    detector: DetectorConfig
    target: TargetConfig
    control: ControlConfig
    interface: InterfaceConfig
    toggle: ToggleConfig


def _getValue(data: dict[str, Any], keys: list[str], default: Any) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    windowData = data.get("window", {})
    roiData = windowData.get("roi", {})
    captureData = data.get("capture", {})
    detectorData = data.get("detector", {})
    targetData = data.get("target", {})
    controlData = data.get("control", {})
    interfaceData = data.get("interface", {})
    toggleData = data.get("toggle", {})

    return AppConfig(
        window=WindowConfig(
            title=str(windowData.get("title", "")),
            roiEnabled=bool(_getValue(roiData, ["enabled", "roiEnabled"], False)),
            roiWidth=int(_getValue(roiData, ["width", "roiWidth"], 640)),
            roiHeight=int(_getValue(roiData, ["height", "roiHeight"], 640)),
        ),
        capture=CaptureConfig(
            sizeScale=int(_getValue(captureData, ["sizeScale", "size_scale"], 2)),
        ),
        detector=DetectorConfig(
            modelPath=str(_getValue(detectorData, ["modelPath", "model_path"], "yolo26n.pt")),
            personClassId=int(_getValue(detectorData, ["personClassId", "class_person"], 0)),
            scoreThreshold=float(_getValue(detectorData, ["scoreThreshold", "score_threshold"], 0.45)),
            imageSize=int(_getValue(detectorData, ["imageSize", "image_size"], 640)),
            preferGpu=bool(_getValue(detectorData, ["preferGpu"], True)),
            useHalfPrecision=bool(_getValue(detectorData, ["useHalfPrecision"], True)),
            minBoxHeightRatio=float(_getValue(detectorData, ["minBoxHeightRatio"], 0.12)),
            excludeBottomRightEnabled=bool(
                _getValue(detectorData, ["excludeBottomRightEnabled"], True)
            ),
            excludeBottomStartRatio=float(_getValue(detectorData, ["excludeBottomStartRatio"], 0.58)),
            excludeRightStartRatio=float(_getValue(detectorData, ["excludeRightStartRatio"], 0.62)),
        ),
        target=TargetConfig(
            headOffsetRatio=float(_getValue(targetData, ["headOffsetRatio", "head_offset_ratio"], 0.42)),
            aimOriginOffsetX=int(_getValue(targetData, ["aimOriginOffsetX"], 0)),
            aimOriginOffsetY=int(_getValue(targetData, ["aimOriginOffsetY"], 0)),
        ),
        control=ControlConfig(
            mouseScale=float(_getValue(controlData, ["mouseScale", "mouse_scale"], 1.15)),
            maxStep=int(_getValue(controlData, ["maxStep"], 90)),
            adaptiveStepNearMaxStep=int(_getValue(controlData, ["adaptiveStepNearMaxStep"], 40)),
            adaptiveStepFarDistancePx=float(_getValue(controlData, ["adaptiveStepFarDistancePx"], 220.0)),
            adaptiveStepCurve=float(_getValue(controlData, ["adaptiveStepCurve"], 1.6)),
            deadzonePx=int(_getValue(controlData, ["deadzonePx"], 3)),
            slowRadiusPx=int(_getValue(controlData, ["slowRadiusPx"], 70)),
            minSlowScale=float(_getValue(controlData, ["minSlowScale"], 0.25)),
            moveSleepSec=float(_getValue(controlData, ["moveSleepSec", "move_sleep_sec"], 0.0)),
            clickHoldSec=float(_getValue(controlData, ["clickHoldSec", "click_hold_sec"], 0.015)),
            loopSleepSec=float(_getValue(controlData, ["loopSleepSec", "loop_sleep_sec"], 0.0)),
            autoFire=bool(_getValue(controlData, ["autoFire"], False)),
            boostEnabled=bool(_getValue(controlData, ["boostEnabled"], True)),
            boostStartPx=float(_getValue(controlData, ["boostStartPx"], 18.0)),
            boostMaxScale=float(_getValue(controlData, ["boostMaxScale"], 2.8)),
        ),
        interface=InterfaceConfig(
            enabled=bool(_getValue(interfaceData, ["enabled"], True)),
            windowName=str(_getValue(interfaceData, ["windowName"], "Aimbot Detection")),
            maxFps=int(_getValue(interfaceData, ["maxFps"], 75)),
            showAimOrigin=bool(_getValue(interfaceData, ["showAimOrigin"], False)),
        ),
        toggle=ToggleConfig(
            virtualKeyCode=int(_getValue(toggleData, ["virtualKeyCode"], 123)),
            debounceMs=int(_getValue(toggleData, ["debounceMs"], 180)),
        ),
    )
