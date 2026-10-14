import { ParticleFeatures } from './particle';

export interface ImageValidationInfo {
  valid: boolean;
  width: number;
  height: number;
  channels: number;
  format: string;
  file_size_bytes: number;
}

export interface ImageQualityAssessment {
  blur_score: number;
  contrast_score: number;
  noise_score: number;
  quality_score: number;
  warnings: string[];
}

export interface PreprocessingConfig {
  denoise: boolean;
  background_correction: boolean;
  contrast_enhancement: boolean;
  normalize: boolean;
  threshold_method: 'otsu' | 'adaptive';
}

export interface PipelineTiming {
  validation_time: number;
  quality_time: number;
  preprocessing_time: number;
  thresholding_time?: number;
  morphological_cleanup_time?: number;
  watershed_time?: number;
  particle_extraction_time?: number;
  feature_extraction_time?: number;
  segmentation_time?: number;
  instance_time?: number;
  feature_time?: number;
  analytics_time: number;
  evaluation_time?: number;
  total_time: number;
}

export interface SampleAnalytics {
  particle_count: number;
  total_detected_objects?: number;
  valid_particles?: number;
  filtered_objects?: number;
  pixel_size_um?: number | null;
  calibration_unit?: string;
  particle_density: number;
  area_statistics: {
    mean: number;
    median: number;
    min: number;
    max: number;
    std: number;
  };
  shape_statistics: {
    circularity: { mean: number; std: number };
    aspect_ratio: { mean: number; std: number };
    solidity: { mean: number; std: number };
    eccentricity: { mean: number; std: number };
  };
  size_distribution: Record<string, number>;
  spatial_distribution: {
    quadrant_counts: {
      top_left: number;
      top_right: number;
      bottom_left: number;
      bottom_right: number;
    };
  };
}

export interface AnalysisCreateResponse {
  analysis_id: string;
  status: string;
  particle_count: number;
  total_detected_objects?: number;
  valid_particles?: number;
  filtered_objects?: number;
  pixel_size_um?: number | null;
  calibration_unit?: string;
  quality_score: number;
  processing_time: number;
  pipeline_version: string;
  configuration_hash?: string;
}

export interface AnalysisDetailResponse {
  analysis_id: string;
  filename: string;
  created_at: string;
  status: string;
  pipeline_version: string;
  configuration_hash?: string;
  configuration?: Record<string, any>;
  pixel_size_um?: number | null;
  calibration_unit?: string;
  total_detected_objects?: number;
  valid_particles?: number;
  filtered_objects?: number;
  image_info: ImageValidationInfo;
  quality_assessment: ImageQualityAssessment;
  timing: PipelineTiming;
  particle_count: number;
  sample_analytics: SampleAnalytics;
  artifacts: Record<string, string>;
  particles: ParticleFeatures[];
}
