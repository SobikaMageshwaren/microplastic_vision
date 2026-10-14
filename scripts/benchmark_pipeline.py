"""
MicroPlastic-Vision Performance Benchmarking Script

Measures actual processing time, minimum, maximum, average stage timings across dataset images,
and records the performance benchmark into the experiments database table.
"""
import sys
import time
import json
from pathlib import Path

# Add workspace directory to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal, init_db
from app.services.analysis_service import AnalysisService
from app.schemas.config import PipelineConfig
from app.db.models import ExperimentModel
import numpy as np


def run_benchmark():
    print("=" * 70)
    print("MicroPlastic-Vision CV Pipeline Performance Benchmarking")
    print("=" * 70)

    init_db()
    db = SessionLocal()
    analysis_service = AnalysisService()

    dataset_dir = Path("dataset/original_size")
    image_paths = list(dataset_dir.glob("*.tiff")) + list(dataset_dir.glob("*.png")) + list(dataset_dir.glob("*.jpg"))
    
    if not image_paths:
        print("No dataset images found in dataset/original_size! Benchmarking cancelled.")
        return

    print(f"Found {len(image_paths)} images for performance benchmarking:\n")
    for img in image_paths:
        print(f"  - {img.name}")

    timings = []
    particle_counts = []
    config = PipelineConfig()

    for idx, img_path in enumerate(image_paths, 1):
        print(f"\n[{idx}/{len(image_paths)}] Benchmarking image: {img_path.name}...")
        start_t = time.time()
        
        try:
            with open(img_path, "rb") as f:
                img_bytes = f.read()

            res = analysis_service.run_full_pipeline(
                image_input=img_bytes,
                filename=img_path.name,
                db=db,
                pipeline_config=config
            )
            elapsed = time.time() - start_t
            timings.append(res.processing_time)
            particle_counts.append(res.particle_count)
            print(f"    [OK] Completed in {res.processing_time:.3f}s | Detected {res.particle_count} particles")
        except Exception as e:
            print(f"    [FAIL] Failed: {str(e)}")

    if timings:
        avg_time = float(np.mean(timings))
        min_time = float(np.min(timings))
        max_time = float(np.max(timings))
        std_time = float(np.std(timings))

        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY RESULTS")
        print("=" * 70)
        print(f"Total Evaluated Images : {len(timings)}")
        print(f"Average Processing Time: {avg_time:.4f} s")
        print(f"Minimum Processing Time: {min_time:.4f} s")
        print(f"Maximum Processing Time: {max_time:.4f} s")
        print(f"Standard Deviation     : {std_time:.4f} s")
        print(f"Average Particle Count : {np.mean(particle_counts):.1f}")
        print("=" * 70)

        # Store benchmark experiment in DB
        exp_id = f"BENCH-{int(time.time())}"
        metrics = {
            "evaluated_images_count": len(timings),
            "avg_processing_time_s": round(avg_time, 4),
            "min_processing_time_s": round(min_time, 4),
            "max_processing_time_s": round(max_time, 4),
            "std_processing_time_s": round(std_time, 4),
            "avg_particle_count": round(float(np.mean(particle_counts)), 1),
            "raw_timings": [round(t, 4) for t in timings]
        }

        exp_record = ExperimentModel(
            experiment_id=exp_id,
            experiment_type="benchmark",
            experiment_name=f"Pipeline Performance Benchmark ({len(timings)} images)",
            pipeline_version=config.pipeline_version,
            configuration_hash=config.compute_configuration_hash(),
            configuration_json=config.model_dump(),
            metrics_json=metrics
        )
        db.add(exp_record)
        db.commit()
        print(f"\n[OK] Saved benchmark experiment to DB record: {exp_id}")
    
    db.close()


if __name__ == "__main__":
    run_benchmark()
