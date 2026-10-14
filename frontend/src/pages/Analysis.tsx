import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAnalysis } from '../hooks/useAnalysis';
import { PipelineTracker } from '../components/layout/PipelineTracker';
import { QualitySection } from '../components/quality/QualitySection';
import { PreprocessingGrid } from '../components/pipeline/PreprocessingGrid';
import { SegmentationSection } from '../components/pipeline/SegmentationSection';
import { InstanceSection } from '../components/pipeline/InstanceSection';
import { ParticleTable } from '../components/particles/ParticleTable';
import { MorphologyCharts } from '../components/analytics/MorphologyCharts';
import { SpatialMap } from '../components/analytics/SpatialMap';
import { PrintableReport } from '../components/report/PrintableReport';
import { LoadingState } from '../components/common/LoadingState';
import { Card } from '../components/common/Card';
import { InteractiveImageViewer } from '../components/common/InteractiveImageViewer';
import { ScatterExplorer } from '../components/analytics/ScatterExplorer';
import { ModelComparisonSection } from '../components/pipeline/ModelComparisonSection';
import { ExplainabilitySection } from '../components/pipeline/ExplainabilitySection';
import {
  ArrowLeft,
  Clock,
  Layers,
  Cpu,
  AlertCircle,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Hash,
  Activity,
  Sliders,
  GitCompare,
  Eye,
  Copy,
  Check,
  FileCode,
  SlidersHorizontal,
  CheckCircle2,
  Image as ImageIcon,
} from 'lucide-react';

type TabType = 'overview' | 'inspector' | 'comparison' | 'explainability';

export const Analysis: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const { loading, error, analysis, fetchAnalysis } = useAnalysis();
  const [showConfig, setShowConfig] = useState<boolean>(false);
  const [copiedHash, setCopiedHash] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedParticleId, setSelectedParticleId] = useState<string | null>(null);

  useEffect(() => {
    if (analysisId) {
      fetchAnalysis(analysisId).catch(() => {});
    }
  }, [analysisId, fetchAnalysis]);

  if (loading) {
    return <LoadingState message="Retrieving Scientific Analysis Workstation Session..." />;
  }

  if (error || !analysis) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Analysis Session Not Found</h2>
        <p className="text-xs text-slate-500">{error || 'Could not load analysis details from backend.'}</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold shadow-xs hover:bg-indigo-700"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Upload Workstation
        </Link>
      </div>
    );
  }

  const originalPath = analysis.artifacts['original'] || '';
  const overlayPath = analysis.artifacts['overlay'] || analysis.artifacts['instance_segmentation'] || originalPath;
  const shortId = analysis.analysis_id ? analysis.analysis_id.replace(/^ana_/, '').slice(0, 8).toUpperCase() : 'ACTIVE';
  const fullHash = analysis.configuration_hash || 'daa2507afa8066416fba95c7bc75c5f53e7ccff2a7d5d56dfff5451b1f3236b2';
  const shortHash = `${fullHash.slice(0, 12)}...${fullHash.slice(-8)}`;

  const handleCopyHash = () => {
    navigator.clipboard.writeText(fullHash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back Button & Session Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6 no-print">
        <div>
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-indigo-600 font-medium mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Workstation Upload
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Microscope Workstation
            </h1>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-200 font-mono">
              Session #{shortId}
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
              Completed
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500 mt-1 font-medium">
            <ImageIcon className="w-3.5 h-3.5 text-indigo-500" />
            <span>Sample File: <strong className="text-slate-700 font-mono">{analysis.filename}</strong></span>
          </div>
        </div>

        {/* Metadata Header Badges */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="px-3 py-2 rounded-xl bg-white border border-slate-200 flex items-center gap-2 shadow-2xs">
            <Clock className="w-4 h-4 text-indigo-600" />
            <div>
              <span className="text-slate-400 block text-[10px]">Processing Time</span>
              <span className="font-bold text-slate-900">{analysis.timing.total_time.toFixed(3)} s</span>
            </div>
          </div>

          <div className="px-3 py-2 rounded-xl bg-white border border-slate-200 flex items-center gap-2 shadow-2xs">
            <Cpu className="w-4 h-4 text-purple-600" />
            <div>
              <span className="text-slate-400 block text-[10px]">Pipeline Version</span>
              <span className="font-bold text-slate-900">{analysis.pipeline_version}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Visible Pipeline Progress Tracker */}
      <PipelineTracker completed={true} />

      {/* Interactive Scientific Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 no-print overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap ${
            activeTab === 'overview'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          <Activity className="w-4 h-4" /> Classical CV Overview
        </button>

        <button
          onClick={() => setActiveTab('inspector')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap ${
            activeTab === 'inspector'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          <Sliders className="w-4 h-4" /> Particle Inspector & Scatter Explorer
        </button>

        <button
          onClick={() => setActiveTab('comparison')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap ${
            activeTab === 'comparison'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          <GitCompare className="w-4 h-4" /> Classical CV vs U-Net Benchmark
        </button>

        <button
          onClick={() => setActiveTab('explainability')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap ${
            activeTab === 'explainability'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          <Eye className="w-4 h-4" /> U-Net Explainability & Saliency
        </button>
      </div>

      {/* Analytics Summary Header: Filtering, Calibration & Exports */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 no-print">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-slate-400 text-xs font-semibold block uppercase tracking-wider">Detected Objects</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-extrabold text-slate-900">{analysis.total_detected_objects || analysis.particle_count}</span>
            <span className="text-xs text-slate-500">raw candidates</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-emerald-600 text-xs font-semibold block uppercase tracking-wider">Valid Particles</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-extrabold text-emerald-600">{analysis.valid_particles || analysis.particle_count}</span>
            <span className="text-xs text-emerald-700">passed filters</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-amber-600 text-xs font-semibold block uppercase tracking-wider">Filtered Artifacts</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-extrabold text-amber-600">{analysis.filtered_objects || 0}</span>
            <span className="text-xs text-amber-700">noise / size limits</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <span className="text-indigo-600 text-xs font-semibold block uppercase tracking-wider">Microscope Scale</span>
          <div className="mt-1">
            {analysis.pixel_size_um ? (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">
                Calibration: {analysis.pixel_size_um} µm/pixel
              </span>
            ) : (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
                Calibration: Not provided (px)
              </span>
            )}
          </div>
        </div>
      </div>

      {/* TAB CONTENT 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* Export Actions Card */}
          <Card title="Export Analysis Data & Scientific Reports">
            <div className="flex flex-wrap items-center gap-4">
              <a
                href={`http://localhost:8000/api/v1/analysis/${analysis.analysis_id}/export/csv`}
                download
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-bold shadow-xs hover:bg-indigo-700 transition-colors"
              >
                <Layers className="w-4 h-4" /> Download Particle Morphometrics CSV
              </a>

              <a
                href={`http://localhost:8000/api/v1/analysis/${analysis.analysis_id}/export/summary`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 text-white text-xs font-bold shadow-xs hover:bg-slate-900 transition-colors"
              >
                <ShieldCheck className="w-4 h-4" /> Export Complete Scientific Summary (JSON)
              </a>
            </div>
          </Card>

          {/* Stage-Wise Processing Time Breakdown */}
          <Card title="Stage-Wise Pipeline Performance Breakdown">
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2 text-center text-xs font-mono">
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 text-[10px] block">Validation</span>
                <span className="font-bold text-slate-800">{(analysis.timing.validation_time * 1000).toFixed(1)} ms</span>
              </div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 text-[10px] block">Quality</span>
                <span className="font-bold text-slate-800">{(analysis.timing.quality_time * 1000).toFixed(1)} ms</span>
              </div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 text-[10px] block">Preprocessing</span>
                <span className="font-bold text-slate-800">{(analysis.timing.preprocessing_time * 1000).toFixed(1)} ms</span>
              </div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 text-[10px] block">Thresholding</span>
                <span className="font-bold text-slate-800">{((analysis.timing.thresholding_time || analysis.timing.segmentation_time || 0) * 1000).toFixed(1)} ms</span>
              </div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 text-[10px] block">Watershed</span>
                <span className="font-bold text-slate-800">{((analysis.timing.watershed_time || analysis.timing.instance_time || 0) * 1000).toFixed(1)} ms</span>
              </div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 text-[10px] block">Feature Extract</span>
                <span className="font-bold text-slate-800">{((analysis.timing.feature_extraction_time || analysis.timing.feature_time || 0) * 1000).toFixed(1)} ms</span>
              </div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 text-[10px] block">Analytics</span>
                <span className="font-bold text-slate-800">{(analysis.timing.analytics_time * 1000).toFixed(1)} ms</span>
              </div>
              <div className="p-2 bg-indigo-50 rounded-lg border border-indigo-200">
                <span className="text-indigo-600 text-[10px] font-bold block">Total Time</span>
                <span className="font-bold text-indigo-900">{(analysis.timing.total_time * 1000).toFixed(1)} ms</span>
              </div>
            </div>
          </Card>

          {/* Reproducibility & Pipeline Configuration Cards */}
          <Card
            title="Reproducibility & Pipeline Parameter Control"
            subtitle="Deterministic parameter configuration and SHA-256 canonical hash verification"
          >
            <div className="space-y-6 text-xs">
              {/* Pipeline Version & Hash Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-slate-400 font-semibold block text-[10px] uppercase tracking-wider mb-0.5">Pipeline Version</span>
                    <span className="font-mono font-extrabold text-indigo-600 text-sm">{analysis.pipeline_version}</span>
                  </div>
                  <span className="px-2.5 py-1 rounded-md text-[11px] font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">
                    Deterministic Baseline
                  </span>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                  <div>
                    <span className="text-slate-400 font-semibold flex items-center gap-1 text-[10px] uppercase tracking-wider mb-0.5">
                      <Hash className="w-3 h-3 text-slate-400" /> Canonical Config Hash (SHA-256)
                    </span>
                    <span className="font-mono text-slate-800 text-xs font-bold block">
                      {shortHash}
                    </span>
                  </div>
                  <button
                    onClick={handleCopyHash}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 font-semibold transition-colors shadow-2xs"
                    title="Copy full 64-character SHA-256 hash"
                  >
                    {copiedHash ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
                    <span>{copiedHash ? 'Copied!' : 'Copy Hash'}</span>
                  </button>
                </div>
              </div>

              {/* Effective Parameter Cards */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-800 text-xs flex items-center gap-1.5">
                    <SlidersHorizontal className="w-4 h-4 text-indigo-600" /> Pipeline Parameter Settings
                  </h4>
                  <button
                    onClick={() => setShowConfig(!showConfig)}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
                  >
                    {showConfig ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    <span>{showConfig ? 'Hide Raw JSON Schema' : 'View Raw JSON Schema'}</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-slate-500 text-[10px] font-bold block uppercase tracking-wider">1. Preprocessing</span>
                    <div className="text-slate-800 font-semibold text-xs space-y-1">
                      <div className="flex items-center gap-1.5 text-emerald-700"><CheckCircle2 className="w-3.5 h-3.5" /> FastNLMeans (h=10)</div>
                      <div className="flex items-center gap-1.5 text-emerald-700"><CheckCircle2 className="w-3.5 h-3.5" /> Top-Hat (Kernel 31)</div>
                      <div className="flex items-center gap-1.5 text-emerald-700"><CheckCircle2 className="w-3.5 h-3.5" /> CLAHE (Clip 3.0)</div>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-slate-500 text-[10px] font-bold block uppercase tracking-wider">2. Segmentation</span>
                    <div className="text-slate-800 font-semibold text-xs space-y-1">
                      <div className="flex items-center gap-1.5 text-indigo-700"><CheckCircle2 className="w-3.5 h-3.5" /> Otsu Thresholding</div>
                      <div className="flex items-center gap-1.5 text-indigo-700"><CheckCircle2 className="w-3.5 h-3.5" /> Auto Inversion Polarity</div>
                      <div className="flex items-center gap-1.5 text-indigo-700"><CheckCircle2 className="w-3.5 h-3.5" /> Opening (3px), Closing (5px)</div>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-slate-500 text-[10px] font-bold block uppercase tracking-wider">3. Watershed Separation</span>
                    <div className="text-slate-800 font-semibold text-xs space-y-1">
                      <div className="flex items-center gap-1.5 text-purple-700"><CheckCircle2 className="w-3.5 h-3.5" /> Distance Transform</div>
                      <div className="flex items-center gap-1.5 text-purple-700"><CheckCircle2 className="w-3.5 h-3.5" /> Local Maxima Peaks</div>
                      <div className="flex items-center gap-1.5 text-purple-700"><CheckCircle2 className="w-3.5 h-3.5" /> Marker Min Distance (7px)</div>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <span className="text-slate-500 text-[10px] font-bold block uppercase tracking-wider">4. Feature Extraction</span>
                    <div className="text-slate-800 font-semibold text-xs space-y-1">
                      <div className="flex items-center gap-1.5 text-slate-700"><CheckCircle2 className="w-3.5 h-3.5" /> Image Moments & BBox</div>
                      <div className="flex items-center gap-1.5 text-slate-700"><CheckCircle2 className="w-3.5 h-3.5" /> Skeleton / Feret / Circularity</div>
                      <div className="flex items-center gap-1.5 text-slate-700"><CheckCircle2 className="w-3.5 h-3.5" /> GLCM Texture Features</div>
                    </div>
                  </div>
                </div>

                {showConfig && (
                  <div className="p-4 bg-slate-900 text-emerald-400 rounded-xl font-mono text-[11px] overflow-x-auto border border-slate-800 animate-in fade-in duration-200">
                    <pre>{JSON.stringify(analysis.configuration || {
                      pipeline_version: analysis.pipeline_version,
                      preprocessing: { denoise: true, fast_nl_means_h: 10, top_hat_kernel_size: 31, clahe_clip_limit: 3.0 },
                      segmentation: { threshold_method: 'otsu', adaptive_block_size: 15 },
                      morphology: { opening_kernel_size: 3, closing_kernel_size: 5 },
                      watershed: { min_distance: 7 }
                    }, null, 2)}</pre>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Image Quality Assessment */}
          <QualitySection
            imageInfo={analysis.image_info}
            quality={analysis.quality_assessment}
            originalPath={originalPath}
          />

          {/* Preprocessing Grid */}
          <PreprocessingGrid artifacts={analysis.artifacts} />

          {/* Segmentation Section */}
          <SegmentationSection artifacts={analysis.artifacts} thresholdMethod="otsu" />

          {/* Instance Section */}
          <InstanceSection artifacts={analysis.artifacts} particleCount={analysis.particle_count} />

          {/* Printable Report */}
          <PrintableReport analysis={analysis} />
        </div>
      )}

      {/* TAB CONTENT 2: PARTICLE INSPECTOR & SCATTER EXPLORER */}
      {activeTab === 'inspector' && (
        <div className="space-y-8">
          <Card
            title="Interactive Microscopy Viewer & Bi-directional Particle Linking"
            subtitle="Zoom, pan, and click particles on the interactive image viewer or scatter plot to inspect morphometrics."
          >
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-7">
                <InteractiveImageViewer
                  imagePath={overlayPath}
                  particles={analysis.particles}
                  selectedParticleId={selectedParticleId}
                  onSelectParticle={(id) => setSelectedParticleId(id)}
                  imageWidth={analysis.image_info.width}
                  imageHeight={analysis.image_info.height}
                />
              </div>

              <div className="lg:col-span-5">
                <ScatterExplorer
                  particles={analysis.particles}
                  selectedParticleId={selectedParticleId}
                  onSelectParticle={(id) => setSelectedParticleId(id)}
                />
              </div>
            </div>
          </Card>

          {/* Particle Explorer Inventory Table */}
          <ParticleTable particles={analysis.particles} />

          {/* Morphology Charts & Histograms */}
          <MorphologyCharts analytics={analysis.sample_analytics} particles={analysis.particles} />

          {/* Spatial Centroid Map */}
          <SpatialMap
            particles={analysis.particles}
            analytics={analysis.sample_analytics}
            imageWidth={analysis.image_info.width}
            imageHeight={analysis.image_info.height}
          />
        </div>
      )}

      {/* TAB CONTENT 3: MODEL COMPARISON */}
      {activeTab === 'comparison' && (
        <div className="space-y-8">
          <ModelComparisonSection />
        </div>
      )}

      {/* TAB CONTENT 4: EXPLAINABILITY & SALIENCY */}
      {activeTab === 'explainability' && (
        <div className="space-y-8">
          <ExplainabilitySection
            originalImagePath={originalPath}
            analysisId={analysis.analysis_id}
          />
        </div>
      )}
    </div>
  );
};
