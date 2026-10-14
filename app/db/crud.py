import uuid
import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.db.models import AnalysisModel, ParticleModel, ArtifactModel
from app.schemas.analysis import AnalysisDetailResponse, ImageValidationInfo, ImageQualityAssessment, PipelineTiming, SampleAnalytics
from app.schemas.particle import ParticleFeatures


def save_analysis_results(
    db: Session,
    analysis_id: str,
    filename: str,
    image_info: ImageValidationInfo,
    quality: ImageQualityAssessment,
    timing: PipelineTiming,
    analytics: SampleAnalytics,
    particles: List[ParticleFeatures],
    artifact_paths: Dict[str, str],
    pipeline_config: Optional[Any] = None
) -> AnalysisModel:
    """Save complete analysis session, particle measurements, and artifacts into DB."""
    
    version = pipeline_config.pipeline_version if pipeline_config else "classical-cv-v1.1"
    config_hash = pipeline_config.compute_configuration_hash() if pipeline_config else None
    config_json = pipeline_config.model_dump() if pipeline_config else None

    # 1. Save Analysis record
    analysis_record = AnalysisModel(
        analysis_id=analysis_id,
        filename=filename,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        image_width=image_info.width,
        image_height=image_info.height,
        processing_time=timing.total_time,
        particle_count=analytics.particle_count,
        total_detected_objects=analytics.total_detected_objects,
        valid_particles=analytics.valid_particles,
        filtered_objects=analytics.filtered_objects,
        pixel_size_um=analytics.pixel_size_um,
        quality_score=quality.quality_score,
        pipeline_version=version,
        configuration_hash=config_hash,
        configuration_json=config_json,
        status="completed",
        image_info_json=image_info.model_dump(),
        quality_info_json=quality.model_dump(),
        timing_json=timing.model_dump(),
        analytics_json=analytics.model_dump()
    )
    db.add(analysis_record)

    # 2. Save Particle records
    for p in particles:
        particle_record = ParticleModel(
            particle_id=p.particle_id,
            analysis_id=analysis_id,
            area=p.area,
            perimeter=p.perimeter,
            width=p.width,
            height=p.height,
            aspect_ratio=p.aspect_ratio,
            circularity=p.circularity,
            eccentricity=p.eccentricity,
            solidity=p.solidity,
            extent=p.extent,
            centroid_x=p.centroid.x,
            centroid_y=p.centroid.y,
            mean_intensity=p.mean_intensity,
            std_intensity=p.std_intensity,
            features_json=p.model_dump()
        )
        db.add(particle_record)

    # 3. Save Artifact records
    for artifact_type, file_path in artifact_paths.items():
        artifact_record = ArtifactModel(
            artifact_id=f"art_{uuid.uuid4().hex[:10]}",
            analysis_id=analysis_id,
            artifact_type=artifact_type,
            file_path=file_path,
            created_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(artifact_record)

    db.commit()
    db.refresh(analysis_record)
    return analysis_record


def get_analysis_by_id(db: Session, analysis_id: str) -> Optional[AnalysisModel]:
    """Retrieve Analysis DB record by analysis_id."""
    return db.query(AnalysisModel).filter(AnalysisModel.analysis_id == analysis_id).first()


def get_particles_by_analysis_id(db: Session, analysis_id: str) -> List[ParticleModel]:
    """Retrieve all particle records for a given analysis_id."""
    return db.query(ParticleModel).filter(ParticleModel.analysis_id == analysis_id).all()


def get_particle_by_id(db: Session, analysis_id: str, particle_id: str) -> Optional[ParticleModel]:
    """Retrieve a specific particle record."""
    return db.query(ParticleModel).filter(
        ParticleModel.analysis_id == analysis_id,
        ParticleModel.particle_id == particle_id
    ).first()


from app.db.models import AnalysisModel, ParticleModel, ArtifactModel, ModelRegistryModel


def get_artifacts_by_analysis_id(db: Session, analysis_id: str) -> List[ArtifactModel]:
    """Retrieve all visual artifact records for an analysis_id."""
    return db.query(ArtifactModel).filter(ArtifactModel.analysis_id == analysis_id).all()


def register_trained_model(
    db: Session,
    model_id: str,
    model_name: str,
    architecture: str,
    version: str,
    checkpoint_path: str,
    configuration_hash: Optional[str] = None,
    dataset_split: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None
) -> ModelRegistryModel:
    """Register a trained deep-learning benchmark model in the model registry."""
    existing = db.query(ModelRegistryModel).filter(ModelRegistryModel.model_id == model_id).first()
    if existing:
        existing.checkpoint_path = checkpoint_path
        existing.metrics_json = metrics
        existing.dataset_split_json = dataset_split
        db.commit()
        db.refresh(existing)
        return existing

    record = ModelRegistryModel(
        model_id=model_id,
        model_name=model_name,
        architecture=architecture,
        version=version,
        checkpoint_path=checkpoint_path,
        configuration_hash=configuration_hash,
        dataset_split_json=dataset_split,
        metrics_json=metrics,
        status="ready",
        created_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_model_by_id(db: Session, model_id: str) -> Optional[ModelRegistryModel]:
    """Retrieve ModelRegistryModel by model_id."""
    return db.query(ModelRegistryModel).filter(ModelRegistryModel.model_id == model_id).first()


def list_registered_models(db: Session) -> List[ModelRegistryModel]:
    """List all registered deep learning benchmark models."""
    return db.query(ModelRegistryModel).order_by(ModelRegistryModel.created_at.desc()).all()
