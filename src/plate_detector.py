"""
plate_detector.py
------------------
Module 1 of the pipeline: locates candidate license-plate regions in a
frame using a Haar Cascade classifier (shipped with OpenCV, so no extra
model download is required — a deliberate choice explained in
docs/DESIGN.md's "Model Selection Rationale" section).
"""

from dataclasses import dataclass
from typing import List

import cv2
import numpy as np

from src.config import (
    CASCADE_PATH,
    DETECTOR_MIN_NEIGHBORS,
    DETECTOR_MIN_SIZE,
    DETECTOR_SCALE_FACTOR,
)
from src.logger_config import get_logger

logger = get_logger("plate_detector")


@dataclass
class PlateCandidate:
    """A single detected plate region within a source frame."""
    x: int
    y: int
    w: int
    h: int
    crop: np.ndarray

    @property
    def bbox(self):
        return (self.x, self.y, self.w, self.h)


class PlateDetectorError(Exception):
    """Raised when the detector cannot be initialised or run."""


class PlateDetector:
    """Wraps a Haar Cascade classifier tuned for license plates."""

    def __init__(self, cascade_path: str = CASCADE_PATH):
        self._cascade = cv2.CascadeClassifier(cascade_path)
        if self._cascade.empty():
            raise PlateDetectorError(
                f"Could not load Haar Cascade from '{cascade_path}'. "
                "Verify your OpenCV installation includes the data files."
            )
        logger.info("Plate detector initialised with cascade: %s", cascade_path)

    def detect(self, frame: np.ndarray) -> List[PlateCandidate]:
        """
        Run detection on a single BGR frame and return every candidate
        plate region found, cropped out of the original frame.
        """
        if frame is None or frame.size == 0:
            raise PlateDetectorError("Received an empty frame for detection.")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

        boxes = self._cascade.detectMultiScale(
            gray,
            scaleFactor=DETECTOR_SCALE_FACTOR,
            minNeighbors=DETECTOR_MIN_NEIGHBORS,
            minSize=DETECTOR_MIN_SIZE,
        )

        candidates = []
        for (x, y, w, h) in boxes:
            crop = frame[y:y + h, x:x + w].copy()
            candidates.append(PlateCandidate(x=x, y=y, w=w, h=h, crop=crop))

        logger.info("Detected %d plate candidate(s) in frame", len(candidates))
        return candidates
