import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Microscope, Sliders, FileText, CheckCircle2, AlertTriangle } from 'lucide-react';
import { apiService } from '../../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    apiService.getHealth()
      .then(() => setHealthy(true))
      .catch(() => setHealthy(false));
  }, []);

  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40 shadow-sm no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-md group-hover:bg-indigo-500 transition-colors">
            <Microscope className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white">MicroPlastic-Vision</span>
              <span className="text-xs px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 font-mono">v0.1.0</span>
            </div>
            <p className="text-xs text-slate-400">Automated Microplastic Computer Vision Analysis</p>
          </div>
        </Link>

        <nav className="flex items-center gap-1 sm:gap-4">
          <Link
            to="/"
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              location.pathname === '/'
                ? 'bg-slate-800 text-indigo-400'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>Workstation</span>
          </Link>

          <Link
            to="/evaluation"
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              location.pathname === '/evaluation'
                ? 'bg-slate-800 text-indigo-400'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Model Evaluation</span>
          </Link>

          <div className="ml-4 pl-4 border-l border-slate-800 flex items-center gap-2 text-xs">
            {healthy === true && (
              <span className="inline-flex items-center gap-1.5 text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-800">
                <CheckCircle2 className="w-3.5 h-3.5" /> Backend Online
              </span>
            )}
            {healthy === false && (
              <span className="inline-flex items-center gap-1.5 text-amber-400 bg-amber-950/60 px-2.5 py-1 rounded-full border border-amber-800">
                <AlertTriangle className="w-3.5 h-3.5" /> Backend Offline
              </span>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
};
