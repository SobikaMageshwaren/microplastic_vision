import React, { useState } from 'react';
import { Layers, SlidersHorizontal, ArrowLeftRight } from 'lucide-react';
import { Card } from '../common/Card';
import { ScientificImageViewer } from '../image-viewer/ScientificImageViewer';
import { ImageComparisonSlider } from '../common/ImageComparisonSlider';
import { getImageUrl } from '../../utils/image';

interface PreprocessingGridProps {
  artifacts: Record<string, string>;
}

export const PreprocessingGrid: React.FC<PreprocessingGridProps> = ({ artifacts }) => {
  const prepSteps = [
    {
      key: 'original',
      label: '1. Raw Image',
      subtext: 'Unfiltered input microscopy grayscale',
      badge: 'Input',
    },
    {
      key: 'denoised',
      label: '2. Denoised (FastNLMeans)',
      subtext: 'Suppresses sensor noise grain (h=10)',
      badge: 'Filtering',
    },
    {
      key: 'background_corrected',
      label: '3. Background Flattened (Top-Hat)',
      subtext: 'Removes uneven lighting & vignetting (31px ellipse)',
      badge: 'Correction',
    },
    {
      key: 'normalized',
      label: '4. Min-Max Normalized',
      subtext: 'Linear dynamic range stretch across full [0, 255] spectrum',
      badge: 'Linear Stretch',
    },
    {
      key: 'contrast_enhanced',
      label: '5. Contrast Boosted (CLAHE)',
      subtext: 'Local adaptive tile equalization (Clip=4.0, Grid=8x8) bringing out particle edge micro-contrast',
      badge: 'Adaptive Equalization',
    },
  ].filter((step) => artifacts[step.key]);

  const [activeStep, setActiveStep] = useState<string>(prepSteps[0]?.key || 'original');
  const [showSliderComparison, setShowSliderComparison] = useState<boolean>(false);

  const activeStepMeta = prepSteps.find((s) => s.key === activeStep) || prepSteps[0];

  const hasNormAndClahe = Boolean(artifacts['normalized'] && artifacts['contrast_enhanced']);

  return (
    <Card
      title="Multi-Stage Image Preprocessing"
      subtitle="Preserved intermediate outputs: Denoising, Morphological Top-Hat Illumination Flattening, Linear Normalization, and Adaptive CLAHE"
      action={
        hasNormAndClahe && (
          <button
            onClick={() => setShowSliderComparison(!showSliderComparison)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition-colors"
          >
            <ArrowLeftRight className="w-3.5 h-3.5" />
            <span>{showSliderComparison ? 'View Stage Gallery' : 'Compare Normalization vs. CLAHE'}</span>
          </button>
        )
      }
    >
      <div className="space-y-6">
        {showSliderComparison && hasNormAndClahe ? (
          <div className="space-y-3">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <strong className="text-slate-900 block font-bold">Interactive Dynamic Slider: Normalization vs. CLAHE</strong>
                <span className="text-slate-500 text-[11px]">
                  Slide left/right to observe how CLAHE accentuates edge boundaries and faint particle textures over linear Min-Max stretch.
                </span>
              </div>
              <div className="flex items-center gap-2 text-[11px] font-mono shrink-0">
                <span className="text-slate-600 font-bold">Left: Normalized</span>
                <span>•</span>
                <span className="text-emerald-700 font-bold">Right: CLAHE</span>
              </div>
            </div>
            <ImageComparisonSlider
              beforeImage={artifacts['normalized']}
              afterImage={artifacts['contrast_enhanced']}
              beforeLabel="4. Min-Max Normalized (Linear)"
              afterLabel="5. CLAHE Enhanced (Adaptive)"
            />
          </div>
        ) : (
          <>
            {/* Step Selector Pills */}
            <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-4">
              {prepSteps.map((step) => (
                <button
                  key={step.key}
                  onClick={() => setActiveStep(step.key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                    activeStep === step.key
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>{step.label}</span>
                </button>
              ))}
            </div>

            {/* Selected Preprocessing Stage Image Viewer */}
            {artifacts[activeStep] && (
              <div className="max-w-4xl mx-auto space-y-2">
                <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-800">{activeStepMeta?.label}</span>
                  <span className="text-slate-500 text-[11px]">{activeStepMeta?.subtext}</span>
                </div>
                <ScientificImageViewer
                  src={artifacts[activeStep]}
                  alt={activeStepMeta?.label || activeStep}
                  title={activeStepMeta?.label || activeStep}
                  caption={activeStepMeta?.subtext}
                />
              </div>
            )}

            {/* Thumbnail Comparison Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 pt-2">
              {prepSteps.map((step) => (
                <div
                  key={step.key}
                  onClick={() => {
                    setActiveStep(step.key);
                    setShowSliderComparison(false);
                  }}
                  className={`cursor-pointer rounded-xl overflow-hidden border p-1.5 bg-slate-900 transition-all ${
                    activeStep === step.key
                      ? 'ring-2 ring-indigo-500 border-transparent scale-[1.02]'
                      : 'border-slate-800 opacity-80 hover:opacity-100 hover:border-slate-700'
                  }`}
                >
                  <div className="h-24 bg-slate-950 flex items-center justify-center overflow-hidden rounded-lg">
                    <img
                      src={getImageUrl(artifacts[step.key])}
                      alt={step.label}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="mt-1 px-1">
                    <p className="text-[10px] font-bold text-slate-200 truncate">{step.label}</p>
                    <span className="text-[9px] font-mono text-indigo-400 block truncate">{step.badge}</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </Card>
  );
};
