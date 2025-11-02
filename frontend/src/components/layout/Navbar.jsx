/**
 * Composant Navbar - Barre de navigation
 */
import React, { useState, useEffect } from 'react';
import { checkPredictionHealth } from '../../services/api';

const Navbar = () => {
  const [apiStatus, setApiStatus] = useState('checking'); // 'checking', 'healthy', 'unhealthy'

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await checkPredictionHealth();
        setApiStatus(response.model_loaded ? 'healthy' : 'unhealthy');
      } catch (error) {
        setApiStatus('unhealthy');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const StatusIndicator = () => {
    const statuses = {
      checking: { color: 'bg-gray-400', text: 'Vérification...', pulse: true },
      healthy: { color: 'bg-green-500', text: 'API Opérationnelle', pulse: false },
      unhealthy: { color: 'bg-red-500', text: 'API Hors Ligne', pulse: true },
    };

    const status = statuses[apiStatus];

    return (
      <div className="flex items-center space-x-2">
        <div className="relative">
          <div
            className={`w-2 h-2 rounded-full ${status.color} ${
              status.pulse ? 'animate-pulse' : ''
            }`}
          />
        </div>
        <span className="text-sm text-gray-600">{status.text}</span>
      </div>
    );
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Titre */}
          <div className="flex items-center space-x-3">
            <div className="text-3xl">🔍</div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Fraud Detection
              </h1>
              <p className="text-xs text-gray-500">
                Plateforme de détection de fraude électrique
              </p>
            </div>
          </div>

          {/* Liens de navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <a
              href="/"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              🏠 Accueil
            </a>
            <a
              href="/batch"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              📤 Analyse Batch
            </a>
            <a
              href="/realtime"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              🔴 Temps Réel
            </a>
            <a
              href="/dashboard"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              📊 Dashboard
            </a>
            <a
            href="/history"
            className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
          >
            📜 Historique
          </a>
          </div>

          {/* Statut & Documentation */}
          <div className="flex items-center space-x-4">
            <StatusIndicator />
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
              title="Documentation API"
            >
              📚 API Docs
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
