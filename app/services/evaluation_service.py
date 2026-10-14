import cv2
import time
import uuid
import numpy as np
import math
from pathlib import Path
from typing import Union, List, Optional
from sqlalchemy.orm import Session

from app.utils.image_io import load_image, save_image
from app.utils.file_utils import get_analysis_output_dir
from app.schemas.common import EvaluationResponse, AggregateEvaluationResponse
from app.db.models import EvaluationModel


class EvaluationService:
    def evaluate_masks(
        self,
        predicted_mask_input: Union[str, Path, np.ndarray, bytes],
        ground_truth_mask_input: Union[str, Path, np.ndarray, bytes],
        image_name: str = "evaluated_image",
        analysis_id: Optional[str] = None,
        original_image_input: Optional[Union[str, Path, np.ndarray, bytes]] = None,
        db: Optional[Session] = None
    ) -> EvaluationResponse:
        """
        Evaluate binary segmentation metrics and generate visual error maps & boundary overlays.
        """
        t0 = time.time()

        if isinstance(predicted_mask_input, np.ndarray):
            pred_gray = predicted_mask_input
        else:
            _, pred_gray = load_image(predicted_mask_input)

        if isinstance(ground_truth_mask_input, np.ndarray):
            gt_gray = ground_truth_mask_input
        else:
            _, gt_gray = load_image(ground_truth_mask_input)

        # Resize ground-truth if dimensions differ
        if pred_gray.shape != gt_gray.shape:
            gt_gray = cv2.resize(gt_gray, (pred_gray.shape[1], pred_gray.shape[0]), interpolation=cv2.INTER_NEAREST)

        pred_binary = (pred_gray > 127).astype(np.uint8)
        gt_binary = (gt_gray > 127).astype(np.uint8)

        tp_mask = (pred_binary == 1) & (gt_binary == 1)
        fp_mask = (pred_binary == 1) & (gt_binary == 0)
        fn_mask = (pred_binary == 0) & (gt_binary == 1)
        tn_mask = (pred_binary == 0) & (gt_binary == 0)

        tp = int(np.sum(tp_mask))
        fp = int(np.sum(fp_mask))
        fn = int(np.sum(fn_mask))
        tn = int(np.sum(tn_mask))

        # Metrics
        union = tp + fp + fn
        iou = float(tp / union) if union > 0 else 1.0 if (tp == 0 and fp == 0 and fn == 0) else 0.0

        dice_denom = 2 * tp + fp + fn
        dice = float(2 * tp / dice_denom) if dice_denom > 0 else 1.0 if (tp == 0 and fp == 0 and fn == 0) else 0.0

        precision_denom = tp + fp
        precision = float(tp / precision_denom) if precision_denom > 0 else 0.0

        recall_denom = tp + fn
        recall = float(tp / recall_denom) if recall_denom > 0 else 0.0

        f1_denom = precision + recall
        f1 = float(2 * precision * recall / f1_denom) if f1_denom > 0 else 0.0

        # Particle counts via connected components
        _, pred_labels = cv2.connectedComponents(pred_binary * 255)
        _, gt_labels = cv2.connectedComponents(gt_binary * 255)
        pred_count = int(np.max(pred_labels))
        gt_count = int(np.max(gt_labels))
        count_error = pred_count - gt_count

        # Generate Visual Error Map (TP=Green, FP=Red, FN=Blue, TN=Black)
        error_map_bgr = np.zeros((pred_gray.shape[0], pred_gray.shape[1], 3), dtype=np.uint8)
        error_map_bgr[tp_mask] = [0, 255, 0]   # True Positive -> Green
        error_map_bgr[fp_mask] = [0, 0, 255]   # False Positive -> Red
        error_map_bgr[fn_mask] = [255, 0, 0]   # False Negative -> Blue

        # Generate Boundary Overlay
        if original_image_input is not None:
            try:
                orig_bgr, _ = load_image(original_image_input)
                if orig_bgr.shape[:2] != pred_gray.shape[:2]:
                    orig_bgr = cv2.resize(orig_bgr, (pred_gray.shape[1], pred_gray.shape[0]))
                overlay_bgr = orig_bgr.copy()
            except Exception:
                overlay_bgr = cv2.cvtColor(pred_gray, cv2.COLOR_GRAY2BGR)
        else:
            overlay_bgr = cv2.cvtColor(pred_gray, cv2.COLOR_GRAY2BGR)

        # Draw contours: Ground truth in Cyan (255, 255, 0), Prediction in Magenta (255, 0, 255)
        gt_contours, _ = cv2.findContours(gt_binary * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pred_contours, _ = cv2.findContours(pred_binary * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay_bgr, gt_contours, -1, (255, 255, 0), 2)
        cv2.drawContours(overlay_bgr, pred_contours, -1, (255, 0, 255), 1)

        # Save Visual Artifacts
        eval_id = f"eval_{uuid.uuid4().hex[:10]}"
        output_dir = get_analysis_output_dir(analysis_id or "evaluations")
        
        error_map_path = output_dir / f"{eval_id}_error_map.png"
        overlay_path = output_dir / f"{eval_id}_overlay.png"

        save_image(error_map_path, error_map_bgr)
        save_image(overlay_path, overlay_bgr)

        # Convert paths to relative web format
        web_error_map = f"/data/outputs/{output_dir.name}/{error_map_path.name}"
        web_overlay = f"/data/outputs/{output_dir.name}/{overlay_path.name}"

        elapsed_ms = round((time.time() - t0) * 1000.0, 2)

        response = EvaluationResponse(
            evaluation_id=eval_id,
            image_name=image_name,
            iou=round(iou, 4),
            dice=round(dice, 4),
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1=round(f1, 4),
            tp_pixels=tp,
            fp_pixels=fp,
            fn_pixels=fn,
            tn_pixels=tn,
            predicted_particle_count=pred_count,
            ground_truth_particle_count=gt_count,
            particle_count_error=count_error,
            processing_time_ms=elapsed_ms,
            error_map_path=web_error_map,
            overlay_path=web_overlay
        )

        # Save to DB if Session is provided
        if db is not None:
            eval_record = EvaluationModel(
                evaluation_id=eval_id,
                analysis_id=analysis_id,
                image_name=image_name,
                iou=response.iou,
                dice=response.dice,
                precision=response.precision,
                recall=response.recall,
                f1=response.f1,
                tp_pixels=tp,
                fp_pixels=fp,
                fn_pixels=fn,
                tn_pixels=tn,
                predicted_particle_count=pred_count,
                ground_truth_particle_count=gt_count,
                particle_count_error=count_error,
                processing_time_ms=elapsed_ms,
                error_map_path=web_error_map,
                overlay_path=web_overlay
            )
            db.add(eval_record)
            db.commit()

        return response

    def get_aggregate_evaluations(self, db: Session) -> AggregateEvaluationResponse:
        """
        Calculate aggregate mean & std across all evaluated images stored in database.
        """
        records = db.query(EvaluationModel).order_by(EvaluationModel.created_at.desc()).all()
        n = len(records)

        if n == 0:
            return AggregateEvaluationResponse(
                evaluated_images_count=0,
                mean_iou=0.0, std_iou=0.0,
                mean_dice=0.0, std_dice=0.0,
                mean_precision=0.0, std_precision=0.0,
                mean_recall=0.0, std_recall=0.0,
                mean_f1=0.0, std_f1=0.0,
                mean_processing_time_ms=0.0,
                per_image_results=[]
            )

        ious = [r.iou for r in records]
        dices = [r.dice for r in records]
        precisions = [r.precision for r in records]
        recalls = [r.recall for r in records]
        f1s = [r.f1 for r in records]
        times = [r.processing_time_ms for r in records]

        per_image_list = [
            EvaluationResponse(
                evaluation_id=r.evaluation_id,
                image_name=r.image_name,
                iou=r.iou,
                dice=r.dice,
                precision=r.precision,
                recall=r.recall,
                f1=r.f1,
                tp_pixels=r.tp_pixels,
                fp_pixels=r.fp_pixels,
                fn_pixels=r.fn_pixels,
                tn_pixels=r.tn_pixels,
                predicted_particle_count=r.predicted_particle_count,
                ground_truth_particle_count=r.ground_truth_particle_count,
                particle_count_error=r.particle_count_error,
                processing_time_ms=r.processing_time_ms,
                error_map_path=r.error_map_path,
                overlay_path=r.overlay_path,
                created_at=r.created_at.isoformat() if r.created_at else None
            )
            for r in records
        ]

        def calc_mean_std(vals: List[float]):
            m = float(np.mean(vals))
            s = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            return round(m, 4), round(s, 4)

        mean_iou, std_iou = calc_mean_std(ious)
        mean_dice, std_dice = calc_mean_std(dices)
        mean_prec, std_prec = calc_mean_std(precisions)
        mean_rec, std_rec = calc_mean_std(recalls)
        mean_f1, std_f1 = calc_mean_std(f1s)

        return AggregateEvaluationResponse(
            evaluated_images_count=n,
            mean_iou=mean_iou,
            std_iou=std_iou,
            mean_dice=mean_dice,
            std_dice=std_dice,
            mean_precision=mean_prec,
            std_precision=std_prec,
            mean_recall=mean_rec,
            std_recall=std_rec,
            mean_f1=mean_f1,
            std_f1=std_f1,
            mean_processing_time_ms=round(float(np.mean(times)), 2),
            per_image_results=per_image_list
        )
