import React, { useState } from 'react';
import { Network } from 'lucide-react';
import { Card } from '../common/Card';
import { ScientificImageViewer } from '../image-viewer/ScientificImageViewer';

interface InstanceSectionProps {
  artifacts: Record<string, string>;
  particleCount: number;
}

export const InstanceSection: React.FC<InstanceSectionProps> = ({
  artifacts,
  particleCount,
}) => {
  const [activeTab, setActiveTab] = useState<'watershed' | 'ids' | 'overlay' | 'contours'>('watershed');

  const tabs = [
    { id: 'watershed', label: 'Watershed Instance Map', artifactKey: 'watershed_instances' },
    { id: 'ids', label: 'Particle ID Map (P001...)', artifactKey: 'particle_ids' },
    { id: 'overlay', label: 'Segmentation Overlay', artifactKey: 'segmentation_overlay' },
    { id: 'contours', label: 'Bounding Boxes & Contours', artifactKey: 'particle_contours' },
  ].filter((t) => artifacts[t.artifactKey]);

  return (
    <Card
      title="Watershed Particle Instance Separation"
      subtitle="Distance Transform & Local Maxima peak marker identification separating touching particles"
      action={
        <div className="flex items-center gap-1.5 px-3 py-1 bg-indigo-50 border border-indigo-200 rounded-lg text-indigo-900 font-bold text-xs">
          <Network className="w-4 h-4 text-indigo-600" />
          <span>Detected: {particleCount} Particles</span>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Tab Buttons */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Selected Instance View */}
        {artifacts[tabs.find((t) => t.id === activeTab)?.artifactKey || 'watershed_instances'] && (
          <div className="max-w-4xl mx-auto">
            <ScientificImageViewer
              src={artifacts[tabs.find((t) => t.id === activeTab)?.artifactKey || 'watershed_instances']}
              alt={tabs.find((t) => t.id === activeTab)?.label || 'Instance Map'}
              title={tabs.find((t) => t.id === activeTab)?.label || 'Instance Map'}
              caption={`Watershed instance separation map displaying ${particleCount} individual particles`}
            />
          </div>
        )}
      </div>
    </Card>
  );
};
