/**
 * Page HistoryPage - Historique des batches uploadés
 */
import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import BatchCard from '../components/history/BatchCard';
import BatchDetailsModal from '../components/history/BatchDetailsModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { checkApiHealth } from '../services/api';

const HistoryPage = () => {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [selectedPredictions, setSelectedPredictions] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const handleDeleteBatch = (batchId) => {
  // Retire le batch de la liste
  setBatches(prevBatches => prevBatches.filter(b => b.id !== batchId));
};

  // Charger les batches au montage
  useEffect(() => {
    loadBatches();
  }, []);

  const loadBatches = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/predictions/batches');
      if (!response.ok) throw new Error(`Erreur ${response.status}`);

      const data = await response.json();
      setBatches(data.batches || []);
    } catch (err) {
      console.error('Erreur chargement batches:', err);
      setError(err.message || 'Impossible de charger les batches');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (batchId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/predictions/batch/${batchId}`);
      if (!response.ok) throw new Error('Erreur chargement détails');

      const data = await response.json();
      setSelectedBatch(data.batch);
      setSelectedPredictions(data.predictions);
      setShowModal(true);
    } catch (err) {
      console.error('Erreur chargement détails:', err);
      alert('Impossible de charger les détails du batch');
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedBatch(null);
    setSelectedPredictions(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                📜 Historique des Analyses
              </h1>
              <p className="text-gray-600">
                Liste de tous les fichiers CSV analysés
              </p>
            </div>

            <button
              onClick={loadBatches}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              🔄 Actualiser
            </button>
          </div>

          {/* Stats Globales */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Batches</p>
                <p className="text-3xl font-bold text-blue-600">{batches.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Clients Analysés</p>
                <p className="text-3xl font-bold text-green-600">
                  {batches.reduce((sum, b) => sum + b.total_clients, 0)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Fraudeurs Détectés</p>
                <p className="text-3xl font-bold text-red-600">
                  {batches.reduce((sum, b) => sum + b.fraud_detected, 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Loading */}
        {loading && <LoadingSpinner message="Chargement de l'historique..." />}

        {/* Error */}
        {error && !loading && (
          <ErrorMessage
            type="error"
            title="Erreur de chargement"
            message={error}
            onRetry={loadBatches}
          />
        )}

        {/* Liste des Batches */}
        {!loading && !error && (
          <>
            {batches.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {batches.map((batch) => (
                  <BatchCard
                        key={batch.id}
                       batch={batch}
                        onViewDetails={handleViewDetails}
                       onDelete={handleDeleteBatch}
                            />
                ))}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="text-6xl mb-4">📭</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Aucun batch trouvé
                </h3>
                <p className="text-gray-600 mb-6">
                  Commencez par uploader un fichier CSV dans l'analyse batch
                </p>

                <a
                  href="/batch"
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
                >
                  📤 Uploader un CSV
                </a>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modal Détails */}
      {showModal && (
        <BatchDetailsModal
          batch={selectedBatch}
          predictions={selectedPredictions}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default HistoryPage;
