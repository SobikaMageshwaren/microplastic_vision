import numpy as np
from typing import List, Dict, Any, Optional
from app.schemas.particle import ParticleFeatures
from app.schemas.analysis import SampleAnalytics


class AnalyticsService:
    def compute_sample_analytics(
        self,
        particles: List[ParticleFeatures],
        image_width: int,
        image_height: int,
        object_counts: Optional[Dict[str, int]] = None,
        pixel_size_um: Optional[float] = None
    ) -> SampleAnalytics:
        particle_count = len(particles)
        img_area = float(image_width * image_height)
        particle_density = (particle_count / img_area * 1e6) if img_area > 0 else 0.0

        counts = object_counts or {
            "total_detected_objects": particle_count,
            "valid_particles": particle_count,
            "filtered_objects": 0
        }
        calib_unit = "µm" if pixel_size_um else "px"

        if particle_count == 0:
            return SampleAnalytics(
                particle_count=0,
                total_detected_objects=counts.get("total_detected_objects", 0),
                valid_particles=0,
                filtered_objects=counts.get("filtered_objects", 0),
                pixel_size_um=pixel_size_um,
                calibration_unit=calib_unit,
                particle_density=0.0,
                area_statistics={"mean": 0, "median": 0, "min": 0, "max": 0, "std": 0},
                shape_statistics={
                    "circularity": {"mean": 0, "std": 0},
                    "aspect_ratio": {"mean": 0, "std": 0},
                    "solidity": {"mean": 0, "std": 0},
                    "eccentricity": {"mean": 0, "std": 0}
                },
                size_distribution={"<50": 0, "50-200": 0, "200-500": 0, "500-1000": 0, ">1000": 0},
                spatial_distribution={"quadrant_counts": {"top_left": 0, "top_right": 0, "bottom_left": 0, "bottom_right": 0}}
            )

        areas = np.array([p.area for p in particles])
        circs = np.array([p.circularity for p in particles])
        aspects = np.array([p.aspect_ratio for p in particles])
        solidities = np.array([p.solidity for p in particles])
        eccentricities = np.array([p.eccentricity for p in particles])

        area_stats = {
            "mean": round(float(np.mean(areas)), 2),
            "median": round(float(np.median(areas)), 2),
            "min": round(float(np.min(areas)), 2),
            "max": round(float(np.max(areas)), 2),
            "std": round(float(np.std(areas)), 2)
        }

        shape_stats = {
            "circularity": {"mean": round(float(np.mean(circs)), 4), "std": round(float(np.std(circs)), 4)},
            "aspect_ratio": {"mean": round(float(np.mean(aspects)), 4), "std": round(float(np.std(aspects)), 4)},
            "solidity": {"mean": round(float(np.mean(solidities)), 4), "std": round(float(np.std(solidities)), 4)},
            "eccentricity": {"mean": round(float(np.mean(eccentricities)), 4), "std": round(float(np.std(eccentricities)), 4)}
        }

        # Size distribution bins
        size_dist = {
            "<50": int(np.sum(areas < 50)),
            "50-200": int(np.sum((areas >= 50) & (areas < 200))),
            "200-500": int(np.sum((areas >= 200) & (areas < 500))),
            "500-1000": int(np.sum((areas >= 500) & (areas < 1000))),
            ">1000": int(np.sum(areas >= 1000))
        }

        # Spatial distribution across image quadrants
        mid_x, mid_y = image_width / 2.0, image_height / 2.0
        tl = tr = bl = br = 0
        for p in particles:
            if p.centroid.x < mid_x and p.centroid.y < mid_y:
                tl += 1
            elif p.centroid.x >= mid_x and p.centroid.y < mid_y:
                tr += 1
            elif p.centroid.x < mid_x and p.centroid.y >= mid_y:
                bl += 1
            else:
                br += 1

        spatial_dist = {
            "quadrant_counts": {
                "top_left": tl,
                "top_right": tr,
                "bottom_left": bl,
                "bottom_right": br
            }
        }

        return SampleAnalytics(
            particle_count=particle_count,
            total_detected_objects=counts.get("total_detected_objects", particle_count),
            valid_particles=counts.get("valid_particles", particle_count),
            filtered_objects=counts.get("filtered_objects", 0),
            pixel_size_um=pixel_size_um,
            calibration_unit=calib_unit,
            particle_density=round(particle_density, 2),
            area_statistics=area_stats,
            shape_statistics=shape_stats,
            size_distribution=size_dist,
            spatial_distribution=spatial_dist
        )
