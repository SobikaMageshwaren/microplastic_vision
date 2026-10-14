export interface HealthResponse {
  status: string;
  version: string;
}

export interface ModelInfoResponse {
  pipeline: string;
  segmentation_method: string;
  version: string;
  supported_formats: string[];
}

export interface EvaluationResponse {
  evaluation_id?: string;
  image_name: string;
  iou: number;
  dice: number;
  precision: number;
  recall: number;
  f1: number;
  tp_pixels: number;
  fp_pixels: number;
  fn_pixels: number;
  tn_pixels: number;
  predicted_particle_count?: number | null;
  ground_truth_particle_count?: number | null;
  particle_count_error?: number | null;
  processing_time_ms: number;
  error_map_path?: string | null;
  overlay_path?: string | null;
  created_at?: string | null;
}

export interface AggregateEvaluationResponse {
  evaluated_images_count: number;
  mean_iou: number;
  std_iou: number;
  mean_dice: number;
  std_dice: number;
  mean_precision: number;
  std_precision: number;
  mean_recall: number;
  std_recall: number;
  mean_f1: number;
  std_f1: number;
  mean_processing_time_ms: number;
  per_image_results: EvaluationResponse[];
}

export interface AblationConfigResult {
  config_name: string;
  iou: number;
  dice: number;
  precision: number;
  recall: number;
  f1: number;
  particle_count?: number | null;
  processing_time_ms: number;
}

export interface AblationExperimentResponse {
  experiment_id: string;
  experiment_name: string;
  pipeline_version: string;
  configuration_hash: string;
  evaluated_image_name: string;
  results_table: AblationConfigResult[];
  created_at: string;
}

export interface ModelComparisonResponse {
  evaluated_image: string;
  metrics_comparison: Array<{
    method: string;
    pipeline_version: string;
    iou: number;
    dice: number;
    precision: number;
    recall: number;
    f1: number;
    particle_count: number;
    processing_time_ms: number;
    predicted_mask_path?: string | null;
    error_map_path?: string | null;
    overlay_path?: string | null;
  }>;
  artifacts: Record<string, string>;
}

export interface SaliencyExplainabilityResponse {
  analysis_id: string;
  explainability_method: string;
  heatmap_path: string;
  description: string;
}
