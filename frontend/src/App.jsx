import React from 'react';
import Navbar from './components/layout/Navbar';
import BatchPage from './pages/BatchPage';
import ClientDetailsPage from './pages/ClientDetailsPage';
import HistoryPage from './pages/HistoryPage';



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

    // Page d'accueil par défaut
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        
        <div className="max-w-7xl mx-auto px-4 py-16">
          <div className="text-center">
            <div className="text-6xl mb-6">🔍</div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Plateforme de Détection de Fraude
            </h1>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Analysez vos données de consommation électrique et détectez les anomalies
              grâce à l'intelligence artificielle
            </p>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => navigate('/batch')}
                className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors shadow-lg"
              >
                📤 Analyse Batch
              </button>
              <button
                onClick={() => navigate('/realtime')}
                className="bg-green-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-green-700 transition-colors shadow-lg"
              >
                🔴 Temps Réel
              </button>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="font-bold text-lg mb-2">Rapide</h3>
                <p className="text-gray-600 text-sm">
                  Analyse de milliers de clients en quelques secondes
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="text-4xl mb-4">🎯</div>
                <h3 className="font-bold text-lg mb-2">Précis</h3>
                <p className="text-gray-600 text-sm">
                  Modèle ML entraîné avec 72% de recall
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="font-bold text-lg mb-2">Complet</h3>
                <p className="text-gray-600 text-sm">
                  Dashboard détaillé et visualisations interactives
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return renderPage();
}

export default App;