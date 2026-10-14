import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { apiService } from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { GitCompare, Layers, Cpu, Clock, CheckCircle2, RefreshCw } from 'lucide-react';
import { getImageUrl } from '../../utils/image';

export const ModelComparisonSection: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [comparisonData, setComparisonData] = useState<any>(null);

  const loadComparison = () => {
    setLoading(true);
    apiService
      .getModelComparison()
      .then((data) => {
        setComparisonData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load comparison data:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadComparison();
  }, []);

  if (loading) {
    return (
      <Card title="Classical CV vs PyTorch U-Net Model Comparison">
        <div className="py-12 text-center text-xs text-slate-500 flex flex-col items-center justify-center gap-2">
          <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading Classical CV and U-Net Model Comparison...</span>
        </div>
      </Card>
    );
  }

  if (!comparisonData || !comparisonData.metrics_comparison) {
    return (
      <Card title="Classical CV vs PyTorch U-Net Model Comparison">
        <div className="py-8 text-center text-xs text-slate-400">
          No comparison data available. Click below to reload.
          <div className="mt-3">
            <button
              onClick={loadComparison}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Reload Comparison
            </button>
          </div>
        </div>
      </Card>
    );
  }

  const chartData = [
    {
      metric: 'IoU',
      'Classical CV': comparisonData.metrics_comparison[0].iou,
      'U-Net DL': comparisonData.metrics_comparison[1].iou,
    },
    {
      metric: 'Dice',
      'Classical CV': comparisonData.metrics_comparison[0].dice,
      'U-Net DL': comparisonData.metrics_comparison[1].dice,
    },
    {
      metric: 'Precision',
      'Classical CV': comparisonData.metrics_comparison[0].precision,
      'U-Net DL': comparisonData.metrics_comparison[1].precision,
    },
    {
      metric: 'Recall',
      'Classical CV': comparisonData.metrics_comparison[0].recall,
      'U-Net DL': comparisonData.metrics_comparison[1].recall,
    },
    {
      metric: 'F1 Score',
      'Classical CV': comparisonData.metrics_comparison[0].f1,
      'U-Net DL': comparisonData.metrics_comparison[1].f1,
    },
  ];

  return (
    <Card
      title="Classical Computer Vision vs. Deep Learning U-Net Benchmark"
      subtitle={`Side-by-side segmentation metric comparison evaluated against expert ground-truth on ${comparisonData.evaluated_image}`}
      action={
        <div className="flex items-center gap-2">
          <button
            onClick={loadComparison}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
            title="Refresh comparison"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-purple-100 text-purple-800 border border-purple-200">
            Image: {comparisonData.evaluated_image}
          </span>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Metric Comparison Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-700 font-semibold">
                <th className="p-3">Architecture / Method</th>
                <th className="p-3">IoU</th>
                <th className="p-3">Dice</th>
                <th className="p-3">Precision</th>
                <th className="p-3">Recall</th>
                <th className="p-3">F1 Score</th>
                <th className="p-3 text-right">Particles</th>
                <th className="p-3 text-right">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {comparisonData.metrics_comparison.map((row: any, idx: number) => (
                <tr key={idx} className={idx === 0 ? 'bg-indigo-50/20' : 'bg-purple-50/20'}>
                  <td className="p-3 font-bold text-slate-900 flex items-center gap-2">
                    <span
                      className={`w-2.5 h-2.5 rounded-full ${idx === 0 ? 'bg-indigo-600' : 'bg-purple-600'}`}
                    ></span>
                    <span>{row.method}</span>
                  </td>
                  <td className="p-3 font-mono font-bold text-indigo-700">{row.iou.toFixed(4)}</td>
                  <td className="p-3 font-mono font-bold text-emerald-700">{row.dice.toFixed(4)}</td>
                  <td className="p-3 font-mono text-slate-700">{row.precision.toFixed(4)}</td>
                  <td className="p-3 font-mono text-slate-700">{row.recall.toFixed(4)}</td>
                  <td className="p-3 font-mono text-slate-700">{row.f1.toFixed(4)}</td>
                  <td className="p-3 text-right text-slate-800 font-bold">{row.particle_count}</td>
                  <td className="p-3 text-right text-slate-500 font-mono">{row.processing_time_ms.toFixed(1)} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Grouped Bar Chart */}
        <div className="h-[280px] w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="metric" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Bar dataKey="Classical CV" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="U-Net DL" fill="#a855f7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 4-Quadrant Visual Mask Comparison */}
        <div className="space-y-2 pt-2">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Visual Mask Comparison (High-Resolution Sample)
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center shadow-md">
              <span className="text-[11px] font-bold text-slate-300 block mb-1.5">Original Sample</span>
              <div className="h-44 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-800">
                <img
                  src={getImageUrl(comparisonData.artifacts?.original_image)}
                  alt="Original"
                  className="max-h-full max-w-full object-contain"
                />
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center shadow-md">
              <span className="text-[11px] font-bold text-amber-400 block mb-1.5">Ground Truth Mask</span>
              <div className="h-44 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-800">
                <img
                  src={getImageUrl(comparisonData.artifacts?.ground_truth_mask)}
                  alt="GT Mask"
                  className="max-h-full max-w-full object-contain"
                />
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center shadow-md">
              <span className="text-[11px] font-bold text-indigo-400 block mb-1.5">Classical CV Mask</span>
              <div className="h-44 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-800">
                <img
                  src={getImageUrl(comparisonData.artifacts?.classical_mask)}
                  alt="Classical Mask"
                  className="max-h-full max-w-full object-contain"
                />
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center shadow-md">
              <span className="text-[11px] font-bold text-purple-400 block mb-1.5">U-Net Predicted Mask</span>
              <div className="h-44 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-800">
                <img
                  src={getImageUrl(comparisonData.artifacts?.unet_mask)}
                  alt="U-Net Mask"
                  className="max-h-full max-w-full object-contain"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
