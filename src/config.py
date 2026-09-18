"""
config.py
---------
Centralised configuration for the ANPR (Automatic Number Plate Recognition)
system. Keeping every tunable value in one place satisfies the
maintainability and configurability non-functional requirements: nothing
below needs code changes elsewhere in the pipeline to be adjusted.
"""

import os
import cv2

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_IMAGES_DIR = os.path.join(DATA_DIR, "sample_images")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOG_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(OUTPUT_DIR, "anpr_records.db")
LOG_FILE = os.path.join(LOG_DIR, "anpr_system.log")

for _dir in (OUTPUT_DIR, LOG_DIR, SAMPLE_IMAGES_DIR):
    os.makedirs(_dir, exist_ok=True)

# ---------------------------------------------------------------------------
# Plate detection (Haar Cascade)
# ---------------------------------------------------------------------------
# Shipped with opencv-python; no external download required.
CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_russian_plate_number.xml")

DETECTOR_SCALE_FACTOR = 1.05      # how much the image size is reduced at each scale
DETECTOR_MIN_NEIGHBORS = 4        # higher = fewer false positives, may miss real plates
DETECTOR_MIN_SIZE = (60, 20)      # smallest plate region (w, h) in pixels to accept

# ---------------------------------------------------------------------------
# OCR (Tesseract)
# ---------------------------------------------------------------------------
OCR_LANG = "eng"
# psm 7 = "treat the image as a single text line", ideal for a cropped plate
# whitelist restricts recognised characters to what plates actually contain
OCR_CONFIG = (
    "--psm 7 --oem 3 "
    "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)
MIN_PLATE_TEXT_LENGTH = 4          # discard OCR results shorter than this
MIN_OCR_CONFIDENCE = 40.0          # 0-100 scale, from Tesseract's own confidence score

# ---------------------------------------------------------------------------
# Reporting / performance
# ---------------------------------------------------------------------------
SUPPORTED_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")
FRAME_SKIP_FOR_VIDEO = 5           # process every Nth frame to keep video mode responsive
