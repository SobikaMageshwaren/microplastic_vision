import time
import uuid
import datetime
import cv2
import numpy as np
from typing import Union, Dict, Any, List
from pathlib import Path
from sqlalchemy.orm import Session

from app.utils.image_io import load_image
from app.schemas.config import PipelineConfig, PreprocessingParams, SegmentationParams, MorphologyParams, WatershedParams
from app.schemas.common import AblationConfigResult, AblationExperimentResponse
from app.cv.preprocessing import preprocess_image
from app.cv.thresholding import apply_otsu_threshold
from app.cv.morphology import clean_binary_mask
from app.cv.watershed import separate_instances_watershed
from app.services.evaluation_service import EvaluationService
from app.db.models import ExperimentModel


class AblationService:
    def __init__(self):
        self.evaluation_service = EvaluationService()

    def run_ablation_study(
        self,
        image_input: Union[str, Path, bytes, np.ndarray],
        ground_truth_input: Union[str, Path, bytes, np.ndarray],
        image_name: str = "ablation_sample",
        db: Session = None
    ) -> AblationExperimentResponse:
        """
        Execute 4 real pipeline configurations against ground-truth mask.
        """
        img_bgr, gray_img = load_image(image_input)
        _, gt_gray = load_image(ground_truth_input)

        pipeline_config = PipelineConfig()
        config_hash = pipeline_config.compute_configuration_hash()
        exp_id = f"ABLATION-{uuid.uuid4().hex[:6].upper()}"

        results_table: List[AblationConfigResult] = []

        # =====================================================================
        # EXPERIMENT A: Baseline Otsu (No Preprocessing, No Morphology, No Watershed)
        # =====================================================================
        t0 = time.time()
        raw_otsu_mask = apply_otsu_threshold(gray_img)
        if np.mean(raw_otsu_mask) > 127:
            raw_otsu_mask = cv2.bitwise_not(raw_otsu_mask)
        eval_a = self.evaluation_service.evaluate_masks(raw_otsu_mask, gt_gray, image_name="Exp_A_Baseline")
        elapsed_a = round((time.time() - t0) * 1000.0, 2)

        results_table.append(AblationConfigResult(
            config_name="Baseline Otsu",
            iou=eval_a.iou,
            dice=eval_a.dice,
            precision=eval_a.precision,
            recall=eval_a.recall,
            f1=eval_a.f1,
            particle_count=eval_a.predicted_particle_count,
            processing_time_ms=elapsed_a
        ))

        # =====================================================================
        # EXPERIMENT B: Preprocessing + Otsu Thresholding (No Morphology, No Watershed)
        # =====================================================================
        t0 = time.time()
        from app.schemas.analysis import PreprocessingConfig
        prep_config = PreprocessingConfig()
        preproc_img, _ = preprocess_image(img_bgr, gray_img, prep_config)
        prep_otsu_mask = apply_otsu_threshold(preproc_img)
        if np.mean(prep_otsu_mask) > 127:
            prep_otsu_mask = cv2.bitwise_not(prep_otsu_mask)
        eval_b = self.evaluation_service.evaluate_masks(prep_otsu_mask, gt_gray, image_name="Exp_B_Preprocessing")
        elapsed_b = round((time.time() - t0) * 1000.0, 2)

        results_table.append(AblationConfigResult(
            config_name="+ Preprocessing",
            iou=eval_b.iou,
            dice=eval_b.dice,
            precision=eval_b.precision,
            recall=eval_b.recall,
            f1=eval_b.f1,
            particle_count=eval_b.predicted_particle_count,
            processing_time_ms=elapsed_b
        ))

        # =====================================================================
        # EXPERIMENT C: Preprocessing + Otsu + Morphological Opening & Closing
        # =====================================================================
        t0 = time.time()
        cleaned_mask = clean_binary_mask(prep_otsu_mask)
        eval_c = self.evaluation_service.evaluate_masks(cleaned_mask, gt_gray, image_name="Exp_C_Morphology")
        elapsed_c = round((time.time() - t0) * 1000.0, 2)

        results_table.append(AblationConfigResult(
            config_name="+ Morphology",
            iou=eval_c.iou,
            dice=eval_c.dice,
            precision=eval_c.precision,
            recall=eval_c.recall,
            f1=eval_c.f1,
            particle_count=eval_c.predicted_particle_count,
            processing_time_ms=elapsed_c
        ))

        # =====================================================================
        # EXPERIMENT D: Preprocessing + Otsu + Morphology + Distance Transform Watershed
        # =====================================================================
        t0 = time.time()
        watershed_labels, ws_particle_count = separate_instances_watershed(cleaned_mask)
        ws_binary = (watershed_labels > 0).astype(np.uint8) * 255
        eval_d = self.evaluation_service.evaluate_masks(ws_binary, gt_gray, image_name="Exp_D_Watershed")
        elapsed_d = round((time.time() - t0) * 1000.0, 2)

        results_table.append(AblationConfigResult(
            config_name="+ Watershed Instance Split",
            iou=eval_d.iou,
            dice=eval_d.dice,
            precision=eval_d.precision,
            recall=eval_d.recall,
            f1=eval_d.f1,
            particle_count=ws_particle_count,
            processing_time_ms=elapsed_d
        ))

        created_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        response = AblationExperimentResponse(
            experiment_id=exp_id,
            experiment_name=f"Pipeline Stage Ablation on {image_name}",
            pipeline_version="classical-cv-v1.1",
            configuration_hash=config_hash,
            evaluated_image_name=image_name,
            results_table=results_table,
            created_at=created_str
        )

        # Save Experiment in DB if session is available
        if db is not None:
            exp_record = ExperimentModel(
                experiment_id=exp_id,
                experiment_type="ablation",
                experiment_name=response.experiment_name,
                pipeline_version=response.pipeline_version,
                configuration_hash=config_hash,
                configuration_json=pipeline_config.model_dump(),
                metrics_json=[r.model_dump() for r in results_table]
            )
            db.add(exp_record)
            db.commit()

        return response
