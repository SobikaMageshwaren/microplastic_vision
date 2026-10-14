import React from 'react';
import { ShieldCheck, AlertTriangle, Eye, Sparkles, Activity } from 'lucide-react';
import { ImageValidationInfo, ImageQualityAssessment } from '../../types/analysis';
import { Card } from '../common/Card';
import { MetricBadge } from '../common/MetricBadge';
import { ScientificImageViewer } from '../image-viewer/ScientificImageViewer';

interface QualitySectionProps {
  imageInfo: ImageValidationInfo;
  quality: ImageQualityAssessment;
  originalPath: string;
}

export const QualitySection: React.FC<QualitySectionProps> = ({
  imageInfo,
  quality,
  originalPath,
}) => {
  return (
    <Card
      title="Image Properties & Quality Assessment"
      subtitle="Evaluation of microscopy input resolution, blur variance, contrast, and noise heuristics"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Large Original Image Viewer */}
        <div className="lg:col-span-7">
          <ScientificImageViewer
            src={originalPath}
            alt="Original Microscopy Image"
            title="Original Input Microscopy Image"
            caption={`${imageInfo.width} × ${imageInfo.height} px • ${imageInfo.channels} Channels • Format: ${imageInfo.format}`}
          />
        </div>

        {/* Quality Metrics Grid */}
        <div className="lg:col-span-5 space-y-4">
          <div className="p-5 rounded-xl bg-slate-900 text-white flex items-center justify-between border border-slate-800 shadow-sm">
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Quality Score (Heuristic)
              </span>
              <div className="text-3xl font-bold tracking-tight text-white mt-1">
                {quality.quality_score} <span className="text-sm font-medium text-slate-400">/ 100</span>
              </div>
            </div>
            <div className="w-12 h-12 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-6 h-6" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <MetricBadge
              label="Resolution"
              value={`${imageInfo.width}×${imageInfo.height}`}
              subtext={`${(imageInfo.width * imageInfo.height / 1e6).toFixed(2)} Megapixels`}
              icon={<Eye className="w-4 h-4" />}
            />
            <MetricBadge
              label="Channels"
              value={imageInfo.channels}
              subtext={imageInfo.channels === 3 ? 'Color RGB / BGR' : 'Grayscale'}
            />
            <MetricBadge
              label="Blur Variance"
              value={quality.blur_score}
              subtext="Laplacian Variance"
              icon={<Activity className="w-4 h-4" />}
              variant={quality.blur_score < 100 ? 'amber' : 'neutral'}
            />
            <MetricBadge
              label="Contrast (Std)"
              value={quality.contrast_score}
              subtext="Intensity Standard Dev"
              variant={quality.contrast_score < 20 ? 'amber' : 'neutral'}
            />
          </div>

          {/* Warnings list */}
          {quality.warnings && quality.warnings.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
              <div className="font-semibold flex items-center gap-1.5 text-amber-800">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Quality Assessment Warnings</span>
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-amber-800 font-medium pl-1">
                {quality.warnings.map((warn, i) => (
                  <li key={i}>{warn}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};
