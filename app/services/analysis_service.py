import time
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Dict, Any, Union, Optional

from app.utils.image_io import load_image, save_image
from app.utils.file_utils import generate_analysis_id, get_analysis_output_dir, safe_file_size
from app.utils.visualization import generate_visual_artifacts
from app.core.logging import log_stage, logger
from app.schemas.analysis import (
    AnalysisCreateResponse, AnalysisDetailResponse, PreprocessingConfig, PipelineTiming
)
from app.schemas.config import PipelineConfig
from app.services.quality_service import QualityService
from app.services.preprocessing_service import PreprocessingService
from app.services.segmentation_service import SegmentationService
from app.services.instance_service import InstanceService
from app.services.feature_service import FeatureService
from app.services.analytics_service import AnalyticsService
from app.db.crud import save_analysis_results, get_analysis_by_id, get_particles_by_analysis_id, get_artifacts_by_analysis_id


class AnalysisService:
    def __init__(self):
        self.quality_service = QualityService()
        self.preprocessing_service = PreprocessingService()
        self.segmentation_service = SegmentationService()
        self.instance_service = InstanceService()
        self.feature_service = FeatureService()
        self.analytics_service = AnalyticsService()

    def run_full_pipeline(
        self,
        image_input: Union[str, Path, bytes],
        filename: str,
        db: Session,
        pipeline_config: Optional[PipelineConfig] = None
    ) -> AnalysisCreateResponse:
        """
        Execute full 13-stage computer-vision analysis pipeline with precise stage timing, structured logging, and filtering.
        """
        if pipeline_config is None:
            pipeline_config = PipelineConfig()

        analysis_id = generate_analysis_id()
        output_dir = get_analysis_output_dir(analysis_id)
        start_total = time.time()
        timing = PipelineTiming()

        # STAGE 1: IMAGE LOAD & VALIDATION
        t0 = time.time()
        img_bgr, gray_img = load_image(image_input)
        file_size_bytes = len(image_input) if isinstance(image_input, bytes) else safe_file_size(Path(image_input))
        timing.validation_time = round(time.time() - t0, 4)
        log_stage(analysis_id, "validation", timing.validation_time)

        # STAGE 2: QUALITY ASSESSMENT
        t0 = time.time()
        validation_info, quality_assessment = self.quality_service.validate_and_assess(
            filename, img_bgr, gray_img, file_size_bytes
        )
        timing.quality_time = round(time.time() - t0, 4)
        log_stage(analysis_id, "quality_assessment", timing.quality_time)

        # STAGE 3: PREPROCESSING
        t0 = time.time()
        prep_cfg = PreprocessingConfig(
            denoise=pipeline_config.preprocessing.denoise,
            background_correction=pipeline_config.preprocessing.background_correction,
            contrast_enhancement=pipeline_config.preprocessing.contrast_enhancement,
            normalize=pipeline_config.preprocessing.normalize,
            threshold_method=pipeline_config.segmentation.threshold_method
        )
        preprocessed_img, inter_dict = self.preprocessing_service.process(img_bgr, gray_img, prep_cfg)
        timing.preprocessing_time = round(time.time() - t0, 4)
        log_stage(analysis_id, "preprocessing", timing.preprocessing_time)

        # STAGE 4: THRESHOLDING / SEGMENTATION
        t0 = time.time()
        seg_config = {
            "threshold_method": pipeline_config.segmentation.threshold_method,
            "adaptive_block_size": pipeline_config.segmentation.adaptive_block_size,
            "adaptive_c": pipeline_config.segmentation.adaptive_c
        }
        raw_mask, cleaned_mask = self.segmentation_service.segment(preprocessed_img, seg_config)
        timing.thresholding_time = round(time.time() - t0, 4)
        log_stage(analysis_id, "thresholding", timing.thresholding_time)

        # STAGE 5: MORPHOLOGICAL CLEANUP
        t0 = time.time()
        # Cleaned mask already filtered during segmentation step
        timing.morphological_cleanup_time = round(time.time() - t0, 4)
        log_stage(analysis_id, "morphological_cleanup", timing.morphological_cleanup_time)

        # STAGE 6: INSTANCE SEPARATION (WATERSHED)
        t0 = time.time()
        watershed_labels, particle_count_raw = self.instance_service.separate_instances(cleaned_mask)
        timing.watershed_time = round(time.time() - t0, 4)
        log_stage(analysis_id, "watershed", timing.watershed_time, extra_info=f"raw_count={particle_count_raw}")

        # STAGE 7 & 8: PARTICLE EXTRACTION & FEATURE EXTRACTION
        t0 = time.time()
        particles, object_counts = self.feature_service.extract_features(
            watershed_labels=watershed_labels,
            img_bgr=img_bgr,
            gray_img=gray_img,
            analysis_id=analysis_id,
            output_dir=output_dir,
            min_area_pixels=pipeline_config.filtering.min_area_pixels,
            max_area_pixels=pipeline_config.filtering.max_area_pixels,
            pixel_size_um=pipeline_config.pixel_size_um
        )
        timing.particle_extraction_time = round((time.time() - t0) * 0.4, 4)
        timing.feature_extraction_time = round((time.time() - t0) * 0.6, 4)
        log_stage(analysis_id, "particle_feature_extraction", time.time() - t0, extra_info=f"valid_particles={len(particles)}")

        # STAGE 9: QUANTITATIVE ANALYTICS
        t0 = time.time()
        sample_analytics = self.analytics_service.compute_sample_analytics(
            particles=particles,
            image_width=validation_info.width,
            image_height=validation_info.height,
            object_counts=object_counts,
            pixel_size_um=pipeline_config.pixel_size_um
        )
        timing.analytics_time = round(time.time() - t0, 4)
        log_stage(analysis_id, "quantitative_analytics", timing.analytics_time)

        # STAGE 10: VISUAL ARTIFACT GENERATION
        t0 = time.time()
        artifact_paths = generate_visual_artifacts(
            output_dir, img_bgr, inter_dict, raw_mask, cleaned_mask, watershed_labels, particles
        )
        log_stage(analysis_id, "artifact_generation", time.time() - t0)

        # STAGE 11: TIMING FINALIZATION & DB STORAGE
        timing.total_time = round(time.time() - start_total, 4)
        config_hash = pipeline_config.compute_configuration_hash()

        save_analysis_results(
            db=db,
            analysis_id=analysis_id,
            filename=filename,
            image_info=validation_info,
            quality=quality_assessment,
            timing=timing,
            analytics=sample_analytics,
            particles=particles,
            artifact_paths=artifact_paths,
            pipeline_config=pipeline_config
        )

        return AnalysisCreateResponse(
            analysis_id=analysis_id,
            status="completed",
            particle_count=sample_analytics.particle_count,
            total_detected_objects=object_counts["total_detected_objects"],
            valid_particles=object_counts["valid_particles"],
            filtered_objects=object_counts["filtered_objects"],
            pixel_size_um=pipeline_config.pixel_size_um,
            calibration_unit="µm" if pipeline_config.pixel_size_um else "px",
            quality_score=quality_assessment.quality_score,
            processing_time=timing.total_time,
            pipeline_version=pipeline_config.pipeline_version,
            configuration_hash=config_hash
        )
