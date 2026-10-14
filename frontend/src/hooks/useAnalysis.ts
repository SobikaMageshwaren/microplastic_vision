import { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import { AnalysisDetailResponse, PreprocessingConfig } from '../types/analysis';

export function useAnalysis() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisDetailResponse | null>(null);

  const fetchAnalysis = useCallback(async (analysisId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getAnalysis(analysisId);
      setAnalysis(data);
      return data;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to fetch analysis details.';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const runAnalysis = useCallback(
    async (file: File, config?: Partial<PreprocessingConfig>) => {
      setLoading(true);
      setError(null);
      try {
        const createRes = await apiService.analyzeImage(file, config);
        const detailRes = await apiService.getAnalysis(createRes.analysis_id);
        setAnalysis(detailRes);
        return detailRes;
      } catch (err: any) {
        const msg = err.response?.data?.detail || err.message || 'Pipeline analysis failed.';
        setError(msg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    loading,
    error,
    analysis,
    fetchAnalysis,
    runAnalysis,
  };
}
