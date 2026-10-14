from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.db.database import get_db
from app.api.dependencies import get_analysis_service
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisCreateResponse, AnalysisDetailResponse, PreprocessingConfig, ImageValidationInfo, ImageQualityAssessment, PipelineTiming, SampleAnalytics
from app.schemas.particle import ParticleFeatures
from app.core.exceptions import AnalysisNotFoundError, ParticleNotFoundError
from app.db.crud import (
    get_analysis_by_id, get_particles_by_analysis_id, get_particle_by_id, get_artifacts_by_analysis_id
)

router = APIRouter(tags=["Analysis"])


def format_web_path(path_str: Optional[str]) -> Optional[str]:
    """Convert absolute disk file path into web-accessible relative HTTP path."""
    if not path_str:
        return path_str
    normalized = str(path_str).replace("\\", "/")
    if "/data/outputs/" in normalized:
        return "/data/outputs/" + normalized.split("/data/outputs/")[1]
    elif "data/outputs/" in normalized:
        return "/data/outputs/" + normalized.split("data/outputs/")[1]
    return path_str


from fastapi.responses import Response, JSONResponse
from app.schemas.config import PipelineConfig, PreprocessingParams, SegmentationParams, MorphologyParams, WatershedParams, FilteringParams
import csv
import io


@router.post("/analysis", response_model=AnalysisCreateResponse, status_code=status.HTTP_201_CREATED)
async def analyze_microscopy_image(
    file: UploadFile = File(..., description="Microscopy image file (PNG, JPG, TIFF)"),
    denoise: bool = Form(True),
    background_correction: bool = Form(True),
    contrast_enhancement: bool = Form(True),
    normalize: bool = Form(True),
    threshold_method: str = Form("otsu"),
    min_area_pixels: int = Form(5),
    max_area_pixels: Optional[int] = Form(None),
    pixel_size_um: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Upload a microscopy image and run the complete computer-vision analysis pipeline.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    pipeline_cfg = PipelineConfig(
        pixel_size_um=pixel_size_um,
        preprocessing=PreprocessingParams(
            denoise=denoise,
            background_correction=background_correction,
            contrast_enhancement=contrast_enhancement,
            normalize=normalize
        ),
        segmentation=SegmentationParams(
            threshold_method=threshold_method
        ),
        filtering=FilteringParams(
            min_area_pixels=min_area_pixels,
            max_area_pixels=max_area_pixels
        )
    )

    result = service.run_full_pipeline(
        image_input=content,
        filename=file.filename or "microscopy_image.tiff",
        db=db,
        pipeline_config=pipeline_cfg
    )

    return result


@router.get("/analysis/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis_details(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve full analysis report by analysis_id."""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    artifacts_records = get_artifacts_by_analysis_id(db, analysis_id)
    artifacts_dict = {a.artifact_type: format_web_path(a.file_path) for a in artifacts_records}

    particles_records = get_particles_by_analysis_id(db, analysis_id)
    particles_list = []
    for p in particles_records:
        feat_data = dict(p.features_json)
        if feat_data.get("crop_path"):
            feat_data["crop_path"] = format_web_path(feat_data["crop_path"])
        particles_list.append(ParticleFeatures(**feat_data))

    return AnalysisDetailResponse(
        analysis_id=analysis.analysis_id,
        filename=analysis.filename,
        created_at=analysis.created_at.isoformat(),
        status=analysis.status,
        pipeline_version=analysis.pipeline_version,
        configuration_hash=analysis.configuration_hash,
        configuration=analysis.configuration_json,
        image_info=ImageValidationInfo(**analysis.image_info_json),
        quality_assessment=ImageQualityAssessment(**analysis.quality_info_json),
        timing=PipelineTiming(**analysis.timing_json),
        particle_count=analysis.particle_count,
        sample_analytics=SampleAnalytics(**analysis.analytics_json),
        artifacts=artifacts_dict,
        particles=particles_list
    )


@router.get("/analysis/{analysis_id}/configuration", response_model=Dict[str, Any])
def get_analysis_configuration(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve exact processing configuration parameters and configuration_hash for an analysis session."""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    return {
        "analysis_id": analysis.analysis_id,
        "pipeline_version": analysis.pipeline_version,
        "configuration_hash": analysis.configuration_hash,
        "configuration": analysis.configuration_json or {}
    }


@router.get("/analysis/{analysis_id}/particles", response_model=List[ParticleFeatures])
def get_analysis_particles(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve list of extracted particles for an analysis session."""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    particles_records = get_particles_by_analysis_id(db, analysis_id)
    result = []
    for p in particles_records:
        feat_data = dict(p.features_json)
        if feat_data.get("crop_path"):
            feat_data["crop_path"] = format_web_path(feat_data["crop_path"])
        result.append(ParticleFeatures(**feat_data))
    return result


@router.get("/analysis/{analysis_id}/particles/{particle_id}", response_model=ParticleFeatures)
def get_single_particle(analysis_id: str, particle_id: str, db: Session = Depends(get_db)):
    """Retrieve features and metadata for a specific particle."""
    particle = get_particle_by_id(db, analysis_id, particle_id)
    if not particle:
        raise ParticleNotFoundError(particle_id)

    feat_data = dict(particle.features_json)
    if feat_data.get("crop_path"):
        feat_data["crop_path"] = format_web_path(feat_data["crop_path"])
    return ParticleFeatures(**feat_data)


@router.get("/analysis/{analysis_id}/artifacts", response_model=Dict[str, str])
def get_analysis_artifacts(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve dictionary of visual artifact paths generated for an analysis session."""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    artifacts_records = get_artifacts_by_analysis_id(db, analysis_id)
    return {a.artifact_type: format_web_path(a.file_path) for a in artifacts_records}


@router.get("/analysis/{analysis_id}/export/csv")
def export_analysis_csv(analysis_id: str, db: Session = Depends(get_db)):
    """Export extracted particle morphometrics and features as a CSV file attachment."""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    particles_records = get_particles_by_analysis_id(db, analysis_id)
    
    output = io.StringIO()
    writer = csv.writer(output)

    # Header columns
    headers = [
        "particle_id", "analysis_id", "area_px", "perimeter_px", "width_px", "height_px",
        "aspect_ratio", "circularity", "eccentricity", "solidity", "extent", "compactness",
        "skeleton_length_px", "mean_thickness_px", "centroid_x", "centroid_y",
        "mean_intensity", "std_intensity"
    ]
    if analysis.pixel_size_um:
        headers.extend([
            "pixel_size_um", "area_um2", "perimeter_um", "width_um", "height_um",
            "skeleton_length_um", "mean_thickness_um"
        ])
    writer.writerow(headers)

    for p in particles_records:
        feat = dict(p.features_json) if p.features_json else {}
        row = [
            p.particle_id, analysis_id, p.area, p.perimeter, p.width, p.height,
            p.aspect_ratio, p.circularity, p.eccentricity, p.solidity, p.extent,
            feat.get("compactness", 0.0), feat.get("skeleton_length", 0.0),
            feat.get("mean_thickness", 0.0), p.centroid_x, p.centroid_y,
            p.mean_intensity, p.std_intensity
        ]
        if analysis.pixel_size_um:
            row.extend([
                analysis.pixel_size_um,
                feat.get("area_um2"),
                feat.get("perimeter_um"),
                feat.get("width_um"),
                feat.get("height_um"),
                feat.get("skeleton_length_um"),
                feat.get("mean_thickness_um")
            ])
        writer.writerow(row)

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=microplastic_analysis_{analysis_id}.csv"}
    )


@router.get("/analysis/{analysis_id}/export/summary", response_model=Dict[str, Any])
def export_analysis_summary(analysis_id: str, db: Session = Depends(get_db)):
    """Export comprehensive scientific analysis summary report."""
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    return {
        "analysis_id": analysis.analysis_id,
        "filename": analysis.filename,
        "created_at": analysis.created_at.isoformat(),
        "status": analysis.status,
        "pipeline_version": analysis.pipeline_version,
        "configuration_hash": analysis.configuration_hash,
        "configuration": analysis.configuration_json or {},
        "calibration": {
            "pixel_size_um": analysis.pixel_size_um,
            "unit": "µm" if analysis.pixel_size_um else "px"
        },
        "object_detection_summary": {
            "total_detected_objects": analysis.total_detected_objects or analysis.particle_count,
            "valid_particles": analysis.valid_particles or analysis.particle_count,
            "filtered_objects": analysis.filtered_objects or 0
        },
        "image_info": analysis.image_info_json,
        "quality_assessment": analysis.quality_info_json,
        "timing": analysis.timing_json,
        "sample_analytics": analysis.analytics_json
    }

