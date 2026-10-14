import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Dropzone } from '../components/upload/Dropzone';
import { useAnalysis } from '../hooks/useAnalysis';
import { PreprocessingConfig } from '../types/analysis';
import { Microscope, Sparkles, Activity, ShieldCheck, Cpu } from 'lucide-react';

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const { loading, error, runAnalysis } = useAnalysis();

  const handleStartAnalysis = async (file: File, config: PreprocessingConfig) => {
    try {
      const res = await runAnalysis(file, config);
      navigate(`/analysis/${res.analysis_id}`);
    } catch (err) {
      // Error handled by hook
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-12">
      {/* Hero Header */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold shadow-2xs">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Classical Computer Vision Engine v0.1.0</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
          MicroPlastic-Vision
        </h1>

        <p className="text-base sm:text-lg text-slate-600 font-normal leading-relaxed">
          Automated computer-vision microplastic particle detection, watershed instance separation, geometric feature extraction, and quantitative morphological analysis.
        </p>
      </div>

      {/* Main Upload Dropzone Workstation */}
      <Dropzone onStartAnalysis={handleStartAnalysis} loading={loading} error={error} />

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-slate-600">
        <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
          <div className="w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold mb-2">
            <Microscope className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-sm">Automated Pipeline</h3>
          <p className="text-slate-500 leading-relaxed">
            13-stage automated computer-vision pipeline including FastNLMeans denoising, top-hat background fix, CLAHE, and watershed segmentation.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
          <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold mb-2">
            <Activity className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-sm">Feature Extraction</h3>
          <p className="text-slate-500 leading-relaxed">
            Measures particle area, perimeter, circularity, aspect ratio, solidity, eccentricity, skeleton thickness, and GLCM texture features.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
          <div className="w-9 h-9 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center font-bold mb-2">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-sm">Modular Engine</h3>
          <p className="text-slate-500 leading-relaxed">
            Architected with a pluggable <code className="font-mono text-purple-700">SegmentationEngine</code> interface ready for future PyTorch U-Net & YOLO-Seg modules.
          </p>
        </div>
      </div>
    </div>
  );
};
