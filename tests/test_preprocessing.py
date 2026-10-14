import cv2
import numpy as np
import pytest
from app.cv.preprocessing import preprocess_image
from app.schemas.analysis import PreprocessingConfig


def test_preprocessing_output_dimensions():
    bgr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    config = PreprocessingConfig(denoise=True, background_correction=True, contrast_enhancement=True, normalize=True)
    
    preprocessed, intermediates = preprocess_image(bgr, gray, config)
    assert preprocessed.shape == (100, 100)
    assert "denoised" in intermediates
    assert "background_corrected" in intermediates
    assert "contrast_enhanced" in intermediates
    assert "normalized" in intermediates
