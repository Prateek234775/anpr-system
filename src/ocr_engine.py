"""
ocr_engine.py
-------------
Module 2 of the pipeline: reads characters off a preprocessed plate
crop using Tesseract OCR, then cleans and validates the result.
"""

import re
from dataclasses import dataclass

import pytesseract
import numpy as np

from src.config import MIN_OCR_CONFIDENCE, MIN_PLATE_TEXT_LENGTH, OCR_CONFIG, OCR_LANG
from src.logger_config import get_logger

logger = get_logger("ocr_engine")

_ALLOWED_CHARS = re.compile(r"[^A-Z0-9]")


@dataclass
class OCRResult:
    text: str
    confidence: float
    is_valid: bool


class OCREngine:
    """Thin, testable wrapper around pytesseract for plate text extraction."""

    def __init__(self, lang: str = OCR_LANG, config: str = OCR_CONFIG):
        self.lang = lang
        self.config = config

    def read_plate(self, preprocessed_crop: np.ndarray) -> OCRResult:
        """
        Run OCR on a preprocessed (binarised, deskewed) plate crop and
        return the cleaned text plus an aggregate confidence score.
        """
        data = pytesseract.image_to_data(
            preprocessed_crop,
            lang=self.lang,
            config=self.config,
            output_type=pytesseract.Output.DICT,
        )

        words, confidences = [], []
        for text, conf in zip(data["text"], data["conf"]):
            cleaned = _ALLOWED_CHARS.sub("", text.upper())
            conf_value = float(conf)
            if cleaned and conf_value > 0:
                words.append(cleaned)
                confidences.append(conf_value)

        plate_text = "".join(words)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        is_valid = (
            len(plate_text) >= MIN_PLATE_TEXT_LENGTH
            and avg_confidence >= MIN_OCR_CONFIDENCE
        )

        logger.info(
            "OCR result: text='%s' confidence=%.1f valid=%s",
            plate_text, avg_confidence, is_valid,
        )
        return OCRResult(text=plate_text, confidence=avg_confidence, is_valid=is_valid)
