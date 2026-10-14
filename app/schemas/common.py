from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class HealthResponse(BaseModel):
    status: str = Field("healthy", json_schema_extra={"example": "healthy"})
    version: str = Field("classical-cv-v1.1", json_schema_extra={"example": "classical-cv-v1.1"})
    api: str = Field("healthy", description="API status")
    database: str = Field("healthy", description="Database connection status")
    storage: str = Field("healthy", description="Output directory storage status")
    pipeline: str = Field("ready", description="CV pipeline status")


class ModelInfoResponse(BaseModel):
    pipeline: str = Field(..., json_schema_extra={"example": "classical_cv"})
    segmentation_method: str = Field(..., json_schema_extra={"example": "watershed"})
    version: str = Field("classical-cv-v1.1", json_schema_extra={"example": "classical-cv-v1.1"})
    supported_formats: List[str] = Field(default_factory=lambda: ["PNG", "JPG", "JPEG", "TIFF", "TIF"])


class EvaluationRequest(BaseModel):
    predicted_mask_path: Optional[str] = None
    ground_truth_mask_path: Optional[str] = None


class EvaluationResponse(BaseModel):
    evaluation_id: Optional[str] = None
    image_name: str = "evaluated_image"
    iou: float = Field(..., description="Intersection over Union / Jaccard Index")
    dice: float = Field(..., description="Dice Similarity Coefficient")
    precision: float = Field(..., description="Precision score")
    recall: float = Field(..., description="Recall / Sensitivity score")
    f1: float = Field(..., description="F1 score")
    tp_pixels: int = Field(0, description="True positive pixels")
    fp_pixels: int = Field(0, description="False positive pixels")
    fn_pixels: int = Field(0, description="False negative pixels")
    tn_pixels: int = Field(0, description="True negative pixels")
    predicted_particle_count: Optional[int] = None
    ground_truth_particle_count: Optional[int] = None
    particle_count_error: Optional[int] = None
    processing_time_ms: float = 0.0
    error_map_path: Optional[str] = None
    overlay_path: Optional[str] = None
    created_at: Optional[str] = None


class AggregateEvaluationResponse(BaseModel):
    evaluated_images_count: int
    mean_iou: float
    std_iou: float
    mean_dice: float
    std_dice: float
    mean_precision: float
    std_precision: float
    mean_recall: float
    std_recall: float
    mean_f1: float
    std_f1: float
    mean_processing_time_ms: float
    per_image_results: List[EvaluationResponse]


class AblationConfigResult(BaseModel):
    config_name: str = Field(..., description="Configuration stage name e.g. Baseline Otsu, + Preprocessing, etc.")
    iou: float
    dice: float
    precision: float
    recall: float
    f1: float
    particle_count: Optional[int] = None
    processing_time_ms: float


class AblationExperimentResponse(BaseModel):
    experiment_id: str
    experiment_name: str
    pipeline_version: str = "classical-cv-v1.1"
    configuration_hash: str
    evaluated_image_name: str
    results_table: List[AblationConfigResult]
    created_at: str


class ArtifactItem(BaseModel):
    artifact_id: str
    analysis_id: str
    artifact_type: str
    file_path: str
    created_at: str
