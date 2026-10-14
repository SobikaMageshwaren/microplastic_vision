import cv2
import numpy as np


def clean_binary_mask(mask: np.ndarray, open_kernel_size: int = 3, close_kernel_size: int = 5) -> np.ndarray:
    """Clean noise and fill small holes in binary mask using morphological ops."""
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_kernel_size, open_kernel_size))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_kernel_size, close_kernel_size))
    
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_close)
    return cleaned
