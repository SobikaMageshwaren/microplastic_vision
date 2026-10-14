import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.database import init_db, SessionLocal
from app.services.analysis_service import AnalysisService
from app.services.evaluation_service import EvaluationService
from app.schemas.analysis import PreprocessingConfig


def main():
    parser = argparse.ArgumentParser(description="Run MicroPlastic-Vision Computer Vision Pipeline CLI")
    parser.add_argument("--image", required=True, help="Path to input microscopy image file")
    parser.add_argument("--gt-mask", help="Path to ground truth binary mask file (optional)")
    parser.add_argument("--threshold-method", default="otsu", choices=["otsu", "adaptive"], help="Thresholding method")
    
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Input image file '{image_path}' does not exist.")
        sys.exit(1)

    print(f"[*] Initializing MicroPlastic-Vision Pipeline...")
    init_db()
    db = SessionLocal()

    analysis_service = AnalysisService()
    config = PreprocessingConfig(threshold_method=args.threshold_method)

    print(f"[*] Running pipeline on: {image_path.name}...")
    result = analysis_service.run_full_pipeline(
        image_input=image_path,
        filename=image_path.name,
        db=db,
        prep_config=config
    )

    print("\n================ PIPELINE COMPLETE ================")
    print(f" Analysis ID     : {result.analysis_id}")
    print(f" Status          : {result.status}")
    print(f" Detected Count  : {result.particle_count} particles")
    print(f" Quality Score   : {result.quality_score} / 100")
    print(f" Processing Time : {result.processing_time:.3f} seconds")
    print("===================================================\n")

    if args.gt_mask:
        gt_path = Path(args.gt_mask)
        if gt_path.exists():
            print(f"[*] Running Ground-Truth Evaluation against '{gt_path.name}'...")
            eval_service = EvaluationService()
            # Fetch generated binary mask path from DB
            from app.db.crud import get_artifacts_by_analysis_id
            artifacts = get_artifacts_by_analysis_id(db, result.analysis_id)
            cleaned_mask_path = next((a.file_path for a in artifacts if a.artifact_type == "cleaned_mask"), None)

            if cleaned_mask_path and Path(cleaned_mask_path).exists():
                metrics = eval_service.evaluate_masks(cleaned_mask_path, gt_path)
                print("\n------------- EVALUATION METRICS -------------")
                print(f" IoU         : {metrics.iou:.4f}")
                print(f" Dice        : {metrics.dice:.4f}")
                print(f" Precision   : {metrics.precision:.4f}")
                print(f" Recall      : {metrics.recall:.4f}")
                print(f" F1 Score    : {metrics.f1:.4f}")
                print("----------------------------------------------\n")
            else:
                print("Warning: Cleaned mask artifact not found for evaluation.")
        else:
            print(f"Warning: Ground truth mask file '{gt_path}' not found.")

    db.close()


if __name__ == "__main__":
    main()
