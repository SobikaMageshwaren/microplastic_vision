import numpy as np
import pytest
from app.cv.quality import validate_image_properties, assess_image_quality
from app.core.exceptions import ImageValidationError


def test_validate_image_properties_success():
    synthetic_img = np.zeros((200, 200, 3), dtype=np.uint8)
    info = validate_image_properties("test_microscopy.png", synthetic_img, 1024)
    assert info.valid is True
    assert info.width == 200
    assert info.height == 200
    assert info.channels == 3
    assert info.format == "PNG"


def test_validate_image_properties_invalid_format():
    synthetic_img = np.zeros((200, 200, 3), dtype=np.uint8)
    with pytest.raises(ImageValidationError):
        validate_image_properties("test.txt", synthetic_img, 1024)


def test_assess_image_quality():
    gray_clean = np.ones((100, 100), dtype=np.uint8) * 128
    assessment = assess_image_quality(gray_clean)
    assert 0 <= assessment.quality_score <= 100
    assert assessment.blur_score >= 0.0
