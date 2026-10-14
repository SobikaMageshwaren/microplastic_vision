import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiService } from '../services/api';
import {
  EvaluationResponse,
  AggregateEvaluationResponse,
  AblationExperimentResponse,
} from '../types/api';
import { Card } from '../components/common/Card';
import { MetricBadge } from '../components/common/MetricBadge';
import { ScientificImageViewer } from '../components/image-viewer/ScientificImageViewer';
import {
  Activity,
  UploadCloud,
  FileCheck,
  Layers,
  Play,
  CheckCircle2,
  AlertCircle,
  FlaskConical,
  BarChart3,
  ListFilter,
  Eye,
} from 'lucide-react';

export const Evaluation: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'aggregate' | 'ablation'>('single');

  // Single Evaluation state
  const [predFile, setPredFile] = useState<File | null>(null);
  const [gtFile, setGtFile] = useState<File | null>(null);
  const [origFile, setOrigFile] = useState<File | null>(null);
  const [predPreview, setPredPreview] = useState<string | null>(null);
  const [gtPreview, setGtPreview] = useState<string | null>(null);

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [singleResult, setSingleResult] = useState<EvaluationResponse | null>(null);

  // Aggregate Evaluation state
  const [aggregateData, setAggregateData] = useState<AggregateEvaluationResponse | null>(null);

  // Ablation Experiment state
  const [ablationData, setAblationData] = useState<AblationExperimentResponse | null>(null);
  const [ablationLoading, setAblationLoading] = useState<boolean>(false);

  useEffect(() => {
    if (activeTab === 'aggregate') {
      apiService.getAggregateEvaluations().then(setAggregateData).catch(() => {});
    }
  }, [activeTab]);

  const handleRunEvaluation = async () => {
    if (!predFile || !gtFile) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.evaluateMasks(predFile, gtFile, origFile);
      setSingleResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Evaluation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunAblation = async () => {
    setAblationLoading(true);
    setError(null);
    try {
      const res = await apiService.runAblationExperiment(null, null, true);
      setAblationData(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Ablation study failed.');
    } finally {
      setAblationLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="border-b border-slate-200 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold mb-2">
            <Activity className="w-3.5 h-3.5" />
            <span>Model Evaluation & Ablation Suite</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Scientific Model Evaluation Workstation
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Pixel-level error analysis, ground-truth metrics, aggregate statistics, and real 4-configuration pipeline ablation studies.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold shrink-0">
          <button
            onClick={() => setActiveTab('single')}
            className={`px-3.5 py-2 rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'single' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Eye className="w-3.5 h-3.5" /> Error Analysis
          </button>
          <button
            onClick={() => setActiveTab('aggregate')}
            className={`px-3.5 py-2 rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'aggregate' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" /> Aggregate Stats
          </button>
          <button
            onClick={() => setActiveTab('ablation')}
            className={`px-3.5 py-2 rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'ablation' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5" /> Ablation Study
          </button>
        </div>
      </div>

      {/* TAB 1: SINGLE IMAGE ERROR ANALYSIS */}
      {activeTab === 'single' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-4">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-600" />
                <span>1. Predicted Binary Mask</span>
              </h3>
              {!predFile ? (
                <label className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center cursor-pointer hover:border-indigo-500 hover:bg-slate-50 block transition-all">
                  <input
                    type="file"
                    className="hidden"
                    accept=".png,.jpg,.jpeg,.tiff,.tif"
                    onChange={(e) => e.target.files?.[0] && (setPredFile(e.target.files[0]), setPredPreview(URL.createObjectURL(e.target.files[0])))}
                  />
                  <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <span className="text-xs font-semibold text-slate-700 block">Select Predicted Mask</span>
                </label>
              ) : (
                <div className="p-3 bg-slate-900 rounded-xl text-center space-y-2">
                  {predPreview && <img src={predPreview} alt="Pred Preview" className="h-32 mx-auto object-contain rounded border border-slate-800" />}
                  <div className="text-xs font-mono text-slate-300 truncate">{predFile.name}</div>
                  <button onClick={() => { setPredFile(null); setPredPreview(null); }} className="text-[11px] text-rose-400 hover:underline">
                    Change File
                  </button>
                </div>
              )}
            </div>

            <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-2xs space-y-4">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>2. Ground-Truth Reference Mask</span>
              </h3>
              {!gtFile ? (
                <label className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center cursor-pointer hover:border-emerald-500 hover:bg-slate-50 block transition-all">
                  <input
                    type="file"
                    className="hidden"
                    accept=".png,.jpg,.jpeg,.tiff,.tif"
                    onChange={(e) => e.target.files?.[0] && (setGtFile(e.target.files[0]), setGtPreview(URL.createObjectURL(e.target.files[0])))}
                  />
                  <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <span className="text-xs font-semibold text-slate-700 block">Select Ground-Truth Mask</span>
                </label>
              ) : (
                <div className="p-3 bg-slate-900 rounded-xl text-center space-y-2">
                  {gtPreview && <img src={gtPreview} alt="GT Preview" className="h-32 mx-auto object-contain rounded border border-slate-800" />}
                  <div className="text-xs font-mono text-slate-300 truncate">{gtFile.name}</div>
                  <button onClick={() => { setGtFile(null); setGtPreview(null); }} className="text-[11px] text-rose-400 hover:underline">
                    Change File
                  </button>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={handleRunEvaluation}
            disabled={!predFile || !gtFile || loading}
            className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Computing Evaluation & Generating Error Maps...' : 'Run Single Image Evaluation & Error Analysis'}</span>
          </button>

          {singleResult && (
            <div className="space-y-6">
              {/* Metrics Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                <MetricBadge label="IoU (Jaccard)" value={singleResult.iou} variant="indigo" />
                <MetricBadge label="Dice Coeff" value={singleResult.dice} variant="emerald" />
                <MetricBadge label="Precision" value={singleResult.precision} variant="neutral" />
                <MetricBadge label="Recall" value={singleResult.recall} variant="neutral" />
                <MetricBadge label="F1 Score" value={singleResult.f1} variant="purple" />
              </div>

              {/* Error Visualizations */}
              <Card title="Visual Error Analysis & Boundary Overlay" subtitle="TP=Green (Correct), FP=Red (Over-segmentation), FN=Blue (Missed)">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {singleResult.error_map_path && (
                    <ScientificImageViewer
                      src={singleResult.error_map_path}
                      alt="Pixel Error Confusion Map"
                      title="Pixel Error Map (TP=Green, FP=Red, FN=Blue)"
                      caption="Green: True Positive • Red: False Positive (Over-segmented) • Blue: False Negative (Missed)"
                    />
                  )}
                  {singleResult.overlay_path && (
                    <ScientificImageViewer
                      src={singleResult.overlay_path}
                      alt="Boundary Contours Overlay"
                      title="Boundary Overlay (Cyan=GT, Magenta=Pred)"
                      caption="Cyan contours: Ground Truth • Magenta contours: Model Prediction"
                    />
                  )}
                </div>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: AGGREGATE EVALUATION */}
      {activeTab === 'aggregate' && (
        <div className="space-y-6">
          {aggregateData ? (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                <MetricBadge label="Mean IoU" value={aggregateData.mean_iou} subtext={`Std: ±${aggregateData.std_iou}`} variant="indigo" />
                <MetricBadge label="Mean Dice" value={aggregateData.mean_dice} subtext={`Std: ±${aggregateData.std_dice}`} variant="emerald" />
                <MetricBadge label="Mean Precision" value={aggregateData.mean_precision} subtext={`Std: ±${aggregateData.std_precision}`} variant="neutral" />
                <MetricBadge label="Mean Recall" value={aggregateData.mean_recall} subtext={`Std: ±${aggregateData.std_recall}`} variant="neutral" />
                <MetricBadge label="Mean F1" value={aggregateData.mean_f1} subtext={`Std: ±${aggregateData.std_f1}`} variant="purple" />
              </div>

              <Card title={`Evaluated Dataset Images (${aggregateData.evaluated_images_count})`} subtitle="Per-image segmentation metrics breakdown">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-700 font-semibold">
                        <th className="py-2.5 px-3">Image</th>
                        <th className="py-2.5 px-3">IoU</th>
                        <th className="py-2.5 px-3">Dice</th>
                        <th className="py-2.5 px-3">Precision</th>
                        <th className="py-2.5 px-3">Recall</th>
                        <th className="py-2.5 px-3">F1 Score</th>
                        <th className="py-2.5 px-3">Pred Count</th>
                        <th className="py-2.5 px-3">GT Count</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {aggregateData.per_image_results.map((res, i) => (
                        <tr key={i} className="hover:bg-slate-50">
                          <td className="py-2 px-3 font-semibold text-slate-800">{res.image_name}</td>
                          <td className="py-2 px-3 font-mono font-bold text-indigo-600">{res.iou}</td>
                          <td className="py-2 px-3 font-mono text-emerald-600">{res.dice}</td>
                          <td className="py-2 px-3 font-mono">{res.precision}</td>
                          <td className="py-2 px-3 font-mono">{res.recall}</td>
                          <td className="py-2 px-3 font-mono font-bold">{res.f1}</td>
                          <td className="py-2 px-3">{res.predicted_particle_count ?? 'N/A'}</td>
                          <td className="py-2 px-3">{res.ground_truth_particle_count ?? 'N/A'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          ) : (
            <div className="p-12 text-center text-slate-400 bg-white rounded-xl border border-slate-200">
              No aggregate evaluations stored yet. Run an evaluation to generate results.
            </div>
          )}
        </div>
      )}

      {/* TAB 3: REAL ABLATION STUDY WORKSTATION */}
      {activeTab === 'ablation' && (
        <div className="space-y-6">
          <Card title="Pipeline Stage Ablation Experiment" subtitle="Runs 4 actual CV pipeline configurations against ground-truth mask to measure stage performance">
            <div className="space-y-4">
              <p className="text-xs text-slate-600">
                Measures incremental performance gains across: <strong>Baseline Otsu</strong> → <strong>+ Preprocessing</strong> → <strong>+ Morphology</strong> → <strong>+ Watershed Instance Split</strong>.
              </p>
              <button
                onClick={handleRunAblation}
                disabled={ablationLoading}
                className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md transition-all flex items-center gap-2 disabled:opacity-50"
              >
                <FlaskConical className="w-4 h-4" />
                <span>{ablationLoading ? 'Executing 4 Ablation Pipeline Runs...' : 'Run Ablation Study (Dataset Sample RR1)'}</span>
              </button>
            </div>
          </Card>

          {ablationData && (
            <div className="space-y-6">
              {/* Results Table */}
              <Card title={`Ablation Results: ${ablationData.experiment_id}`} subtitle={`Evaluated on ${ablationData.evaluated_image_name} under Hash: ${ablationData.configuration_hash.substring(0, 16)}...`}>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-700 font-semibold">
                        <th className="py-3 px-4">Pipeline Configuration</th>
                        <th className="py-3 px-4">IoU (Jaccard)</th>
                        <th className="py-3 px-4">Dice Coeff</th>
                        <th className="py-3 px-4">Precision</th>
                        <th className="py-3 px-4">Recall</th>
                        <th className="py-3 px-4">F1 Score</th>
                        <th className="py-3 px-4">Particle Count</th>
                        <th className="py-3 px-4">Time (ms)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono">
                      {ablationData.results_table.map((row, i) => (
                        <tr key={i} className={i === ablationData.results_table.length - 1 ? 'bg-indigo-50/50 font-bold' : ''}>
                          <td className="py-3 px-4 font-sans font-semibold text-slate-900">{row.config_name}</td>
                          <td className="py-3 px-4 text-indigo-600">{row.iou.toFixed(4)}</td>
                          <td className="py-3 px-4 text-emerald-600">{row.dice.toFixed(4)}</td>
                          <td className="py-3 px-4">{row.precision.toFixed(4)}</td>
                          <td className="py-3 px-4">{row.recall.toFixed(4)}</td>
                          <td className="py-3 px-4 font-bold">{row.f1.toFixed(4)}</td>
                          <td className="py-3 px-4">{row.particle_count ?? 'N/A'}</td>
                          <td className="py-3 px-4 text-slate-500">{row.processing_time_ms.toFixed(1)} ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Recharts Bar Chart Comparison */}
              <Card title="Ablation Metric Comparison Chart" subtitle="Visualizing metric trajectory across pipeline configurations">
                <div className="h-72 w-full pt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={ablationData.results_table} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="config_name" tick={{ fontSize: 11, fill: '#64748b' }} />
                      <YAxis domain={[0, 1]} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                      <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                      <Bar dataKey="iou" name="IoU" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="dice" name="Dice" fill="#059669" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="precision" name="Precision" fill="#d97706" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="recall" name="Recall" fill="#2563eb" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
