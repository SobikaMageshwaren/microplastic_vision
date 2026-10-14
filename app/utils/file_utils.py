import os
import uuid
import shutil
from pathlib import Path
from app.core.config import settings


def generate_analysis_id() -> str:
    """Generate a unique deterministic analysis ID."""
    return f"ana_{uuid.uuid4().hex[:12]}"


def get_analysis_output_dir(analysis_id: str) -> Path:
    """Get output directory for a given analysis ID and ensure it exists."""
    output_dir = settings.OUTPUT_DIR / analysis_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "particles").mkdir(parents=True, exist_ok=True)
    return output_dir


def safe_file_size(file_path: Path) -> int:
    """Return size of file in bytes, or 0 if file does not exist."""
    if file_path.exists():
        return file_path.stat().st_size
    return 0
