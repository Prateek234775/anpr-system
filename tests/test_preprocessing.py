import numpy as np

from src.preprocessing import (
    binarize,
    denoise,
    enhance_contrast,
    prepare_plate_for_ocr,
    to_grayscale,
)


def _make_bgr_image():
    return (np.random.rand(60, 200, 3) * 255).astype(np.uint8)


def test_to_grayscale_converts_bgr():
    img = _make_bgr_image()
    gray = to_grayscale(img)
    assert gray.ndim == 2
    assert gray.shape == img.shape[:2]


def test_to_grayscale_passthrough_for_already_gray():
    gray_in = (np.random.rand(60, 200) * 255).astype(np.uint8)
    gray_out = to_grayscale(gray_in)
    assert np.array_equal(gray_in, gray_out)


def test_denoise_preserves_shape():
    gray = (np.random.rand(60, 200) * 255).astype(np.uint8)
    result = denoise(gray)
    assert result.shape == gray.shape


def test_enhance_contrast_preserves_shape_and_dtype():
    gray = (np.random.rand(60, 200) * 255).astype(np.uint8)
    result = enhance_contrast(gray)
    assert result.shape == gray.shape
    assert result.dtype == np.uint8


def test_binarize_output_is_binary():
    gray = (np.random.rand(60, 200) * 255).astype(np.uint8)
    binary = binarize(gray)
    unique_values = set(np.unique(binary).tolist())
    assert unique_values.issubset({0, 255})


def test_prepare_plate_for_ocr_end_to_end():
    img = _make_bgr_image()
    result = prepare_plate_for_ocr(img)
    assert result.shape == img.shape[:2]
