from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class BoundingBox(BaseModel):
    x: int = Field(..., description="Top-left X coordinate")
    y: int = Field(..., description="Top-left Y coordinate")
    width: int = Field(..., description="Bounding box width in pixels")
    height: int = Field(..., description="Bounding box height in pixels")


class Centroid(BaseModel):
    x: float = Field(..., description="Centroid X coordinate")
    y: float = Field(..., description="Centroid Y coordinate")


class ParticleFeatures(BaseModel):
    particle_id: str = Field(..., example="P001")
    analysis_id: str
    bbox: BoundingBox
    centroid: Centroid
    
    # Geometry
    area: float = Field(..., description="Particle area in pixels")
    perimeter: float = Field(..., description="Particle perimeter in pixels")
    width: float = Field(..., description="Bounding box width")
    height: float = Field(..., description="Bounding box height")
    aspect_ratio: float = Field(..., description="Width / Height aspect ratio")
    
    # Shape
    circularity: float = Field(..., description="4 * pi * area / (perimeter^2)")
    eccentricity: float = Field(..., description="Eccentricity of fitted ellipse")
    solidity: float = Field(..., description="Area / Convex Hull Area")
    extent: float = Field(..., description="Area / Bounding Box Area")
    compactness: float = Field(..., description="Perimeter^2 / Area")
    convex_hull_area: float = Field(..., description="Convex hull area in pixels")
    
    # Skeleton
    skeleton_length: float = Field(0.0, description="Length of skeletonized particle")
    mean_thickness: float = Field(0.0, description="Approximate thickness based on area/skeleton")
    
    # Optional Physical Calibration Measurements (when pixel_size_um is provided)
    pixel_size_um: Optional[float] = Field(None, description="Calibration scale in µm/pixel if provided")
    area_um2: Optional[float] = Field(None, description="Area in square micrometers (µm²)")
    perimeter_um: Optional[float] = Field(None, description="Perimeter in micrometers (µm)")
    width_um: Optional[float] = Field(None, description="Width in micrometers (µm)")
    height_um: Optional[float] = Field(None, description="Height in micrometers (µm)")
    skeleton_length_um: Optional[float] = Field(None, description="Skeleton length in micrometers (µm)")
    mean_thickness_um: Optional[float] = Field(None, description="Mean thickness in micrometers (µm)")
    
    # Intensity & Texture
    mean_intensity: float = Field(0.0, description="Mean pixel intensity")
    std_intensity: float = Field(0.0, description="Standard deviation of intensity")
    min_intensity: float = Field(0.0, description="Minimum pixel intensity")
    max_intensity: float = Field(0.0, description="Maximum pixel intensity")
    
    # Optional Texture
    glcm_contrast: Optional[float] = None
    glcm_energy: Optional[float] = None
    glcm_homogeneity: Optional[float] = None
    glcm_correlation: Optional[float] = None
    
    crop_path: Optional[str] = None
