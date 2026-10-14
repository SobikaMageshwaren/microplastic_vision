import time
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

from app.services.evaluation_service import EvaluationService
from app.services.analysis_service import AnalysisService
from app.services.ml_service import MLService
from app.db.database import SessionLocal
from app.utils.image_io import load_image, save_image


class ModelComparisonService:
    def __init__(self):
        self.evaluation_service = EvaluationService()
        self.analysis_service = AnalysisService()
        self.ml_service = MLService()
        self._cached_comparison: Optional[Dict[str, Any]] = None

    def compare_classical_vs_unet(
        self,
        image_path: Path = Path("dataset/original_size/RR1.tiff"),
        gt_path: Path = Path("dataset/annotations/Annotatied masks/RR1.png"),
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Run side-by-side evaluation comparison of Classical CV (Otsu+Watershed) vs. U-Net Learned Segmentation on ground truth annotations.
        Caches result for instant UI responses. Reports objective raw metrics.
        """
        if not force_refresh and self._cached_comparison is not None:
            return self._cached_comparison

        if not image_path.exists() or not gt_path.exists():
            image_path = Path("dataset/original_size/RR1.tiff")
            gt_path = Path("dataset/annotations/Annotatied masks/RR1.png")

        db = SessionLocal()

        # 1. Evaluate Classical CV
        t0 = time.time()
        with open(image_path, "rb") as f:
            img_bytes = f.read()

        classical_create_res = self.analysis_service.run_full_pipeline(
            image_input=img_bytes,
            filename=image_path.name,
            db=db
        )
        classical_time_ms = round((time.time() - t0) * 1000.0, 1)

        # Get generated cleaned mask path for classical CV evaluation
        classical_output_dir = Path("data/outputs") / classical_create_res.analysis_id
        classical_mask_path = classical_output_dir / "cleaned_mask.png"
        original_png_path = classical_output_dir / "original.png"

        # Save displayable Ground Truth Mask PNG into the analysis output directory
        _, gt_gray = load_image(gt_path)
        gt_display_path = classical_output_dir / "ground_truth_mask.png"
        save_image(gt_display_path, gt_gray)

        classical_eval = self.evaluation_service.evaluate_masks(
            predicted_mask_input=classical_mask_path,
            ground_truth_mask_input=gt_path,
            image_name=image_path.name,
            db=db
        )

        # 2. Evaluate U-Net Deep Learning
        t0 = time.time()
        unet_res = self.ml_service.predict_unet(
            image_input=img_bytes,
            threshold=0.5
        )
        unet_time_ms = round((time.time() - t0) * 1000.0, 1)

        unet_mask_path = Path(unet_res["artifacts"]["binary_mask"])
        unet_eval = self.evaluation_service.evaluate_masks(
            predicted_mask_input=unet_mask_path,
            ground_truth_mask_input=gt_path,
            image_name=image_path.name,
            db=db
        )

        db.close()

        # Helper path formatter
        def format_path(p_str: Optional[str]) -> Optional[str]:
            if not p_str:
                return None
            norm = str(p_str).replace("\\", "/")
            if "/data/outputs/" in norm:
                return "/data/outputs/" + norm.split("/data/outputs/")[1]
            elif "data/outputs/" in norm:
                return "/data/outputs/" + norm.split("data/outputs/")[1]
            return norm

        result = {
            "evaluated_image": image_path.name,
            "metrics_comparison": [
                {
                    "method": "Classical CV (Otsu + Watershed)",
                    "pipeline_version": classical_create_res.pipeline_version,
                    "iou": classical_eval.iou,
                    "dice": classical_eval.dice,
                    "precision": classical_eval.precision,
                    "recall": classical_eval.recall,
                    "f1": classical_eval.f1,
                    "particle_count": classical_create_res.particle_count,
                    "processing_time_ms": classical_time_ms,
                    "predicted_mask_path": format_path(str(classical_mask_path)),
                    "error_map_path": format_path(classical_eval.error_map_path),
                    "overlay_path": format_path(classical_eval.overlay_path)
                },
                {
                    "method": "U-Net Learned Segmentation",
                    "pipeline_version": "unet-dl-v1.0",
                    "iou": unet_eval.iou,
                    "dice": unet_eval.dice,
                    "precision": unet_eval.precision,
                    "recall": unet_eval.recall,
                    "f1": unet_eval.f1,
                    "particle_count": unet_res["particle_count"],
                    "processing_time_ms": unet_time_ms,
                    "predicted_mask_path": format_path(str(unet_mask_path)),
                    "error_map_path": format_path(unet_eval.error_map_path),
                    "overlay_path": format_path(unet_eval.overlay_path)
                }
            ],
            "artifacts": {
                "original_image": format_path(str(original_png_path)),
                "ground_truth_mask": format_path(str(gt_display_path)),
                "classical_mask": format_path(str(classical_mask_path)),
                "unet_mask": format_path(str(unet_mask_path)),
                "unet_prob_map": format_path(unet_res["artifacts"]["probability_map"])
            }
        }
        self._cached_comparison = result
        return result
