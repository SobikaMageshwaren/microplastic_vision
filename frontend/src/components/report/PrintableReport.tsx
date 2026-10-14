import React from 'react';
import { Printer, Download, Microscope, CheckCircle2 } from 'lucide-react';
import { AnalysisDetailResponse } from '../../types/analysis';
import { formatDate, formatNumber } from '../../utils/formatting';

interface PrintableReportProps {
  analysis: AnalysisDetailResponse;
}

export const PrintableReport: React.FC<PrintableReportProps> = ({ analysis }) => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold">
            <Microscope className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">MicroPlastic-Vision Scientific Analysis Report</h2>
            <p className="text-xs text-slate-500">Automated Computer-Vision Microplastic Quantification</p>
          </div>
        </div>

        <button
          onClick={handlePrint}
          className="no-print px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold flex items-center gap-2 shadow-xs transition-colors"
        >
          <Printer className="w-4 h-4" />
          <span>Print / Export PDF</span>
        </button>
      </div>

      {/* Summary Metadata Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs mb-8">
        <div>
          <span className="text-slate-400 block mb-0.5">Analysis ID</span>
          <span className="font-mono font-bold text-slate-900">{analysis.analysis_id}</span>
        </div>
        <div>
          <span className="text-slate-400 block mb-0.5">Filename</span>
          <span className="font-semibold text-slate-900 truncate block">{analysis.filename}</span>
        </div>
        <div>
          <span className="text-slate-400 block mb-0.5">Processed Date</span>
          <span className="font-medium text-slate-800">{formatDate(analysis.created_at)}</span>
        </div>
        <div>
          <span className="text-slate-400 block mb-0.5">Pipeline Version</span>
          <span className="font-mono font-semibold text-indigo-600">{analysis.pipeline_version}</span>
        </div>
      </div>

      {/* Report Section 1: Sample & Quality Summary */}
      <div className="space-y-6 text-xs text-slate-700">
        <div>
          <h4 className="font-bold text-slate-900 text-sm uppercase tracking-wider mb-2 border-b border-slate-100 pb-1">
            1. Sample Quantitative Summary
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-2">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block">Total Particles</span>
              <span className="text-lg font-bold text-slate-900">{analysis.particle_count}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block">Mean Particle Area</span>
              <span className="text-lg font-bold text-slate-900">
                {formatNumber(analysis.sample_analytics.area_statistics.mean)} px²
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block">Mean Circularity</span>
              <span className="text-lg font-bold text-indigo-600">
                {analysis.sample_analytics.shape_statistics.circularity.mean}
              </span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block">Processing Duration</span>
              <span className="text-lg font-bold text-slate-900">
                {analysis.timing.total_time.toFixed(3)} s
              </span>
            </div>
          </div>
        </div>

        {/* Report Section 2: Image Quality */}
        <div>
          <h4 className="font-bold text-slate-900 text-sm uppercase tracking-wider mb-2 border-b border-slate-100 pb-1">
            2. Image Quality & Resolution
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-2 font-mono">
            <div>Dimensions: {analysis.image_info.width} × {analysis.image_info.height} px</div>
            <div>Blur Variance: {analysis.quality_assessment.blur_score}</div>
            <div>Contrast Std: {analysis.quality_assessment.contrast_score}</div>
            <div>Quality Score: {analysis.quality_assessment.quality_score} / 100</div>
          </div>
        </div>

        {/* Report Section 3: Processing Time Breakdown */}
        <div>
          <h4 className="font-bold text-slate-900 text-sm uppercase tracking-wider mb-2 border-b border-slate-100 pb-1">
            3. Stage Timing Breakdown
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-2 font-mono">
            <div>Validation: {analysis.timing.validation_time}s</div>
            <div>Preprocessing: {analysis.timing.preprocessing_time}s</div>
            <div>Segmentation: {analysis.timing.segmentation_time}s</div>
            <div>Instance Split: {analysis.timing.instance_time}s</div>
            <div>Feature Extract: {analysis.timing.feature_time}s</div>
            <div>Analytics: {analysis.timing.analytics_time}s</div>
          </div>
        </div>
      </div>

      <div className="mt-8 pt-4 border-t border-slate-200 text-center text-[11px] text-slate-400">
        Generated by MicroPlastic-Vision Automated Computer Vision Engine • Version 0.1.0
      </div>
    </div>
  );
};
