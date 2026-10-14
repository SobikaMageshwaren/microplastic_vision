import numpy as np
from pathlib import Path
from typing import List
from app.cv.contours import extract_particle_regions
from app.cv.features import extract_particle_features
from app.schemas.particle import ParticleFeatures


from typing import List, Dict, Any, Tuple, Optional
from app.cv.contours import extract_particle_regions
from app.cv.features import extract_particle_features
from app.schemas.particle import ParticleFeatures


class FeatureService:
    def extract_features(
        self,
        watershed_labels: np.ndarray,
        img_bgr: np.ndarray,
        gray_img: np.ndarray,
        analysis_id: str,
        output_dir: Path,
        min_area_pixels: int = 5,
        max_area_pixels: Optional[int] = None,
        pixel_size_um: Optional[float] = None
    ) -> Tuple[List[ParticleFeatures], Dict[str, int]]:
        extraction_result = extract_particle_regions(
            watershed_labels=watershed_labels,
            img_bgr=img_bgr,
            analysis_id=analysis_id,
            output_dir=output_dir,
            min_area_pixels=min_area_pixels,
            max_area_pixels=max_area_pixels
        )
        
        particle_infos = extraction_result["particles"]
        object_counts = {
            "total_detected_objects": extraction_result["total_detected_objects"],
            "valid_particles": extraction_result["valid_particles"],
            "filtered_objects": extraction_result["filtered_objects"]
        }
        
        features_list = []
        for info in particle_infos:
            features = extract_particle_features(
                particle_info=info,
                gray_img=gray_img,
                analysis_id=analysis_id,
                pixel_size_um=pixel_size_um
            )
            features_list.append(features)
            
        return features_list, object_counts
