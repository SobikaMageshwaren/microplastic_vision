import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Home } from './pages/Home';
import { Analysis } from './pages/Analysis';
import { Evaluation } from './pages/Evaluation';
import { NotFound } from './pages/NotFound';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analysis/:analysisId" element={<Analysis />} />
            <Route path="/evaluation" element={<Evaluation />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <footer className="bg-slate-900 text-slate-400 py-6 border-t border-slate-800 text-xs no-print">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white">MicroPlastic-Vision</span>
              <span>• Scientific Computer Vision Pipeline</span>
            </div>
            <div className="text-slate-500">
              Microscopy Analysis Workstation v0.1.0 • Classical CV Engine
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
