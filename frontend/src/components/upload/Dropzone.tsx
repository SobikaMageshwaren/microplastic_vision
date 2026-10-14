import React, { useState, useRef } from 'react';
import { UploadCloud, FileImage, X, Sliders, Play, AlertCircle } from 'lucide-react';
import { PreprocessingConfig } from '../../types/analysis';
import { formatBytes } from '../../utils/formatting';

interface DropzoneProps {
  onStartAnalysis: (file: File, config: PreprocessingConfig) => void;
  loading: boolean;
  error?: string | null;
}

export const Dropzone: React.FC<DropzoneProps> = ({ onStartAnalysis, loading, error }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);

  // Pipeline parameters
  const [denoise, setDenoise] = useState<boolean>(true);
  const [backgroundCorrection, setBackgroundCorrection] = useState<boolean>(true);
  const [contrastEnhancement, setContrastEnhancement] = useState<boolean>(true);
  const [normalize, setNormalize] = useState<boolean>(true);
  const [thresholdMethod, setThresholdMethod] = useState<'otsu' | 'adaptive'>('otsu');

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    const ext = file.name.split('.').pop()?.toUpperCase() || '';
    const validExts = ['PNG', 'JPG', 'JPEG', 'TIFF', 'TIF'];
    if (!validExts.includes(ext)) {
      alert(`Invalid format .${ext}. Please select a PNG, JPG, JPEG, or TIFF image.`);
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const clearSelection = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleRun = () => {
    if (!selectedFile) return;
    onStartAnalysis(selectedFile, {
      denoise,
      background_correction: backgroundCorrection,
      contrast_enhancement: contrastEnhancement,
      normalize,
      threshold_method: thresholdMethod,
    });
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
      {error && (
        <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">Analysis Error</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
            dragActive
              ? 'border-indigo-600 bg-indigo-50/50 scale-[1.01]'
              : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50/80'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".png,.jpg,.jpeg,.tiff,.tif"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          />
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-xs">
            <UploadCloud className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-1">Upload Microscopy Image</h3>
          <p className="text-xs text-slate-500 mb-4 max-w-sm mx-auto">
            Drag and drop your raw microscopy file or click to browse. Max size 50MB.
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200">
            <FileImage className="w-3.5 h-3.5 text-slate-400" />
            <span>Supported: PNG • JPG • JPEG • TIFF</span>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row items-center gap-6 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="w-32 h-32 rounded-lg border border-slate-300 bg-slate-900 overflow-hidden shrink-0 flex items-center justify-center">
              {previewUrl ? (
                <img src={previewUrl} alt="Selected microscopy preview" className="w-full h-full object-contain" />
              ) : (
                <FileImage className="w-8 h-8 text-slate-500" />
              )}
            </div>

            <div className="flex-1 min-w-0 text-center sm:text-left">
              <h4 className="font-bold text-slate-900 text-base truncate">{selectedFile.name}</h4>
              <p className="text-xs text-slate-500 mt-1">Size: {formatBytes(selectedFile.size)}</p>
              <div className="mt-3 flex items-center justify-center sm:justify-start gap-2">
                <span className="text-xs px-2.5 py-1 rounded bg-indigo-100 text-indigo-800 font-semibold uppercase">
                  {selectedFile.name.split('.').pop()}
                </span>
                <button
                  type="button"
                  onClick={clearSelection}
                  disabled={loading}
                  className="text-xs text-rose-600 hover:text-rose-800 font-medium px-2 py-1 rounded hover:bg-rose-50 flex items-center gap-1 transition-colors"
                >
                  <X className="w-3.5 h-3.5" /> Remove
                </button>
              </div>
            </div>
          </div>

          {/* Pipeline Options Toggle */}
          <div className="p-5 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center gap-2 mb-4 text-slate-800 font-semibold text-sm">
              <Sliders className="w-4 h-4 text-indigo-600" />
              <span>Pipeline Configuration Parameters</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
              <label className="flex items-center gap-2.5 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={denoise}
                  onChange={(e) => setDenoise(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span className="font-medium text-slate-700">Denoise (FastNLMeans)</span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={backgroundCorrection}
                  onChange={(e) => setBackgroundCorrection(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span className="font-medium text-slate-700">Top-Hat Background Fix</span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={contrastEnhancement}
                  onChange={(e) => setContrastEnhancement(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span className="font-medium text-slate-700">CLAHE Contrast Boost</span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={normalize}
                  onChange={(e) => setNormalize(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span className="font-medium text-slate-700">Min-Max Normalization</span>
              </label>

              <div className="sm:col-span-2 flex items-center gap-3">
                <span className="font-semibold text-slate-700">Segmentation Algorithm:</span>
                <select
                  value={thresholdMethod}
                  onChange={(e) => setThresholdMethod(e.target.value as 'otsu' | 'adaptive')}
                  className="bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-800 font-medium focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="otsu">Otsu Thresholding (Global)</option>
                  <option value="adaptive">Gaussian Adaptive Thresholding</option>
                </select>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleRun}
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Processing CV Pipeline...' : 'Run Analysis Pipeline'}</span>
          </button>
        </div>
      )}
    </div>
  );
};
