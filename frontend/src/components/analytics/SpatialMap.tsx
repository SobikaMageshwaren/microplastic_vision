import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ParticleFeatures } from '../../types/particle';
import { SampleAnalytics } from '../../types/analysis';
import { Card } from '../common/Card';
import { MetricBadge } from '../common/MetricBadge';

interface SpatialMapProps {
  particles: ParticleFeatures[];
  analytics: SampleAnalytics;
  imageWidth: number;
  imageHeight: number;
}

export const SpatialMap: React.FC<SpatialMapProps> = ({
  particles,
  analytics,
  imageWidth,
  imageHeight,
}) => {
  const scatterData = React.useMemo(() => {
    return particles.map((p) => ({
      x: p.centroid.x,
      y: p.centroid.y,
      id: p.particle_id,
      area: p.area,
    }));
  }, [particles]);

  const quadrants = analytics.spatial_distribution.quadrant_counts;

  return (
    <Card
      title="Particle Spatial Distribution & Centroid Map"
      subtitle={`Centroid coordinate map (0..${imageWidth}x0..${imageHeight} px) colored by particle size`}
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Scatter Chart */}
        <div className="lg:col-span-8 h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                type="number"
                dataKey="x"
                name="X Coordinate"
                unit="px"
                domain={[0, imageWidth]}
                tick={{ fontSize: 11, fill: '#64748b' }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Y Coordinate"
                unit="px"
                domain={[0, imageHeight]}
                reversed={true} // Invert Y axis for image coordinates
                tick={{ fontSize: 11, fill: '#64748b' }}
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ payload }) => {
                  if (payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-slate-900 text-white p-2.5 rounded-lg text-xs shadow-md border border-slate-800">
                        <p className="font-bold text-indigo-400 font-mono">{data.id}</p>
                        <p>Centroid: ({data.x}, {data.y}) px</p>
                        <p>Area: {data.area} px²</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter name="Particles" data={scatterData} fill="#6366f1" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Quadrant Counts */}
        <div className="lg:col-span-4 space-y-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
            Quadrant Particle Counts
          </span>
          <div className="grid grid-cols-2 gap-3">
            <MetricBadge label="Top-Left" value={quadrants.top_left} subtext="Q1" />
            <MetricBadge label="Top-Right" value={quadrants.top_right} subtext="Q2" />
            <MetricBadge label="Bottom-Left" value={quadrants.bottom_left} subtext="Q3" />
            <MetricBadge label="Bottom-Right" value={quadrants.bottom_right} subtext="Q4" />
          </div>
        </div>
      </div>
    </Card>
  );
};
