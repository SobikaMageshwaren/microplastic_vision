import React, { useState } from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Download, Image as ImageIcon } from 'lucide-react';
import { getImageUrl } from '../../utils/image';

interface ScientificImageViewerProps {
  src: string;
  alt: string;
  title?: string;
  caption?: string;
  className?: string;
}

export const ScientificImageViewer: React.FC<ScientificImageViewerProps> = ({
  src,
  alt,
  title,
  caption,
  className = '',
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const fullUrl = getImageUrl(src);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 4));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleReset = () => setZoom(1);

  const handleDownload = () => {
    const a = document.createElement('a');
    a.href = fullUrl;
    a.download = `${alt.replace(/\s+/g, '_')}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div
      className={`bg-slate-900 rounded-xl overflow-hidden border border-slate-800 flex flex-col ${
        isFullscreen ? 'fixed inset-0 z-50 rounded-none' : className
      }`}
    >
      {/* Viewer Header */}
      <div className="px-4 py-2.5 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between text-xs text-slate-300">
        <div className="flex items-center gap-2 font-medium">
          <ImageIcon className="w-4 h-4 text-indigo-400" />
          <span>{title || alt}</span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleZoomIn}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Reset Zoom"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          <button
            onClick={handleDownload}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors ml-1 border-l border-slate-800 pl-2"
            title="Download Image"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Image Canvas Container */}
      <div className="flex-1 overflow-auto p-4 flex items-center justify-center min-h-[300px] bg-slate-950/40 relative">
        <img
          src={fullUrl}
          alt={alt}
          style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
          className="max-h-[600px] object-contain transition-transform duration-150 rounded shadow-md"
        />
      </div>

      {caption && (
        <div className="px-4 py-2 bg-slate-950 text-slate-400 text-xs border-t border-slate-800 flex justify-between items-center">
          <span>{caption}</span>
          <span className="font-mono text-[10px] text-slate-500">Zoom: {Math.round(zoom * 100)}%</span>
        </div>
      )}
    </div>
  );
};
