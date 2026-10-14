import pytest
import numpy as np
import cv2
from app.utils.image_io import load_image
from app.core.exceptions import ImageValidationError


def test_load_grayscale_image():
    gray_input = np.ones((100, 100), dtype=np.uint8) * 128
    bgr, gray = load_image(gray_input)
    assert bgr.shape == (100, 100, 3)
    assert gray.shape == (100, 100)


def test_load_rgb_image():
    bgr_input = np.zeros((100, 100, 3), dtype=np.uint8)
    bgr_input[:, :, 2] = 255  # Red in BGR
    bgr, gray = load_image(bgr_input)
    assert bgr.shape == (100, 100, 3)
    assert gray.shape == (100, 100)


def test_load_rgba_image():
    rgba_input = np.zeros((100, 100, 4), dtype=np.uint8)
    rgba_input[:, :, 3] = 255  # Alpha channel
    bgr, gray = load_image(rgba_input)
    assert bgr.shape == (100, 100, 3)
    assert gray.shape == (100, 100)


def test_corrupted_bytes_handling():
    corrupted_bytes = b"NOT_AN_IMAGE_FILE_DATA_12345"
    with pytest.raises(ImageValidationError) as excinfo:
        load_image(corrupted_bytes)
    assert "cannot be decoded" in str(excinfo.value.detail).lower() or "could not decode" in str(excinfo.value.detail).lower()


def test_too_small_image_handling():
    tiny_img = np.zeros((5, 5, 3), dtype=np.uint8)
    with pytest.raises(ImageValidationError) as excinfo:
        load_image(tiny_img)
    assert "too small" in str(excinfo.value.detail).lower()
