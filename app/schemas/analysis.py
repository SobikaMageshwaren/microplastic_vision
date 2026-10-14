from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.particle import ParticleFeatures
from app.schemas.config import PipelineConfig


class ImageValidationInfo(BaseModel):
    valid: bool
    width: int
    height: int
    channels: int
    format: str
    file_size_bytes: int


class ImageQualityAssessment(BaseModel):
    blur_score: float = Field(..., description="Laplacian variance blur score")
    contrast_score: float = Field(..., description="Intensity standard deviation contrast score")
    noise_score: float = Field(..., description="Estimated high-frequency noise level")
    quality_score: float = Field(..., description="Heuristic quality score from 0 to 100")
    warnings: List[str] = Field(default_factory=list)


class PreprocessingConfig(BaseModel):
    denoise: bool = True
    background_correction: bool = True
    contrast_enhancement: bool = True
    normalize: bool = True
    threshold_method: str = Field("otsu", description="Threshold method: 'otsu' or 'adaptive'")


class PipelineTiming(BaseModel):
    validation_time: float = 0.0
    quality_time: float = 0.0
    preprocessing_time: float = 0.0
    thresholding_time: float = 0.0
    morphological_cleanup_time: float = 0.0
    watershed_time: float = 0.0
    particle_extraction_time: float = 0.0
    feature_extraction_time: float = 0.0
    analytics_time: float = 0.0
    evaluation_time: float = 0.0
    total_time: float = 0.0


class SampleAnalytics(BaseModel):
    particle_count: int
    total_detected_objects: int = 0
    valid_particles: int = 0
    filtered_objects: int = 0
    pixel_size_um: Optional[float] = None
    calibration_unit: str = "px"
    particle_density: float = Field(..., description="Particles per 10^6 square pixels or um^2")
    area_statistics: Dict[str, float] = Field(..., description="mean, median, min, max, std area")
    shape_statistics: Dict[str, Dict[str, float]] = Field(..., description="Statistics for circularity, aspect_ratio, solidity, eccentricity")
    size_distribution: Dict[str, int] = Field(..., description="Histogram bins for particle sizes")
    spatial_distribution: Dict[str, Any] = Field(..., description="Centroid spatial distribution breakdown")


class AnalysisCreateResponse(BaseModel):
    analysis_id: str
    status: str = "completed"
    particle_count: int
    total_detected_objects: int = 0
    valid_particles: int = 0
    filtered_objects: int = 0
    pixel_size_um: Optional[float] = None
    calibration_unit: str = "px"
    quality_score: float
    processing_time: float
    pipeline_version: str = "classical-cv-v1.1"
    configuration_hash: Optional[str] = None


class AnalysisDetailResponse(BaseModel):
    analysis_id: str
    filename: str
    created_at: str
    status: str
    pipeline_version: str = "classical-cv-v1.1"
    configuration_hash: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    
    # Calibration & Filtering Summary
    pixel_size_um: Optional[float] = None
    calibration_unit: str = "px"
    total_detected_objects: int = 0
    valid_particles: int = 0
    filtered_objects: int = 0
    
    # Image properties & quality
    image_info: ImageValidationInfo
    quality_assessment: ImageQualityAssessment
    
    # Timing
    timing: PipelineTiming
    
    # Analytics summary
    particle_count: int
    sample_analytics: SampleAnalytics
    
    # Artifacts & Particles
    artifacts: Dict[str, str] = Field(default_factory=dict, description="Artifact types mapped to file paths")
    particles: Optional[List[ParticleFeatures]] = None
