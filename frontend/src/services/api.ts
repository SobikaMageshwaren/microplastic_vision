import axios from 'axios';
import {
  AnalysisCreateResponse,
  AnalysisDetailResponse,
  PreprocessingConfig,
} from '../types/analysis';
import { ParticleFeatures } from '../types/particle';
import {
  HealthResponse,
  ModelInfoResponse,
  EvaluationResponse,
  AggregateEvaluationResponse,
  AblationExperimentResponse,
  ModelComparisonResponse,
  SaliencyExplainabilityResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Accept': 'application/json',
  },
  timeout: 120000,
});

export const apiService = {
  // 1. Health check
  async getHealth(): Promise<HealthResponse> {
    const res = await api.get<HealthResponse>('/health');
    return res.data;
  },

  // 2. Model information
  async getModelInfo(): Promise<ModelInfoResponse> {
    const res = await api.get<ModelInfoResponse>('/model-info');
    return res.data;
  },

  // 3. Upload microscopy image and run analysis pipeline
  async analyzeImage(
    file: File,
    config?: Partial<PreprocessingConfig> & {
      min_area_pixels?: number;
      max_area_pixels?: number;
      pixel_size_um?: number;
    }
  ): Promise<AnalysisCreateResponse> {
    const formData = new FormData();
    formData.append('file', file);

    if (config) {
      if (config.denoise !== undefined) formData.append('denoise', String(config.denoise));
      if (config.background_correction !== undefined) formData.append('background_correction', String(config.background_correction));
      if (config.contrast_enhancement !== undefined) formData.append('contrast_enhancement', String(config.contrast_enhancement));
      if (config.normalize !== undefined) formData.append('normalize', String(config.normalize));
      if (config.threshold_method) formData.append('threshold_method', config.threshold_method);
      if (config.min_area_pixels !== undefined) formData.append('min_area_pixels', String(config.min_area_pixels));
      if (config.max_area_pixels !== undefined) formData.append('max_area_pixels', String(config.max_area_pixels));
      if (config.pixel_size_um !== undefined && config.pixel_size_um > 0) formData.append('pixel_size_um', String(config.pixel_size_um));
    }

    const res = await api.post<AnalysisCreateResponse>('/analysis', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  // Helper URLs for downloads
  getExportCsvUrl(analysisId: string): string {
    return `${API_BASE_URL}/api/v1/analysis/${analysisId}/export/csv`;
  },

  getExportSummaryUrl(analysisId: string): string {
    return `${API_BASE_URL}/api/v1/analysis/${analysisId}/export/summary`;
  },

  // 4. Get complete analysis details
  async getAnalysis(analysisId: string): Promise<AnalysisDetailResponse> {
    const res = await api.get<AnalysisDetailResponse>(`/analysis/${analysisId}`);
    return res.data;
  },

  // 5. Get configuration parameters and SHA-256 hash
  async getAnalysisConfiguration(analysisId: string): Promise<Record<string, any>> {
    const res = await api.get<Record<string, any>>(`/analysis/${analysisId}/configuration`);
    return res.data;
  },

  // 6. Get particles list
  async getParticles(analysisId: string): Promise<ParticleFeatures[]> {
    const res = await api.get<ParticleFeatures[]>(`/analysis/${analysisId}/particles`);
    return res.data;
  },

  // 7. Get single particle detail
  async getParticle(analysisId: string, particleId: string): Promise<ParticleFeatures> {
    const res = await api.get<ParticleFeatures>(`/analysis/${analysisId}/particles/${particleId}`);
    return res.data;
  },

  // 8. Get artifact paths mapping
  async getArtifacts(analysisId: string): Promise<Record<string, string>> {
    const res = await api.get<Record<string, string>>(`/analysis/${analysisId}/artifacts`);
    return res.data;
  },

  // 9. Ground truth single image evaluation with error map
  async evaluateMasks(
    predFile: File,
    gtFile: File,
    origFile?: File | null,
    imageName: string = 'evaluated_sample'
  ): Promise<EvaluationResponse> {
    const formData = new FormData();
    formData.append('predicted_mask', predFile);
    formData.append('ground_truth_mask', gtFile);
    if (origFile) formData.append('original_image', origFile);
    formData.append('image_name', imageName);

    const res = await api.post<EvaluationResponse>('/evaluation', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  // 10. Aggregate evaluation stats
  async getAggregateEvaluations(): Promise<AggregateEvaluationResponse> {
    const res = await api.get<AggregateEvaluationResponse>('/evaluations/aggregate');
    return res.data;
  },

  // 11. Run 4-stage ablation experiment
  async runAblationExperiment(
    imageFile?: File | null,
    gtFile?: File | null,
    useDatasetDefault: boolean = true
  ): Promise<AblationExperimentResponse> {
    const formData = new FormData();
    if (imageFile) formData.append('image', imageFile);
    if (gtFile) formData.append('ground_truth_mask', gtFile);
    formData.append('use_dataset_default', String(useDatasetDefault));

    const res = await api.post<AblationExperimentResponse>('/experiments/ablation', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  // 12. Get stored ablation experiment
  async getAblationExperiment(experimentId: string): Promise<AblationExperimentResponse> {
    const res = await api.get<AblationExperimentResponse>(`/experiments/ablation/${experimentId}`);
    return res.data;
  },

  // 13. Deep Learning Benchmark - List Models
  async listModels(): Promise<any[]> {
    const res = await api.get<any[]>('/models');
    return res.data;
  },

  // 14. Deep Learning Benchmark - Model Comparison (Classical CV vs U-Net)
  async getModelComparison(imageId: string = 'RR1.tiff', modelId?: string): Promise<ModelComparisonResponse> {
    const res = await api.get<ModelComparisonResponse>('/models/comparison', {
      params: { image_id: imageId, model_id: modelId },
    });
    return res.data;
  },

  // 15. Deep Learning Benchmark - Model Prediction
  async predictUnet(
    imageFile: File,
    threshold: number = 0.5,
    modelId?: string
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('image', imageFile);
    formData.append('threshold', String(threshold));
    if (modelId) formData.append('model_id', modelId);

    const targetUrl = modelId ? `/models/${modelId}/predict` : `/models/predict`;
    const res = await api.post<any>(targetUrl, formData);
    return res.data;
  },

  // 16. Deep Learning Benchmark - Input-Gradient Saliency Explainability
  async explainModelSaliency(
    analysisId: string = 'latest',
    modelId: string = 'unet-baseline-v1',
    imageFile?: File
  ): Promise<SaliencyExplainabilityResponse> {
    const formData = new FormData();
    if (imageFile) {
      formData.append('file', imageFile);
      formData.append('image', imageFile);
    }
    if (analysisId) {
      formData.append('analysis_id', analysisId);
    }

    const targetUrl = `/models/${modelId}/explain?analysis_id=${encodeURIComponent(analysisId)}`;

    const res = await api.post<SaliencyExplainabilityResponse>(targetUrl, formData);
    return res.data;
  },
};


