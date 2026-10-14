import React, { useState, useMemo } from 'react';
import { Search, ArrowUpDown, ChevronLeft, ChevronRight, Eye } from 'lucide-react';
import { ParticleFeatures } from '../../types/particle';
import { Card } from '../common/Card';
import { ParticleModal } from './ParticleModal';
import { formatNumber } from '../../utils/formatting';

interface ParticleTableProps {
  particles: ParticleFeatures[];
}

export const ParticleTable: React.FC<ParticleTableProps> = ({ particles }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortField, setSortField] = useState<keyof ParticleFeatures>('particle_id');
  const [sortAsc, setSortAsc] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedParticle, setSelectedParticle] = useState<ParticleFeatures | null>(null);

  const pageSize = 10;

  const filtered = useMemo(() => {
    return particles.filter((p) =>
      p.particle_id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [particles, searchTerm]);

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];

      if (typeof valA === 'string') {
        valA = (valA as string).toLowerCase();
        valB = (valB as string).toLowerCase();
      }

      if (valA! < valB!) return sortAsc ? -1 : 1;
      if (valA! > valB!) return sortAsc ? 1 : -1;
      return 0;
    });
  }, [filtered, sortField, sortAsc]);

  const totalPages = Math.ceil(sorted.length / pageSize) || 1;
  const paginated = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sorted.slice(start, start + pageSize);
  }, [sorted, currentPage]);

  const handleSort = (field: keyof ParticleFeatures) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  return (
    <Card
      title="Extracted Particle Inventory"
      subtitle={`Detailed geometric and morphological feature vectors for ${particles.length} detected particle instances`}
      action={
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search particle ID..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-48 sm:w-64"
          />
        </div>
      }
    >
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600 border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-700 font-semibold">
              <th className="py-3 px-4 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('particle_id')}>
                <div className="flex items-center gap-1">
                  ID <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('area')}>
                <div className="flex items-center gap-1">
                  Area (px²) <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('perimeter')}>
                <div className="flex items-center gap-1">
                  Perimeter (px) <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('circularity')}>
                <div className="flex items-center gap-1">
                  Circularity <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('aspect_ratio')}>
                <div className="flex items-center gap-1">
                  Aspect Ratio <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('solidity')}>
                <div className="flex items-center gap-1">
                  Solidity <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4">Centroid (X, Y)</th>
              <th className="py-3 px-4 text-right">Inspect</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {paginated.length > 0 ? (
              paginated.map((p) => (
                <tr
                  key={p.particle_id}
                  onClick={() => setSelectedParticle(p)}
                  className="hover:bg-indigo-50/40 cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                      {p.particle_id.includes('_p')
                        ? `P-${p.particle_id.split('_p')[1].padStart(3, '0')}`
                        : p.particle_id}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 font-medium text-slate-900">{formatNumber(p.area)}</td>
                  <td className="py-2.5 px-4">{formatNumber(p.perimeter)}</td>
                  <td className="py-2.5 px-4 font-semibold text-slate-800">{p.circularity}</td>
                  <td className="py-2.5 px-4">{p.aspect_ratio}</td>
                  <td className="py-2.5 px-4">{p.solidity}</td>
                  <td className="py-2.5 px-4 font-mono text-slate-500">
                    ({p.centroid.x}, {p.centroid.y})
                  </td>
                  <td className="py-2.5 px-4 text-right">
                    <button className="p-1 rounded bg-slate-100 hover:bg-indigo-600 hover:text-white text-slate-600 transition-colors">
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-400">
                  No particles found matching "{searchTerm}"
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>
          Showing {sorted.length > 0 ? (currentPage - 1) * pageSize + 1 : 0} to{' '}
          {Math.min(currentPage * pageSize, sorted.length)} of {sorted.length} particles
        </span>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
            disabled={currentPage === 1}
            className="p-1.5 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="font-semibold text-slate-700">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="p-1.5 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Modal Inspector */}
      {selectedParticle && (
        <ParticleModal particle={selectedParticle} onClose={() => setSelectedParticle(null)} />
      )}
    </Card>
  );
};
