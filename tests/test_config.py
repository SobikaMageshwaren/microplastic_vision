import pytest
from pydantic import ValidationError
from app.schemas.config import PipelineConfig, PreprocessingParams, SegmentationParams, MorphologyParams


def test_pipeline_config_defaults_and_hash():
    config = PipelineConfig()
    assert config.pipeline_version == "classical-cv-v1.1"
    
    hash1 = config.compute_configuration_hash()
    hash2 = config.compute_configuration_hash()
    
    assert len(hash1) == 64  # SHA-256 hex length
    assert hash1 == hash2   # Deterministic hash


def test_even_kernel_size_validation_rejected():
    with pytest.raises(ValidationError):
        PreprocessingParams(top_hat_kernel_size=30)  # Even size must be rejected


def test_invalid_threshold_method_rejected():
    with pytest.raises(ValidationError):
        SegmentationParams(threshold_method="invalid_method")


def test_invalid_morphology_kernel_rejected():
    with pytest.raises(ValidationError):
        MorphologyParams(opening_kernel_size=4)
