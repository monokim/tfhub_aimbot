from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import tensorflow_hub as hub

from .capture import FrameData
from .config import AppConfig


@dataclass
class Detection:
    left: int
    right: int
    top: int
    bottom: int
    score: float


class PersonDetector:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.model = hub.load(self.config.model_url)

    def infer(self, frame: FrameData) -> list[Detection]:
        image = np.expand_dims(frame.image, 0)
        result = self.model(image)
        result_np = {key: value.numpy() for key, value in result.items()}
        boxes = result_np["detection_boxes"][0]
        scores = result_np["detection_scores"][0]
        classes = result_np["detection_classes"][0]

        detections: list[Detection] = []
        for i, box in enumerate(boxes):
            if classes[i] != self.config.person_class or scores[i] < self.config.score_threshold:
                continue

            ymin, xmin, ymax, xmax = tuple(box)
            if ymin > self.config.filter_ymin_min and ymax > self.config.filter_ymax_min:
                continue

            left = int(xmin * frame.width)
            right = int(xmax * frame.width)
            top = int(ymin * frame.height)
            bottom = int(ymax * frame.height)

            detections.append(
                Detection(left=left, right=right, top=top, bottom=bottom, score=float(scores[i]))
            )

        return detections
