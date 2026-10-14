import numpy as np
from typing import Tuple, Dict, Any
from app.cv.base import SegmentationEngine
from app.cv.thresholding import ClassicalSegmentationEngine


class SegmentationService:
    def __init__(self, engine: SegmentationEngine = None):
        self.engine = engine or ClassicalSegmentationEngine()

    def segment(self, preprocessed_image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """Run segmentation engine (Classical or future ML engine)."""
        return self.engine.segment(preprocessed_image, config)
