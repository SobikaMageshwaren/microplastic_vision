from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple, Dict, Any


class SegmentationEngine(ABC):
    """
    Abstract base class interface for segmentation engines.
    Allows easy swapping between Classical CV, PyTorch U-Net, SegFormer, YOLO-Seg in the future.
    """

    @abstractmethod
    def segment(self, preprocessed_image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform segmentation on preprocessed image.
        
        Args:
            preprocessed_image: Grayscale or RGB image array
            config: Algorithm configuration dictionary
            
        Returns:
            Tuple[raw_threshold_mask, cleaned_mask]
        """
        pass
