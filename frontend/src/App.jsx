import React from 'react';
import Navbar from './components/layout/Navbar';
import BatchPage from './pages/BatchPage';
import ClientDetailsPage from './pages/ClientDetailsPage';
import HistoryPage from './pages/HistoryPage';

// Icônes SVG
const SearchIcon = () => (
  <svg className="w-16 h-16 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const UploadIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

const BoltIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const SpeedIcon = () => (
  <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const TargetIcon = () => (
  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const ChartIcon = () => (
  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

function App() {
  // Simple routing basé sur window.location
  const path = window.location.pathname;

  // Fonction pour naviguer
  const navigate = (path) => {
    window.history.pushState({}, '', path);
    window.location.reload();
  };

  // Render selon la route
  const renderPage = () => {
    if (path.startsWith('/client/')) {
      return <ClientDetailsPage />;
    }
    if (path === '/batch') {
      return <BatchPage />;
    }
    if (path === '/history') {
      return <HistoryPage />;
    }

    // ========== PAGE D'ACCUEIL - NOUVEAU DESIGN ==========
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50">
        <Navbar />
        
        <div className="max-w-7xl mx-auto px-4 py-16 sm:py-24">
          {/* Hero Section */}
          <div className="text-center mb-20">
            {/* Icon */}
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-2xl mb-8 shadow-lg">
              <SearchIcon />
            </div>
            
            {/* Title */}
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Détection de Fraude
              <span className="block text-blue-600 mt-2">Électrique</span>
            </h1>
            
            {/* Subtitle */}
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed mb-10">
              Analysez vos données de consommation électrique et détectez les anomalies 
              grâce à l'intelligence artificielle
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button
                onClick={() => navigate('/batch')}
                className="group inline-flex items-center justify-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5"
              >
                <UploadIcon />
                <span className="ml-2">Analyse Batch</span>
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
              
              <button
                onClick={() => navigate('/realtime')}
                className="group inline-flex items-center justify-center px-8 py-4 bg-white text-gray-700 font-semibold rounded-xl border-2 border-gray-300 hover:border-blue-600 hover:text-blue-600 shadow-md hover:shadow-lg transition-all transform hover:-translate-y-0.5"
              >
                <BoltIcon />
                <span className="ml-2">Temps Réel</span>
              </button>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Feature 1 - Rapide */}
            <div className="group bg-white rounded-2xl p-8 shadow-md hover:shadow-2xl transition-all transform hover:-translate-y-1">
              <div className="w-16 h-16 bg-yellow-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <SpeedIcon />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Rapide
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Analyse de milliers de clients en quelques secondes grâce à notre moteur ML optimisé
              </p>
              
              {/* Stats */}
              <div className="mt-6 pt-6 border-t border-gray-100">
                <div className="flex items-center text-sm text-gray-500">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>Résultats en &lt; 5 secondes</span>
                </div>
              </div>
            </div>

            {/* Feature 2 - Précis */}
            <div className="group bg-white rounded-2xl p-8 shadow-md hover:shadow-2xl transition-all transform hover:-translate-y-1">
              <div className="w-16 h-16 bg-green-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <TargetIcon />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Précis
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Modèle ML entraîné avec 72% de recall pour une détection fiable des fraudes électriques
              </p>
              
              {/* Stats */}
              <div className="mt-6 pt-6 border-t border-gray-100">
                <div className="flex items-center text-sm text-gray-500">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>72% Recall • 85% Accuracy</span>
                </div>
              </div>
            </div>

            {/* Feature 3 - Complet */}
            <div className="group bg-white rounded-2xl p-8 shadow-md hover:shadow-2xl transition-all transform hover:-translate-y-1">
              <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <ChartIcon />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Complet
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Dashboard détaillé avec visualisations interactives et historique complet de toutes les analyses
              </p>
              
              {/* Stats */}
              <div className="mt-6 pt-6 border-t border-gray-100">
                <div className="flex items-center text-sm text-gray-500">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span>15 Features • 5 Tables DB</span>
                </div>
              </div>
            </div>
          </div>

          {/* Tech Stack Banner */}
          <div className="mt-20 bg-white rounded-2xl shadow-lg p-8">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Technologies Utilisées
              </h3>
              <p className="text-sm text-gray-500">
                Stack moderne et performant
              </p>
            </div>
            
            <div className="flex flex-wrap justify-center gap-4">
              {[
                { name: 'Python', color: 'blue' },
                { name: 'LightGBM', color: 'green' },
                { name: 'FastAPI', color: 'teal' },
                { name: 'React', color: 'blue' },
                { name: 'PostgreSQL', color: 'indigo' },
                { name: 'Docker', color: 'cyan' }
              ].map((tech) => (
                <span
                  key={tech.name}
                  className={`px-4 py-2 bg-${tech.color}-50 text-${tech.color}-700 rounded-lg font-medium text-sm border border-${tech.color}-200`}
                >
                  {tech.name}
                </span>
              ))}
            </div>
          </div>

          {/* Stats Section */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl p-6 text-center shadow-md">
              <div className="text-3xl font-bold text-blue-600 mb-2">15</div>
              <div className="text-sm text-gray-600">Features ML</div>
            </div>
            <div className="bg-white rounded-xl p-6 text-center shadow-md">
              <div className="text-3xl font-bold text-green-600 mb-2">72%</div>
              <div className="text-sm text-gray-600">Recall</div>
            </div>
            <div className="bg-white rounded-xl p-6 text-center shadow-md">
              <div className="text-3xl font-bold text-purple-600 mb-2">5</div>
              <div className="text-sm text-gray-600">Tables DB</div>
            </div>
            <div className="bg-white rounded-xl p-6 text-center shadow-md">
              <div className="text-3xl font-bold text-orange-600 mb-2">8</div>
              <div className="text-sm text-gray-600">API Endpoints</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return renderPage();
}

export default App;