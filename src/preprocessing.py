"""
preprocessing.py
-----------------
Image preprocessing utilities shared by the detection and OCR stages.
Each function does exactly one transformation so the pipeline stays
modular and each step can be unit-tested and swapped independently.
"""

import cv2
import numpy as np

from src.logger_config import get_logger

logger = get_logger("preprocessing")


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert a BGR image to single-channel grayscale."""
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(gray_image: np.ndarray) -> np.ndarray:
    """Remove sensor/compression noise while preserving plate edges."""
    return cv2.bilateralFilter(gray_image, d=11, sigmaColor=17, sigmaSpace=17)


def enhance_contrast(gray_image: np.ndarray) -> np.ndarray:
    """CLAHE contrast enhancement — helps with poorly lit plates."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray_image)


def binarize(gray_image: np.ndarray) -> np.ndarray:
    """Adaptive threshold to get clean black-on-white text for OCR."""
    return cv2.adaptiveThreshold(
        gray_image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
        blockSize=31, C=15,
    )


def deskew(binary_image: np.ndarray) -> np.ndarray:
    """
    Correct small rotation angles so characters sit on a horizontal
    baseline, which noticeably improves OCR accuracy on angled plates.
    """
    coords = np.column_stack(np.where(binary_image > 0))
    if coords.shape[0] < 10:
        return binary_image  # not enough foreground pixels to estimate angle

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.5:
        return binary_image  # negligible skew, skip the transform

    (h, w) = binary_image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        binary_image, matrix, (w, h),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE,
    )


def prepare_plate_for_ocr(plate_crop: np.ndarray) -> np.ndarray:
    """Full preprocessing chain applied to a cropped plate region."""
    logger.debug("Preprocessing plate crop of shape %s", plate_crop.shape)
    gray = to_grayscale(plate_crop)
    gray = denoise(gray)
    gray = enhance_contrast(gray)
    binary = binarize(gray)
    binary = deskew(binary)
    return binary
