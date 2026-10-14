import React from 'react';
import { X, Box, Crosshair, Sparkles, Layers, Activity } from 'lucide-react';
import { ParticleFeatures } from '../../types/particle';
import { getImageUrl } from '../../utils/image';
import { formatNumber } from '../../utils/formatting';

interface ParticleModalProps {
  particle: ParticleFeatures | null;
  onClose: () => void;
}

export const ParticleModal: React.FC<ParticleModalProps> = ({ particle, onClose }) => {
  if (!particle) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-2xl w-full overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold font-mono text-indigo-400 bg-indigo-950 px-3 py-1 rounded border border-indigo-800">
              {particle.particle_id.includes('_p')
                ? `P-${particle.particle_id.split('_p')[1].padStart(3, '0')}`
                : particle.particle_id}
            </span>
            <div>
              <h3 className="font-bold text-white text-base">Particle Feature Inspector</h3>
              <p className="text-xs text-slate-400">
                Session: #{particle.analysis_id ? particle.analysis_id.replace(/^ana_/, '').slice(0, 8).toUpperCase() : 'ACTIVE'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
          {/* Top Row: Crop Image & BBox/Centroid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="bg-slate-900 rounded-xl p-3 border border-slate-800 flex flex-col items-center justify-center">
              <span className="text-xs font-semibold text-slate-400 mb-2">Cropped Particle BGR</span>
              {particle.crop_path ? (
                <img
                  src={getImageUrl(particle.crop_path)}
                  alt={`Particle ${particle.particle_id} Crop`}
                  className="max-h-36 object-contain rounded border border-slate-700 bg-black/40"
                />
              ) : (
                <div className="h-32 w-32 flex items-center justify-center text-slate-600 text-xs">
                  No Crop Available
                </div>
              )}
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="flex items-center gap-1.5 font-semibold text-slate-700 mb-1">
                  <Box className="w-4 h-4 text-indigo-600" /> Bounding Box (Pixels)
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-600 font-mono mt-2">
                  <div>X: {particle.bbox.x}</div>
                  <div>Y: {particle.bbox.y}</div>
                  <div>W: {particle.bbox.width}</div>
                  <div>H: {particle.bbox.height}</div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <div className="flex items-center gap-1.5 font-semibold text-slate-700 mb-1">
                  <Crosshair className="w-4 h-4 text-emerald-600" /> Centroid Coordinates
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-600 font-mono mt-2">
                  <div>X: {particle.centroid.x} px</div>
                  <div>Y: {particle.centroid.y} px</div>
                </div>
              </div>
            </div>
          </div>

          {/* Geometry & Shape Grid */}
          <div>
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" /> Geometric & Morphological Metrics
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Area</span>
                <span className="text-sm font-bold text-slate-900">{formatNumber(particle.area)} px²</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Perimeter</span>
                <span className="text-sm font-bold text-slate-900">{formatNumber(particle.perimeter)} px</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Circularity</span>
                <span className="text-sm font-bold text-indigo-600">{particle.circularity}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Aspect Ratio</span>
                <span className="text-sm font-bold text-slate-900">{particle.aspect_ratio}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Solidity</span>
                <span className="text-sm font-bold text-slate-900">{particle.solidity}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Eccentricity</span>
                <span className="text-sm font-bold text-slate-900">{particle.eccentricity}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Extent</span>
                <span className="text-sm font-bold text-slate-900">{particle.extent}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block mb-0.5">Compactness</span>
                <span className="text-sm font-bold text-slate-900">{particle.compactness}</span>
              </div>
            </div>
          </div>

          {/* Skeleton & Intensity */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h5 className="font-semibold text-slate-800 mb-2 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-indigo-600" /> Skeleton Properties
              </h5>
              <div className="space-y-1 text-slate-600 font-mono">
                <div>Length: {particle.skeleton_length} px</div>
                <div>Mean Thickness: {particle.mean_thickness} px</div>
                <div>Convex Hull Area: {particle.convex_hull_area} px²</div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h5 className="font-semibold text-slate-800 mb-2 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-600" /> Intensity Statistics
              </h5>
              <div className="space-y-1 text-slate-600 font-mono">
                <div>Mean Intensity: {particle.mean_intensity}</div>
                <div>Std Intensity: {particle.std_intensity}</div>
                <div>Min / Max: {particle.min_intensity} / {particle.max_intensity}</div>
              </div>
            </div>
          </div>

          {/* GLCM Texture Metrics */}
          {particle.glcm_contrast !== null && (
            <div className="p-4 rounded-xl bg-indigo-50/50 border border-indigo-100 text-xs">
              <h5 className="font-semibold text-indigo-900 mb-2">GLCM Texture Parameters</h5>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-indigo-800">
                <div>Contrast: {particle.glcm_contrast}</div>
                <div>Energy: {particle.glcm_energy}</div>
                <div>Homogeneity: {particle.glcm_homogeneity}</div>
                <div>Correlation: {particle.glcm_correlation}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
