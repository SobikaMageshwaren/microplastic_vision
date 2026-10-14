import React from 'react';

interface MetricBadgeProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  icon?: React.ReactNode;
  variant?: 'neutral' | 'indigo' | 'emerald' | 'amber' | 'purple';
}

export const MetricBadge: React.FC<MetricBadgeProps> = ({
  label,
  value,
  unit,
  subtext,
  icon,
  variant = 'neutral',
}) => {
  const variantStyles = {
    neutral: 'bg-slate-50 border-slate-200 text-slate-900',
    indigo: 'bg-indigo-50/60 border-indigo-200 text-indigo-900',
    emerald: 'bg-emerald-50/60 border-emerald-200 text-emerald-900',
    amber: 'bg-amber-50/60 border-amber-200 text-amber-900',
    purple: 'bg-purple-50/60 border-purple-200 text-purple-900',
  };

  return (
    <div className={`p-4 rounded-xl border ${variantStyles[variant]} transition-all`}>
      <div className="flex items-center justify-between gap-2 mb-1">
        <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</span>
        {icon && <span className="text-slate-400">{icon}</span>}
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold tracking-tight">{value}</span>
        {unit && <span className="text-xs font-semibold text-slate-500">{unit}</span>}
      </div>
      {subtext && <p className="text-xs text-slate-500 mt-1">{subtext}</p>}
    </div>
  );
};
