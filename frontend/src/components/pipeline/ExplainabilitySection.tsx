import React, { useState } from 'react';
import { Card } from '../common/Card';
import { Sliders, Eye, HelpCircle, Flame } from 'lucide-react';
import { apiService } from '../../services/api';
import { getImageUrl } from '../../utils/image';

interface ExplainabilitySectionProps {
  originalImagePath: string;
  analysisId?: string;
}

export const ExplainabilitySection: React.FC<ExplainabilitySectionProps> = ({ originalImagePath, analysisId }) => {
  const [threshold, setThreshold] = useState<number>(0.5);
  const [saliencyPath, setSaliencyPath] = useState<string | null>(null);
  const [loadingExplain, setLoadingExplain] = useState<boolean>(false);
  const [explainError, setExplainError] = useState<string | null>(null);

  const handleGenerateExplainability = async () => {
    setLoadingExplain(true);
    setExplainError(null);
    try {
      // Determine the exact analysis identifier
      let targetAnalysisId = analysisId;
      if (!targetAnalysisId && originalImagePath) {
        const match = originalImagePath.match(/ana_[a-zA-Z0-9]+/);
        if (match) targetAnalysisId = match[0];
      }
      if (!targetAnalysisId) {
        targetAnalysisId = 'latest';
      }

      // Compute explainability directly on the backend using the analysis context
      const explainRes = await apiService.explainModelSaliency(targetAnalysisId, 'unet-baseline-v1');
      if (explainRes && explainRes.heatmap_path) {
        setSaliencyPath(`${explainRes.heatmap_path}?t=${Date.now()}`);
      }
    } catch (e: any) {
      console.error('Failed to generate saliency attribution heatmap', e);
      const msg =
        e?.response?.data?.error?.message ||
        e?.response?.data?.detail ||
        e?.message ||
        'Could not compute gradient saliency attribution.';
      setExplainError(msg);
    } finally {
      setLoadingExplain(false);
    }
  };

  const resolvedOriginal = getImageUrl(originalImagePath);
  const resolvedSaliency = saliencyPath ? (saliencyPath.startsWith('http') ? saliencyPath : getImageUrl(saliencyPath)) : null;

  return (
    <Card
      title="U-Net Model Explainability & Probability Confidence Inspection"
      subtitle="Interactive probability threshold inspection and Input-Gradient Saliency Attribution heatmaps"
    >
      <div className="space-y-6">
        {/* 1. Threshold Interactive Slider */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <Sliders className="w-4 h-4 text-purple-600" /> Probability Segmentation Threshold
            </span>
            <span className="px-2.5 py-1 rounded-md text-xs font-mono font-extrabold bg-purple-100 text-purple-800 border border-purple-200">
              Threshold: {threshold.toFixed(2)}
            </span>
          </div>

          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-purple-600 cursor-pointer"
          />

          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>0.10 (High Sensitivity / Noise)</span>
            <span>0.50 (Balanced Standard)</span>
            <span>0.90 (High Precision / Strict)</span>
          </div>
        </div>

        {/* 2. Model Attribution Saliency Heatmap Section */}
        <div className="space-y-3 pt-2 border-t border-slate-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <Flame className="w-4 h-4 text-rose-500" /> Model Attribution Visualization (Input-Gradient Saliency)
              </h4>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Answers: Which input microscopy pixels contributed most strongly to the model's segmentation decision?
              </p>
            </div>

            <button
              onClick={handleGenerateExplainability}
              disabled={loadingExplain}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 text-white text-xs font-bold shadow-xs hover:bg-purple-700 disabled:opacity-50 transition-colors whitespace-nowrap self-start sm:self-auto"
            >
              {loadingExplain ? 'Computing Attribution...' : 'Generate Saliency Heatmap'}
            </button>
          </div>

          {explainError && (
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              {explainError}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center shadow-md">
              <span className="text-[11px] font-bold text-slate-300 block mb-1.5">Original Microscopy Input</span>
              <div className="h-48 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-800">
                {resolvedOriginal ? (
                  <img
                    src={resolvedOriginal}
                    alt="Original Input"
                    className="max-h-full max-w-full object-contain"
                  />
                ) : (
                  <span className="text-xs text-slate-500">No input image available</span>
                )}
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center shadow-md">
              <span className="text-[11px] font-bold text-rose-400 block mb-1.5">Input-Gradient Saliency Heatmap Overlay</span>
              <div className="h-48 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-800">
                {loadingExplain ? (
                  <div className="flex flex-col items-center justify-center text-rose-400 text-xs gap-2">
                    <div className="w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
                    <span>Computing backpropagated gradients...</span>
                  </div>
                ) : resolvedSaliency ? (
                  <img
                    src={resolvedSaliency}
                    alt="Saliency Heatmap"
                    className="max-h-full max-w-full object-contain"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center text-slate-500 text-xs gap-2 p-4 text-center">
                    <Flame className="w-8 h-8 opacity-30 text-rose-400" />
                    <span>Click &apos;Generate Saliency Heatmap&apos; to calculate pixel attribution map</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
