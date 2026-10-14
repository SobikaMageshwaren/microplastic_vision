import React, { useState } from 'react';
import { Card } from '../common/Card';
import { ScientificImageViewer } from '../image-viewer/ScientificImageViewer';
import { ImageComparisonSlider } from '../common/ImageComparisonSlider';
import { Layers, ArrowLeftRight, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react';
import { getImageUrl } from '../../utils/image';

interface SegmentationSectionProps {
  artifacts: Record<string, string>;
  thresholdMethod?: string;
}

export const SegmentationSection: React.FC<SegmentationSectionProps> = ({
  artifacts,
  thresholdMethod = 'otsu',
}) => {
  const [viewMode, setViewMode] = useState<'cards' | 'slider' | 'delta'>('cards');

  const hasBothMasks = Boolean(artifacts['threshold_mask'] && artifacts['cleaned_mask']);
  const hasDelta = Boolean(artifacts['morphology_delta']);

  return (
    <Card
      title="Classical Computer Vision Binary Segmentation & Morphological Cleaning"
      subtitle={`Raw binary thresholding (${thresholdMethod.toUpperCase()}) vs. Morphological opening (noise suppression) and closing (void sealing)`}
      action={
        <div className="flex items-center gap-2">
          {hasBothMasks && (
            <div className="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-xs">
              <button
                onClick={() => setViewMode('cards')}
                className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                  viewMode === 'cards' ? 'bg-white text-indigo-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Gallery View
              </button>
              <button
                onClick={() => setViewMode('slider')}
                className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                  viewMode === 'slider' ? 'bg-white text-indigo-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Before / After Slider
              </button>
              {hasDelta && (
                <button
                  onClick={() => setViewMode('delta')}
                  className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                    viewMode === 'delta' ? 'bg-white text-indigo-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Morphology Delta Map
                </button>
              )}
            </div>
          )}
          <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-indigo-100 text-indigo-800 uppercase border border-indigo-200">
            Method: {thresholdMethod}
          </span>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Interactive Comparison Slider View */}
        {viewMode === 'slider' && hasBothMasks && (
          <div className="space-y-3">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <strong className="text-slate-900 block font-bold">Interactive Slider: Raw Threshold vs. Cleaned Binary Mask</strong>
                <span className="text-slate-500 text-[11px]">
                  Drag the slider handle to inspect how mathematical morphology purges spurious boundary noise and bridges voids.
                </span>
              </div>
              <div className="flex items-center gap-2 text-[11px] font-mono shrink-0">
                <span className="text-amber-700 font-bold">Left: 1. Raw Threshold</span>
                <span>•</span>
                <span className="text-emerald-700 font-bold">Right: 2. Morphologically Cleaned</span>
              </div>
            </div>
            <ImageComparisonSlider
              beforeImage={artifacts['threshold_mask']}
              afterImage={artifacts['cleaned_mask']}
              beforeLabel="1. Raw Threshold (Unfiltered Noise)"
              afterLabel="2. Cleaned Mask (Opening + Closing)"
            />
          </div>
        )}

        {/* Morphological Delta Map View */}
        {viewMode === 'delta' && hasDelta && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-900 text-slate-200 border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="font-bold text-white block text-sm flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  Morphological Impact Color Legend
                </span>
                <span className="text-slate-400 text-[11px]">
                  Pixel-level difference map highlighting changes introduced by mathematical morphology.
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-xs font-semibold">
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-red-500"></span>
                  <span>Red: Noise Spikes Removed (Opening)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                  <span>Green: Pinhole Voids Sealed (Closing)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-slate-300"></span>
                  <span>Light Gray: Preserved Particle Body</span>
                </div>
              </div>
            </div>

            <div className="max-w-4xl mx-auto">
              <ScientificImageViewer
                src={artifacts['morphology_delta']}
                alt="Morphological Cleaning Delta Map"
                title="Morphological Impact Delta Map"
                caption="Red: Noise particles eliminated by 4x4 Opening • Green: Internal voids filled by 6x6 Closing • Gray: Stable particle bodies"
              />
            </div>
          </div>
        )}

        {/* Gallery / Side-by-Side Cards View */}
        {viewMode === 'cards' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {artifacts['threshold_mask'] && (
              <div className="space-y-2">
                <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-between text-xs">
                  <span className="font-bold text-amber-900 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> 1. Raw Threshold Mask
                  </span>
                  <span className="text-[10px] font-mono text-amber-700 bg-amber-100 px-2 py-0.5 rounded">Unfiltered</span>
                </div>
                <ScientificImageViewer
                  src={artifacts['threshold_mask']}
                  alt="Raw Threshold Mask"
                  title="1. Raw Binary Threshold Mask"
                  caption="Direct global threshold output exhibiting fine sensor speckles, boundary spurs, and pinhole voids."
                />
              </div>
            )}

            {artifacts['cleaned_mask'] && (
              <div className="space-y-2">
                <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-between text-xs">
                  <span className="font-bold text-emerald-900 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> 2. Morphologically Cleaned Mask
                  </span>
                  <span className="text-[10px] font-mono text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">Cleaned</span>
                </div>
                <ScientificImageViewer
                  src={artifacts['cleaned_mask']}
                  alt="Morphologically Cleaned Mask"
                  title="2. Cleaned Binary Mask"
                  caption="Final cleaned binary mask after 4x4 Opening (noise suppression) and 6x6 Closing (void sealing)."
                />
              </div>
            )}

            {artifacts['morphology_delta'] && (
              <div className="space-y-2 md:col-span-2 lg:col-span-1">
                <div className="p-2.5 rounded-lg bg-purple-50 border border-purple-200 flex items-center justify-between text-xs">
                  <span className="font-bold text-purple-900 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-purple-600" /> 3. Morphological Delta Map
                  </span>
                  <span className="text-[10px] font-mono text-purple-700 bg-purple-100 px-2 py-0.5 rounded">Difference</span>
                </div>
                <ScientificImageViewer
                  src={artifacts['morphology_delta']}
                  alt="Morphological Cleaning Delta Map"
                  title="3. Morphological Delta (Difference)"
                  caption="Color-coded delta: Red = removed noise specs, Green = filled holes, Gray = stable particles."
                />
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
