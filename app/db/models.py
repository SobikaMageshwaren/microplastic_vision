import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class AnalysisModel(Base):
    __tablename__ = "analyses"

    analysis_id = Column(String(50), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    processing_time = Column(Float, nullable=False)
    particle_count = Column(Integer, nullable=False)
    total_detected_objects = Column(Integer, default=0)
    valid_particles = Column(Integer, default=0)
    filtered_objects = Column(Integer, default=0)
    pixel_size_um = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=False)
    pipeline_version = Column(String(50), default="classical-cv-v1.1")
    configuration_hash = Column(String(64), nullable=True, index=True)
    status = Column(String(20), default="completed")

    # Structured JSON stores for nested data & parameters
    image_info_json = Column(JSON, nullable=True)
    quality_info_json = Column(JSON, nullable=True)
    timing_json = Column(JSON, nullable=True)
    analytics_json = Column(JSON, nullable=True)
    configuration_json = Column(JSON, nullable=True)

    # Relationships
    particles = relationship("ParticleModel", back_populates="analysis", cascade="all, delete-orphan")
    artifacts = relationship("ArtifactModel", back_populates="analysis", cascade="all, delete-orphan")


class ParticleModel(Base):
    __tablename__ = "particles"

    particle_id = Column(String(50), primary_key=True, index=True)
    analysis_id = Column(String(50), ForeignKey("analyses.analysis_id"), primary_key=True, index=True)
    area = Column(Float, nullable=False)
    perimeter = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    aspect_ratio = Column(Float, nullable=False)
    circularity = Column(Float, nullable=False)
    eccentricity = Column(Float, nullable=False)
    solidity = Column(Float, nullable=False)
    extent = Column(Float, nullable=False)
    centroid_x = Column(Float, nullable=False)
    centroid_y = Column(Float, nullable=False)
    mean_intensity = Column(Float, nullable=False)
    std_intensity = Column(Float, nullable=False)
    
    # Full JSON payload for complete metrics
    features_json = Column(JSON, nullable=True)

    analysis = relationship("AnalysisModel", back_populates="particles")


class ArtifactModel(Base):
    __tablename__ = "artifacts"

    artifact_id = Column(String(50), primary_key=True, index=True)
    analysis_id = Column(String(50), ForeignKey("analyses.analysis_id"), index=True)
    artifact_type = Column(String(50), nullable=False)
    file_path = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    analysis = relationship("AnalysisModel", back_populates="artifacts")


class EvaluationModel(Base):
    __tablename__ = "evaluations"

    evaluation_id = Column(String(50), primary_key=True, index=True)
    analysis_id = Column(String(50), nullable=True, index=True)
    image_name = Column(String(255), nullable=False)
    iou = Column(Float, nullable=False)
    dice = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1 = Column(Float, nullable=False)
    tp_pixels = Column(Integer, default=0)
    fp_pixels = Column(Integer, default=0)
    fn_pixels = Column(Integer, default=0)
    tn_pixels = Column(Integer, default=0)
    predicted_particle_count = Column(Integer, nullable=True)
    ground_truth_particle_count = Column(Integer, nullable=True)
    particle_count_error = Column(Integer, nullable=True)
    processing_time_ms = Column(Float, default=0.0)
    error_map_path = Column(Text, nullable=True)
    overlay_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class ExperimentModel(Base):
    __tablename__ = "experiments"

    experiment_id = Column(String(50), primary_key=True, index=True)
    experiment_type = Column(String(50), default="ablation", index=True)
    experiment_name = Column(String(255), nullable=False)
    pipeline_version = Column(String(50), default="classical-cv-v1.1")
    configuration_hash = Column(String(64), nullable=True, index=True)
    configuration_json = Column(JSON, nullable=True)
    metrics_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class ModelRegistryModel(Base):
    __tablename__ = "model_registry"

    model_id = Column(String(50), primary_key=True, index=True)
    model_name = Column(String(255), nullable=False)
    architecture = Column(String(50), default="UNet-4Depth")
    version = Column(String(50), default="v1.0")
    checkpoint_path = Column(Text, nullable=False)
    configuration_hash = Column(String(64), nullable=True, index=True)
    dataset_split_json = Column(JSON, nullable=True)
    metrics_json = Column(JSON, nullable=True)
    status = Column(String(20), default="ready")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
