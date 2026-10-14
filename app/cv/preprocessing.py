import cv2
import numpy as np
from typing import Dict, Tuple
from app.schemas.analysis import PreprocessingConfig


def preprocess_image(
    img_bgr: np.ndarray,
    gray_img: np.ndarray,
    config: PreprocessingConfig
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """
    Apply modular preprocessing steps preserving intermediate step images with visible, distinct transformations.
    
    Order:
      1. Denoising (FastNLMeans) -> Smooths Poisson-Gaussian noise
      2. Background Correction (Morphological Top-Hat) -> Removes uneven field illumination & vignetting
      3. Min-Max Normalization -> Linear global dynamic range stretch across [0, 255]
      4. Contrast Enhancement (CLAHE) -> Local adaptive tile equalization enhancing fine edge textures
      
    Returns:
        Tuple[final_preprocessed_grayscale_image, intermediate_images_dict]
    """
    intermediate_images: Dict[str, np.ndarray] = {}
    current = gray_img.copy()

    # 1. Denoising
    if config.denoise:
        # Fast non-local means denoising for microscopy
        current = cv2.fastNlMeansDenoising(current, h=10, templateWindowSize=7, searchWindowSize=21)
        intermediate_images["denoised"] = current.copy()

    # 2. Background / Illumination Correction (Morphological Top-Hat)
    if config.background_correction:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
        top_hat = cv2.morphologyEx(current, cv2.MORPH_TOPHAT, kernel)
        current = cv2.add(current, top_hat)
        intermediate_images["background_corrected"] = current.copy()

    # 3. Dynamic Range Min-Max Normalization (Linear Global Stretch)
    if config.normalize:
        # Robust linear percentile stretch: maps 1st percentile to 0 and 99th to 255
        p_low, p_high = np.percentile(current, (1.0, 99.0))
        if p_high > p_low:
            norm_float = np.clip((current.astype(np.float32) - p_low) * 255.0 / (p_high - p_low), 0.0, 255.0)
            norm_img = norm_float.astype(np.uint8)
        else:
            norm_img = cv2.normalize(current, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        intermediate_images["normalized"] = norm_img.copy()
        current = norm_img

    # 4. Contrast Enhancement (Local Adaptive Equalization - CLAHE)
    if config.contrast_enhancement:
        # Distinct tile-based adaptive equalization with clip limit 4.0
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(current)
        intermediate_images["contrast_enhanced"] = clahe_img.copy()
        current = clahe_img

    return current, intermediate_images
