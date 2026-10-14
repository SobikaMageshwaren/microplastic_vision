import React, { useState } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ParticleFeatures } from '../../types/particle';
import { Card } from '../common/Card';
import { Sliders } from 'lucide-react';

interface ScatterExplorerProps {
  particles: ParticleFeatures[];
  selectedParticleId?: string | null;
  onSelectParticle?: (particleId: string) => void;
}

type FeatureKey = 'area' | 'circularity' | 'aspect_ratio' | 'solidity' | 'eccentricity' | 'perimeter';

const FEATURE_LABELS: Record<FeatureKey, string> = {
  area: 'Area (px²)',
  circularity: 'Circularity (0 - 1)',
  aspect_ratio: 'Aspect Ratio (W / H)',
  solidity: 'Solidity (Area / Convex Hull)',
  eccentricity: 'Eccentricity (0 - 1)',
  perimeter: 'Perimeter (px)',
};

export const ScatterExplorer: React.FC<ScatterExplorerProps> = ({
  particles = [],
  selectedParticleId,
  onSelectParticle,
}) => {
  const [xAxisKey, setXAxisKey] = useState<FeatureKey>('area');
  const [yAxisKey, setYAxisKey] = useState<FeatureKey>('circularity');

  const scatterData = particles.map((p) => ({
    particle_id: p.particle_id,
    x: p[xAxisKey] ?? 0,
    y: p[yAxisKey] ?? 0,
    area: p.area,
    circularity: p.circularity,
  }));

  const handleScatterClick = (entry: any) => {
    if (entry && entry.particle_id && onSelectParticle) {
      onSelectParticle(entry.particle_id);
    }
  };

  return (
    <Card
      title="Particle Morphometrics Scatter Plot Explorer"
      subtitle="Interactive multi-dimensional particle feature distribution analysis"
    >
      <div className="space-y-4">
        {/* Axis Control Selectors */}
        <div className="flex flex-wrap items-center gap-4 bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-600" />
            <span className="font-bold text-slate-700">X-Axis Feature:</span>
            <select
              value={xAxisKey}
              onChange={(e) => setXAxisKey(e.target.value as FeatureKey)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-900 font-semibold focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            >
              {Object.entries(FEATURE_LABELS).map(([k, label]) => (
                <option key={k} value={k}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-700">Y-Axis Feature:</span>
            <select
              value={yAxisKey}
              onChange={(e) => setYAxisKey(e.target.value as FeatureKey)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-900 font-semibold focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            >
              {Object.entries(FEATURE_LABELS).map(([k, label]) => (
                <option key={k} value={k}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Scatter Chart */}
        <div className="h-[360px] w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                type="number"
                dataKey="x"
                name={FEATURE_LABELS[xAxisKey]}
                unit=""
                tick={{ fontSize: 11, fill: '#64748b' }}
                label={{ value: FEATURE_LABELS[xAxisKey], position: 'insideBottom', offset: -10, fontSize: 11 }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name={FEATURE_LABELS[yAxisKey]}
                unit=""
                tick={{ fontSize: 11, fill: '#64748b' }}
                label={{ value: FEATURE_LABELS[yAxisKey], angle: -90, position: 'insideLeft', fontSize: 11 }}
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="p-2.5 bg-slate-900 text-white rounded-xl shadow-xl text-xs font-mono border border-slate-800">
                        <p className="font-extrabold text-amber-400 mb-1">{data.particle_id}</p>
                        <p>{FEATURE_LABELS[xAxisKey]}: {data.x}</p>
                        <p>{FEATURE_LABELS[yAxisKey]}: {data.y}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter name="Particles" data={scatterData} onClick={handleScatterClick}>
                {scatterData.map((entry, index) => {
                  const isSelected = entry.particle_id === selectedParticleId;
                  return (
                    <Cell
                      key={`cell-${index}`}
                      fill={isSelected ? '#f59e0b' : '#6366f1'}
                      r={isSelected ? 7 : 4}
                      stroke={isSelected ? '#b45309' : '#4338ca'}
                      strokeWidth={isSelected ? 2 : 1}
                      className="cursor-pointer transition-all hover:scale-125"
                    />
                  );
                })}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  );
};
