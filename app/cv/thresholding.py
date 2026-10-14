import cv2
import numpy as np
from typing import Tuple, Dict, Any
from app.cv.base import SegmentationEngine


def apply_otsu_threshold(gray: np.ndarray) -> np.ndarray:
    """Apply direct Otsu global thresholding."""
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return mask


def apply_adaptive_threshold(gray: np.ndarray) -> np.ndarray:
    """Apply direct Gaussian adaptive thresholding."""
    mask = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2
    )
    return mask


class ClassicalSegmentationEngine(SegmentationEngine):
    """
    Classical Computer Vision Segmentation Engine.
    Combines True Raw Binary Thresholding (Otsu/Adaptive) with Morphological Cleaning.
    """

    def segment(self, preprocessed_image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        method = config.get("threshold_method", "otsu").lower()
        
        # 1. True Raw Binary Thresholding (Unsmoothed: exhibits sensor noise flecks, jagged borders & voids)
        if method == "adaptive":
            raw_mask = apply_adaptive_threshold(preprocessed_image)
        else:
            raw_mask = apply_otsu_threshold(preprocessed_image)

        # Invert mask if particle is dark on bright background (auto polarity check)
        mean_mask_val = np.mean(raw_mask)
        if mean_mask_val > 127:  # Majority white -> invert to make particles white (255)
            raw_mask = cv2.bitwise_not(raw_mask)

        # 2. Morphological Cleaning:
        # - Opening (4x4 ellipse): Strips away isolated 1-3 pixel noise speckles and boundary spurs
        # - Closing (6x6 ellipse): Bridges internal intra-particle pinhole voids and seals concave crevices
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        
        opened = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel_open)
        cleaned_mask = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_close)

        return raw_mask, cleaned_mask
