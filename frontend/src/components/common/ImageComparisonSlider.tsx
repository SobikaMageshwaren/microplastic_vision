import React, { useState, useRef, useCallback, useEffect } from 'react';
import { SlidersHorizontal } from 'lucide-react';
import { getImageUrl } from '../../utils/image';

interface ImageComparisonSliderProps {
  beforeImage: string;
  afterImage: string;
  beforeLabel?: string;
  afterLabel?: string;
}

export const ImageComparisonSlider: React.FC<ImageComparisonSliderProps> = ({
  beforeImage,
  afterImage,
  beforeLabel = 'Original Image',
  afterLabel = 'Processed Artifact',
}) => {
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      let percentage = (x / rect.width) * 100;
      if (percentage < 0) percentage = 0;
      if (percentage > 100) percentage = 100;
      setSliderPosition(percentage);
    },
    []
  );

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (!isDragging) return;
      handleMove(e.touches[0].clientX);
    },
    [isDragging, handleMove]
  );

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging) return;
      handleMove(e.clientX);
    },
    [isDragging, handleMove]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      window.addEventListener('touchmove', handleTouchMove);
      window.addEventListener('touchend', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp, handleTouchMove]);

  return (
    <div
      ref={containerRef}
      className="relative w-full h-[400px] overflow-hidden rounded-2xl border border-slate-200 shadow-sm select-none cursor-ew-resize group bg-slate-950"
      onMouseDown={() => setIsDragging(true)}
      onTouchStart={() => setIsDragging(true)}
    >
      {/* After Image (Background layer) */}
      <img
        src={getImageUrl(afterImage)}
        alt={afterLabel}
        className="absolute inset-0 w-full h-full object-contain pointer-events-none"
      />
      <span className="absolute top-3 right-3 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase bg-slate-900/80 text-emerald-400 backdrop-blur-xs border border-slate-800 z-10">
        {afterLabel}
      </span>

      {/* Before Image (Clipped overlay layer) */}
      <div
        className="absolute inset-0 overflow-hidden pointer-events-none"
        style={{ width: `${sliderPosition}%` }}
      >
        <img
          src={getImageUrl(beforeImage)}
          alt={beforeLabel}
          className="absolute inset-0 w-full h-full object-contain pointer-events-none max-w-none"
          style={{ width: containerRef.current?.clientWidth || '100%' }}
        />
        <span className="absolute top-3 left-3 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase bg-slate-900/80 text-slate-300 backdrop-blur-xs border border-slate-800 z-10">
          {beforeLabel}
        </span>
      </div>

      {/* Vertical Split Line Divider */}
      <div
        className="absolute top-0 bottom-0 w-0.5 bg-white z-20 shadow-[0_0_10px_rgba(0,0,0,0.5)]"
        style={{ left: `${sliderPosition}%` }}
      >
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-white text-slate-800 flex items-center justify-center shadow-lg border-2 border-indigo-600 transition-transform group-hover:scale-110">
          <SlidersHorizontal className="w-4 h-4 rotate-90" />
        </div>
      </div>
    </div>
  );
};
