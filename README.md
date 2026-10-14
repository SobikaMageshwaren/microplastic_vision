# MicroPlastic-Vision: Automated Microplastic Analysis

> **Scientific Disclaimer**: This application performs **image-based morphological and textural analysis of particles** from microscopy images using classical computer vision. It **does not chemically confirm polymer or plastic material identification** (e.g. via FTIR, Raman spectroscopy, or GC-MS). Physical measurements (`µm²`, `µm`) require microscope pixel-scale calibration (`pixel_size_um`).

---

## 1. Project Overview

**MicroPlastic-Vision** is a production-oriented scientific computer-vision application engineered for automated detection, segmentation, instance separation, feature extraction, and quantitative morphological analysis of microplastic particles from microscopy images.

The project features a **FastAPI backend**, a **React scientific workstation dashboard**, **PostgreSQL / SQLite database persistence**, deterministic **SHA-256 configuration hashing**, **error analysis maps**, **4-stage ablation studies**, and **CSV / JSON export capabilities**.

---

## 2. Key Phase 2 Production Readiness Features

1. **Configurable Particle Filtering**:
   - `min_area_pixels` (default 5 px) and optional `max_area_pixels`.
   - Tracks and reports `Total Detected Objects`, `Valid Particles`, and `Filtered Artifacts`.

2. **Optional Physical Pixel Calibration**:
   - Accepts `pixel_size_um` (e.g. `0.85 µm/pixel`).
   - Dynamically calculates physical morphometrics: `area_um2`, `perimeter_um`, `width_um`, `height_um`, `skeleton_length_um`, `mean_thickness_um`.
   - Clear UI indication: `Calibration: Not provided (px)` or `Calibration: 0.85 µm/pixel`.

3. **Input Validation & Security**:
   - File extension, MIME type, file size limit (50MB max), image readability, dimensions (min 10x10 px), channel normalization (Grayscale 1ch, BGR 3ch, BGRA 4ch).
   - Filename sanitization, path traversal prevention, structured JSON error responses (`{"error": {"code": "...", "message": "..."}}`).

4. **Structured Logging & Stage-Wise Timing**:
   - Contextual logging: `INFO analysis_id=MPV-001 stage=segmentation duration_ms=183 status=success`.
   - Microsecond precision breakdown across all 10 pipeline stages.

5. **Enhanced System Health Check**:
   - `/api/v1/health` verifies API status, Database connectivity (`SELECT 1`), Output storage permissions, and CV pipeline readiness.

6. **Reproducibility & Hashing**:
   - Fixed pipeline version string `classical-cv-v1.1`.
   - Canonical 64-character SHA-256 configuration hashing attached to all database records.

7. **Data & Report Exports**:
   - CSV export (`/api/v1/analysis/{id}/export/csv`) with physical unit columns.
   - Complete scientific summary JSON report export (`/api/v1/analysis/{id}/export/summary`).

---

## 3. Computer Vision Pipeline & Mathematical Formulas

```text
IMAGE UPLOAD (POST /api/v1/analysis)
     ↓
1. IMAGE VALIDATION & CHANNEL NORMALIZATION (Grayscale, BGR, BGRA -> BGR + Grayscale)
     ↓
2. QUALITY ASSESSMENT (Blur Score via Laplacian Variance, Contrast via StdDev, Noise Level)
     ↓
3. PREPROCESSING (Fast Non-Local Means Denoising, Top-Hat Illumination Correction, CLAHE, Normalization)
     ↓
4. THRESHOLDING / SEGMENTATION (Otsu Thresholding / Adaptive Gaussian Thresholding)
     ↓
5. MORPHOLOGICAL CLEANUP (Opening & Closing with Structuring Elements)
     ↓
6. WATERSHED INSTANCE SEPARATION (Distance Transform + Local Maxima Peak Markers + Watershed)
     ↓
7. PARTICLE EXTRACTION & FILTERING (Contours, Bounding Boxes, Centroids via Image Moments, Min/Max Area Filter)
     ↓
8. FEATURE EXTRACTION (Area, Perimeter, Aspect Ratio, Circularity, Solidity, Extent, Compactness, Skeleton, GLCM Texture)
     ↓
9. QUANTITATIVE SAMPLE ANALYTICS (Particle Density, Area/Shape Distributions, Quadrant Spatial Map)
     ↓
10. VISUAL ARTIFACT GENERATION (14 Overlay Maps & Visualizations)
     ↓
11. DB PERSISTENCE & API RESPONSE (Structured JSON + Exports)
```

### Key Mathematical Formulas
- **Laplacian Blur Score**: $S_{blur} = \text{Var}(\nabla^2 I)$
- **Circularity**: $C = \frac{4 \pi \cdot A}{P^2}$ (where $A$ = Area, $P$ = Perimeter)
- **Solidity**: $S = \frac{A}{A_{hull}}$ (where $A_{hull}$ = Convex Hull Area)
- **Extent**: $E = \frac{A}{w \times h}$
- **Compactness**: $K = \frac{P^2}{A}$
- **Physical Area**: $A_{\mu m^2} = A_{px} \times (\text{pixel\_size\_um})^2$
- **Physical Length**: $L_{\mu m} = L_{px} \times \text{pixel\_size\_um}$

---

## 4. API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Comprehensive system readiness check (API, DB, Storage, Pipeline) |
| `POST` | `/api/v1/analysis` | Upload image & run complete CV pipeline |
| `GET` | `/api/v1/analysis/{id}` | Get complete analysis report and particle inventory |
| `GET` | `/api/v1/analysis/{id}/configuration` | Get pipeline config and canonical SHA-256 hash |
| `GET` | `/api/v1/analysis/{id}/export/csv` | Download particle morphometrics CSV |
| `GET` | `/api/v1/analysis/{id}/export/summary` | Export scientific JSON summary report |
| `POST` | `/api/v1/evaluation` | Run single-image ground truth evaluation & error map |
| `GET` | `/api/v1/evaluations/aggregate` | Get aggregate evaluation statistics (Mean & Std) |
| `POST` | `/api/v1/experiments/ablation` | Execute 4-stage ablation study |

---

## 5. System Limitations

1. **Lack of Chemical Material Identification**: The system measures morphological and optical particle properties; it cannot confirm whether a particle is polyethylene, polypropylene, polystyrene, or organic matter.
2. **Dependence on Image Quality & Illumination**: Extremely blurry or unevenly illuminated microscopy images may require parameter tuning.
3. **Classical Thresholding Sensitivity**: High particle overlap or extreme noise can lead to minor over-segmentation or under-segmentation.
4. **Physical Scale Dependency**: Physical measurements (`µm²`, `µm`) require valid microscope pixel calibration.

---

## 6. Installation & Running Locally

### Prerequisites
- Python 3.12+
- Node.js 20+

### Start Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### Run Automated Tests
```bash
python -m pytest -v
```

### Run Performance Benchmark
```bash
python scripts/benchmark_pipeline.py
```

### Docker Deployment
```bash
docker compose up --build
```
