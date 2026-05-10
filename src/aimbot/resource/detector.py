from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from ultralytics import YOLO

from ..config import AppConfig
from .capture import FrameData


@dataclass
class Detection:
    left: int
    right: int
    top: int
    bottom: int
    score: float
    classId: int


class PersonDetector:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        modelPath = Path(self.config.detector.modelPath)
        if not modelPath.exists():
            raise FileNotFoundError(f"Model file not found: {modelPath}")

        self.deviceName = self._resolveDeviceName()
        self.deviceInfo = self._buildDeviceInfo()
        self.model = YOLO(str(modelPath))
        self.model.to(self.deviceName)

    def _resolveDeviceName(self) -> str:
        if self.config.detector.preferGpu and torch.cuda.is_available():
            return "cuda:0"
        return "cpu"

    def _buildDeviceInfo(self) -> str:
        cudaAvailable = torch.cuda.is_available()
        torchCudaVersion = torch.version.cuda if torch.version.cuda is not None else "None"
        if self.deviceName.startswith("cuda") and cudaAvailable:
            gpuName = torch.cuda.get_device_name(0)
            return (
                f"torch={torch.__version__}, torchCuda={torchCudaVersion}, "
                f"cudaAvailable=True, gpu={gpuName}, device={self.deviceName}"
            )
        return (
            f"torch={torch.__version__}, torchCuda={torchCudaVersion}, "
            f"cudaAvailable={cudaAvailable}, device={self.deviceName}"
        )

    @property
    def deviceLabel(self) -> str:
        return f"device={self.deviceName}"

    def _isIgnoredBottomRight(self, detection: Detection, width: int, height: int) -> bool:
        if not self.config.detector.excludeBottomRightEnabled:
            return False

        centerX = (detection.left + detection.right) / 2.0
        centerY = (detection.top + detection.bottom) / 2.0
        return (
            centerX >= (width * self.config.detector.excludeRightStartRatio)
            and centerY >= (height * self.config.detector.excludeBottomStartRatio)
        )

    def _passesSizeFilter(self, detection: Detection, frameHeight: int) -> bool:
        minHeight = max(1.0, frameHeight * self.config.detector.minBoxHeightRatio)
        boxHeight = float(detection.bottom - detection.top)
        return boxHeight >= minHeight

    def infer(self, frame: FrameData) -> list[Detection]:
        inference = self.model.predict(
            source=frame.image,
            imgsz=self.config.detector.imageSize,
            conf=self.config.detector.scoreThreshold,
            classes=[self.config.detector.personClassId],
            device=self.deviceName,
            half=self.config.detector.useHalfPrecision and self.deviceName.startswith("cuda"),
            verbose=False,
        )
        if not inference:
            return []

        boxes = inference[0].boxes
        if boxes is None:
            return []

        detections: list[Detection] = []
        for box in boxes:
            coordinates = box.xyxy[0].tolist()
            classId = int(box.cls[0].item())
            score = float(box.conf[0].item())
            left, top, right, bottom = [int(value) for value in coordinates]
            detections.append(
                Detection(
                    left=left,
                    right=right,
                    top=top,
                    bottom=bottom,
                    score=score,
                    classId=classId,
                )
            )

        filteredDetections: list[Detection] = []
        for detection in detections:
            if not self._passesSizeFilter(detection, frame.height):
                continue
            if self._isIgnoredBottomRight(detection, frame.width, frame.height):
                continue
            filteredDetections.append(detection)

        return filteredDetections
