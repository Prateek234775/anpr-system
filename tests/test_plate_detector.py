import numpy as np
import pytest

from src.plate_detector import PlateDetector, PlateDetectorError


def test_detector_initialises_with_valid_cascade():
    detector = PlateDetector()
    assert detector is not None


def test_detector_raises_on_invalid_cascade_path():
    with pytest.raises(PlateDetectorError):
        PlateDetector(cascade_path="not_a_real_cascade.xml")


def test_detect_raises_on_empty_frame():
    detector = PlateDetector()
    with pytest.raises(PlateDetectorError):
        detector.detect(np.array([]))


def test_detect_returns_list_on_blank_frame():
    detector = PlateDetector()
    blank = np.zeros((200, 400, 3), dtype=np.uint8)
    results = detector.detect(blank)
    assert isinstance(results, list)  # a blank frame should yield zero candidates
    assert len(results) == 0
