"""
pipeline.py
-----------
Orchestrates the end-to-end workflow for a single frame:
  detect plate region(s) -> preprocess crop -> OCR -> persist result.

Keeping this coordination logic separate from main.py means the same
pipeline can be reused by the CLI, by the test suite, or by a future
video-stream mode without duplicating logic.
"""

from dataclasses import dataclass
from typing import List

import cv2
import numpy as np

from src.database import Database
from src.logger_config import get_logger
from src.ocr_engine import OCREngine
from src.plate_detector import PlateDetector
from src.preprocessing import prepare_plate_for_ocr

logger = get_logger("pipeline")


@dataclass
class PipelineResult:
    plate_text: str
    confidence: float
    bbox: tuple
    is_valid: bool


class ANPRPipeline:
    """High-level facade combining detection, OCR and storage."""

    def __init__(self, detector: PlateDetector = None, ocr: OCREngine = None,
                 db: Database = None, persist: bool = True):
        self.detector = detector or PlateDetector()
        self.ocr = ocr or OCREngine()
        self.db = db if db is not None else (Database() if persist else None)
        self.persist = persist

    def process_frame(self, frame: np.ndarray, source_label: str) -> List[PipelineResult]:
        """Run the full pipeline on one frame and return every valid result."""
        results = []
        candidates = self.detector.detect(frame)

        for candidate in candidates:
            preprocessed = prepare_plate_for_ocr(candidate.crop)
            ocr_result = self.ocr.read_plate(preprocessed)

            if ocr_result.is_valid and self.persist and self.db is not None:
                self.db.insert_detection(
                    plate_text=ocr_result.text,
                    confidence=ocr_result.confidence,
                    source_file=source_label,
                )

            results.append(PipelineResult(
                plate_text=ocr_result.text,
                confidence=ocr_result.confidence,
                bbox=candidate.bbox,
                is_valid=ocr_result.is_valid,
            ))

        if not candidates:
            logger.warning("No plate candidates found in '%s'", source_label)

        return results

    def process_image_file(self, image_path: str) -> List[PipelineResult]:
        frame = cv2.imread(image_path)
        if frame is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")
        return self.process_frame(frame, source_label=image_path)
