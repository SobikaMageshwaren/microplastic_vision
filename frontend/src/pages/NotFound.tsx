import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export const NotFound: React.FC = () => {
  return (
    <div className="max-w-md mx-auto px-4 py-20 text-center space-y-4">
      <h1 className="text-4xl font-extrabold text-slate-900 font-mono">404</h1>
      <h2 className="text-lg font-bold text-slate-800">Page Not Found</h2>
      <p className="text-xs text-slate-500">The requested workstation route does not exist.</p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Workstation
      </Link>
    </div>
  );
};
