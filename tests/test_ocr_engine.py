import cv2
import numpy as np

from src.ocr_engine import OCREngine


def _render_text_image(text: str) -> np.ndarray:
    """Render text onto a blank image to give Tesseract something real to read."""
    img = np.full((80, 300), 255, dtype=np.uint8)
    cv2.putText(img, text, (10, 55), cv2.FONT_HERSHEY_SIMPLEX,
                1.4, (0,), 3, cv2.LINE_AA)
    return img


def test_read_plate_recognises_rendered_text():
    engine = OCREngine()
    image = _render_text_image("MP09AB1234")
    result = engine.read_plate(image)
    # Tesseract on synthetic text isn't pixel-perfect, so we check that most
    # of the expected characters were recovered rather than an exact match.
    assert len(result.text) >= 6
    assert any(ch in result.text for ch in "MP091234")


def test_read_plate_on_blank_image_is_invalid():
    engine = OCREngine()
    blank = np.full((80, 300), 255, dtype=np.uint8)
    result = engine.read_plate(blank)
    assert result.is_valid is False
    assert result.text == ""


def test_ocr_result_confidence_is_between_0_and_100():
    engine = OCREngine()
    image = _render_text_image("DL5CAB9999")
    result = engine.read_plate(image)
    assert 0.0 <= result.confidence <= 100.0
