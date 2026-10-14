import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { SampleAnalytics } from '../../types/analysis';
import { ParticleFeatures } from '../../types/particle';
import { Card } from '../common/Card';
import { MetricBadge } from '../common/MetricBadge';
import { formatNumber } from '../../utils/formatting';

interface MorphologyChartsProps {
  analytics: SampleAnalytics;
  particles: ParticleFeatures[];
}

export const MorphologyCharts: React.FC<MorphologyChartsProps> = ({ analytics, particles }) => {
  // Compute histogram data for Circularity and Aspect Ratio from real particles
  const circularityHist = React.useMemo(() => {
    const bins = [0.2, 0.4, 0.6, 0.8, 1.0];
    const counts = { '0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0, '0.6-0.8': 0, '0.8-1.0': 0 };

    particles.forEach((p) => {
      const c = p.circularity;
      if (c <= 0.2) counts['0.0-0.2']++;
      else if (c <= 0.4) counts['0.2-0.4']++;
      else if (c <= 0.6) counts['0.4-0.6']++;
      else if (c <= 0.8) counts['0.6-0.8']++;
      else counts['0.8-1.0']++;
    });

    return Object.entries(counts).map(([range, count]) => ({ range, count }));
  }, [particles]);

  const sizeDistData = React.useMemo(() => {
    return Object.entries(analytics.size_distribution || {}).map(([bin, count]) => ({
      bin: `${bin} px²`,
      count,
    }));
  }, [analytics.size_distribution]);

  return (
    <div className="space-y-6">
      {/* Metric Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricBadge
          label="Mean Area"
          value={formatNumber(analytics.area_statistics.mean)}
          unit="px²"
          subtext={`Median: ${formatNumber(analytics.area_statistics.median)} px²`}
          variant="indigo"
        />
        <MetricBadge
          label="Mean Circularity"
          value={analytics.shape_statistics.circularity.mean}
          subtext={`Std: ${analytics.shape_statistics.circularity.std}`}
          variant="emerald"
        />
        <MetricBadge
          label="Mean Aspect Ratio"
          value={analytics.shape_statistics.aspect_ratio.mean}
          subtext={`Std: ${analytics.shape_statistics.aspect_ratio.std}`}
          variant="neutral"
        />
        <MetricBadge
          label="Mean Solidity"
          value={analytics.shape_statistics.solidity.mean}
          subtext={`Std: ${analytics.shape_statistics.solidity.std}`}
          variant="purple"
        />
      </div>

      {/* Recharts Histograms */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Particle Size Distribution" subtitle="Histogram of particle area bins in square pixels">
          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sizeDistData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="bin" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Particle Circularity Distribution" subtitle="Distribution of circularity values (4πA / P²)">
          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={circularityHist} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="range" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#059669" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};
