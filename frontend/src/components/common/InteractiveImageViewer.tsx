import React, { useState, useRef } from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Eye, Layers } from 'lucide-react';
import { ParticleFeatures } from '../../types/particle';
import { getImageUrl } from '../../utils/image';

interface InteractiveImageViewerProps {
  imagePath: string;
  particles?: ParticleFeatures[];
  selectedParticleId?: string | null;
  onSelectParticle?: (particleId: string) => void;
  imageWidth?: number;
  imageHeight?: number;
}

export const InteractiveImageViewer: React.FC<InteractiveImageViewerProps> = ({
  imagePath,
  particles = [],
  selectedParticleId,
  onSelectParticle,
  imageWidth = 2048,
  imageHeight = 2048,
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 4));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleReset = () => setZoom(1);

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch(() => {});
      setIsFullscreen(false);
    }
  };

  const selectedParticle = particles.find((p) => p.particle_id === selectedParticleId);

  return (
    <div
      ref={containerRef}
      className={`relative w-full overflow-hidden rounded-2xl border border-slate-200 bg-slate-950 flex flex-col justify-between ${
        isFullscreen ? 'h-screen' : 'h-[480px]'
      }`}
    >
      {/* Control Toolbar */}
      <div className="absolute top-3 left-3 right-3 flex items-center justify-between z-30 pointer-events-auto">
        <div className="flex items-center gap-1.5 p-1.5 rounded-xl bg-slate-900/80 backdrop-blur-md border border-slate-800 text-slate-300 shadow-lg">
          <button
            onClick={handleZoomIn}
            className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
            title="Reset Zoom"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <span className="text-[11px] font-mono px-2 text-indigo-400 font-bold border-l border-slate-800">
            {(zoom * 100).toFixed(0)}%
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold backdrop-blur-md border shadow-lg transition-colors ${
              showOverlays
                ? 'bg-indigo-600/90 text-white border-indigo-500'
                : 'bg-slate-900/80 text-slate-400 border-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" /> Overlays {showOverlays ? 'ON' : 'OFF'}
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-xl bg-slate-900/80 text-slate-300 hover:text-white backdrop-blur-md border border-slate-800 shadow-lg"
            title="Toggle Fullscreen"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Image Area */}
      <div className="relative w-full h-full flex items-center justify-center overflow-auto p-4">
        <div
          className="relative transition-transform duration-200 ease-out origin-center"
          style={{ transform: `scale(${zoom})` }}
        >
          <img
            src={getImageUrl(imagePath)}
            alt="Microscopy Sample"
            className="max-h-[400px] w-auto object-contain rounded-lg shadow-2xl"
          />

          {/* Particle Bounding Box & Centroid Overlays */}
          {showOverlays &&
            particles.map((p) => {
              const isSelected = p.particle_id === selectedParticleId;
              const scaleX = 100 / (imageWidth || 1);
              const scaleY = 100 / (imageHeight || 1);

              return (
                <div
                  key={p.particle_id}
                  onClick={() => onSelectParticle && onSelectParticle(p.particle_id)}
                  title={`${p.particle_id}: Area=${p.area} px²`}
                  className={`absolute rounded-xs cursor-pointer transition-all ${
                    isSelected
                      ? 'border-2 border-amber-400 bg-amber-400/30 z-20 shadow-[0_0_12px_rgba(251,191,36,0.8)]'
                      : 'border border-indigo-500/60 bg-indigo-500/10 hover:border-emerald-400 hover:bg-emerald-400/20'
                  }`}
                  style={{
                    left: `${(p.bbox.x / (imageWidth || 1)) * 100}%`,
                    top: `${(p.bbox.y / (imageHeight || 1)) * 100}%`,
                    width: `${(p.bbox.width / (imageWidth || 1)) * 100}%`,
                    height: `${(p.bbox.height / (imageHeight || 1)) * 100}%`,
                  }}
                >
                  {isSelected && (
                    <span className="absolute -top-6 left-0 px-1.5 py-0.5 rounded-md bg-amber-400 text-slate-950 font-extrabold text-[10px] shadow-sm whitespace-nowrap">
                      {p.particle_id}
                    </span>
                  )}
                </div>
              );
            })}
        </div>
      </div>

      {/* Selected Particle Footer Banner */}
      {selectedParticle && (
        <div className="p-3 bg-slate-900/90 backdrop-blur-md border-t border-slate-800 text-xs flex items-center justify-between text-slate-300 z-30">
          <div className="flex items-center gap-3">
            <span className="font-extrabold text-amber-400 font-mono">Selected: {selectedParticle.particle_id}</span>
            <span>Area: <strong className="text-white">{selectedParticle.area} px²</strong> ({selectedParticle.area_um2 ? `${selectedParticle.area_um2} µm²` : 'uncalibrated'})</span>
            <span>Circularity: <strong className="text-white">{selectedParticle.circularity}</strong></span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">Centroid: ({selectedParticle.centroid.x}, {selectedParticle.centroid.y})</span>
        </div>
      )}
    </div>
  );
};
