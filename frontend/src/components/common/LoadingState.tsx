import React from 'react';
import { Loader2, CheckCircle, Circle } from 'lucide-react';

interface StageProgress {
  name: string;
  status: 'done' | 'active' | 'pending';
}

interface LoadingStateProps {
  message?: string;
  stages?: StageProgress[];
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Running Computer-Vision Analysis Pipeline...',
  stages,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-white rounded-2xl border border-slate-200 shadow-sm max-w-lg mx-auto text-center my-12">
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      </div>

      <h3 className="text-lg font-bold text-slate-900 mb-2">{message}</h3>
      <p className="text-xs text-slate-500 mb-6 max-w-xs">
        Executing image quality checks, multi-stage preprocessing, thresholding, and watershed instance separation...
      </p>

      {stages && stages.length > 0 && (
        <div className="w-full bg-slate-50 rounded-xl p-4 border border-slate-100 text-left space-y-2.5">
          {stages.map((st, i) => (
            <div key={i} className="flex items-center gap-3 text-xs">
              {st.status === 'done' && <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />}
              {st.status === 'active' && <Loader2 className="w-4 h-4 text-indigo-600 animate-spin shrink-0" />}
              {st.status === 'pending' && <Circle className="w-4 h-4 text-slate-300 shrink-0" />}
              <span
                className={`font-medium ${
                  st.status === 'done'
                    ? 'text-slate-700'
                    : st.status === 'active'
                    ? 'text-indigo-600 font-semibold'
                    : 'text-slate-400'
                }`}
              >
                {st.name}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
