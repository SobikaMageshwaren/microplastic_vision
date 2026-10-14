import React from 'react';
import { Check } from 'lucide-react';

interface Stage {
  id: string;
  label: string;
}

const STAGES: Stage[] = [
  { id: 'upload', label: 'Upload' },
  { id: 'quality', label: 'Quality' },
  { id: 'preprocess', label: 'Preprocess' },
  { id: 'segment', label: 'Segmentation' },
  { id: 'instances', label: 'Instances' },
  { id: 'features', label: 'Features' },
  { id: 'morphology', label: 'Morphology' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'report', label: 'Report' },
];

interface PipelineTrackerProps {
  currentStage?: string;
  completed?: boolean;
}

export const PipelineTracker: React.FC<PipelineTrackerProps> = ({
  currentStage = 'report',
  completed = true,
}) => {
  const activeIndex = STAGES.findIndex((s) => s.id === currentStage);
  const currentIndex = activeIndex === -1 ? STAGES.length - 1 : activeIndex;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm mb-6 no-print">
      <div className="flex items-center justify-between overflow-x-auto gap-2 pb-2 sm:pb-0 scrollbar-none">
        {STAGES.map((stage, idx) => {
          const isDone = completed || idx < currentIndex;
          const isCurrent = !completed && idx === currentIndex;

          return (
            <div key={stage.id} className="flex items-center gap-2 min-w-max">
              <div className="flex items-center gap-2">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-all ${
                    isDone
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : isCurrent
                      ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-600 animate-pulse'
                      : 'bg-slate-100 text-slate-400 border border-slate-200'
                  }`}
                >
                  {isDone ? <Check className="w-4 h-4" /> : idx + 1}
                </div>
                <span
                  className={`text-xs font-medium ${
                    isDone || isCurrent ? 'text-slate-800' : 'text-slate-400'
                  }`}
                >
                  {stage.label}
                </span>
              </div>
              {idx < STAGES.length - 1 && (
                <div
                  className={`h-0.5 w-6 sm:w-10 rounded-full transition-colors ${
                    idx < currentIndex || completed ? 'bg-indigo-500' : 'bg-slate-200'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
