import json
import hashlib
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional


class PreprocessingParams(BaseModel):
    denoise: bool = True
    fast_nl_means_h: float = Field(10.0, ge=1.0, le=50.0, description="Denoising filter strength")
    fast_nl_means_template_window: int = Field(7, ge=3, le=15, description="Template window size (must be odd)")
    fast_nl_means_search_window: int = Field(21, ge=7, le=35, description="Search window size (must be odd)")
    
    background_correction: bool = True
    top_hat_kernel_size: int = Field(31, ge=3, le=101, description="Top-Hat structuring element size (must be odd)")
    
    contrast_enhancement: bool = True
    clahe_clip_limit: float = Field(3.0, ge=0.5, le=10.0, description="CLAHE contrast clip limit")
    clahe_tile_grid_size: int = Field(8, ge=2, le=32, description="CLAHE grid size")
    
    normalize: bool = True

    @field_validator('fast_nl_means_template_window', 'fast_nl_means_search_window', 'top_hat_kernel_size')
    @classmethod
    def validate_odd_positive(cls, v: int) -> int:
        if v % 2 == 0:
            raise ValueError(f"Kernel size must be an odd positive integer, got {v}")
        return v


class SegmentationParams(BaseModel):
    threshold_method: str = Field("otsu", description="Threshold method: 'otsu' or 'adaptive'")
    adaptive_block_size: int = Field(15, ge=3, le=99, description="Adaptive threshold block size (must be odd)")
    adaptive_c: float = Field(2.0, ge=-10.0, le=20.0, description="Adaptive threshold constant C")

    @field_validator('threshold_method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in {'otsu', 'adaptive'}:
            raise ValueError(f"Invalid threshold method '{v}'. Must be 'otsu' or 'adaptive'.")
        return v_lower

    @field_validator('adaptive_block_size')
    @classmethod
    def validate_block_size(cls, v: int) -> int:
        if v % 2 == 0:
            raise ValueError(f"Adaptive block size must be an odd integer, got {v}")
        return v


class MorphologyParams(BaseModel):
    opening_kernel_size: int = Field(3, ge=1, le=31, description="Opening kernel size (must be odd)")
    closing_kernel_size: int = Field(5, ge=1, le=31, description="Closing kernel size (must be odd)")

    @field_validator('opening_kernel_size', 'closing_kernel_size')
    @classmethod
    def validate_odd_kernel(cls, v: int) -> int:
        if v % 2 == 0:
            raise ValueError(f"Morphology kernel size must be an odd integer, got {v}")
        return v


class WatershedParams(BaseModel):
    min_distance: int = Field(7, ge=1, le=50, description="Minimum distance between local maxima peaks")


class FilteringParams(BaseModel):
    min_area_pixels: int = Field(5, ge=1, le=1000, description="Minimum particle area in pixels to filter noise")
    max_area_pixels: Optional[int] = Field(None, ge=1, description="Optional maximum particle area in pixels")


class PipelineConfig(BaseModel):
    pipeline_version: str = Field("classical-cv-v1.1", description="Pipeline version string")
    pixel_size_um: Optional[float] = Field(None, gt=0.0, description="Microscope physical pixel size in micrometers (µm/pixel)")
    preprocessing: PreprocessingParams = Field(default_factory=PreprocessingParams)
    segmentation: SegmentationParams = Field(default_factory=SegmentationParams)
    morphology: MorphologyParams = Field(default_factory=MorphologyParams)
    watershed: WatershedParams = Field(default_factory=WatershedParams)
    filtering: FilteringParams = Field(default_factory=FilteringParams)

    def compute_configuration_hash(self) -> str:
        """
        Generate deterministic 64-character SHA-256 hash derived from canonical JSON of configuration.
        """
        canonical_dict = self.model_dump()
        canonical_json = json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
