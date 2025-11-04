/**
 * Page HistoryPage - Historique des batches uploadés
 */
import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import BatchCard from '../components/history/BatchCard';
import BatchDetailsModal from '../components/history/BatchDetailsModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

const HistoryPage = () => {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [selectedPredictions, setSelectedPredictions] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const handleDeleteBatch = (batchId) => {
    setBatches((prevBatches) => prevBatches.filter((b) => b.id !== batchId));
  };

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
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
                <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Historique des Analyses</h1>
                <p className="text-gray-600 mt-1">Liste de tous les fichiers CSV analysés</p>
              </div>
            </div>

            <button
              onClick={loadBatches}
              disabled={loading}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <svg className={`w-5 h-5 mr-2 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {loading ? 'Chargement...' : 'Actualiser'}
            </button>
          </div>

          {/* Stats Globales */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Total Batches */}
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-600 font-medium">Total Batches</p>
                  <p className="text-3xl font-bold text-blue-600">{batches.length}</p>
                </div>
              </div>

              {/* Clients Analysés */}
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-600 font-medium">Clients Analysés</p>
                  <p className="text-3xl font-bold text-green-600">
                    {batches.reduce((sum, b) => sum + b.total_clients, 0)}
                  </p>
                </div>
              </div>

              {/* Fraudeurs Détectés */}
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-600 font-medium">Fraudeurs Détectés</p>
                  <p className="text-3xl font-bold text-red-600">
                    {batches.reduce((sum, b) => sum + b.fraud_detected, 0)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading */}
        {loading && <LoadingSpinner message="Chargement de l'historique..." />}

        {/* Error */}
        {error && !loading && (
          <ErrorMessage type="error" title="Erreur de chargement" message={error} onRetry={loadBatches} />
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
                <div className="w-20 h-20 mx-auto mb-6 bg-gray-100 rounded-2xl flex items-center justify-center">
                  <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Aucun batch trouvé</h3>
                <p className="text-gray-600 mb-6">
                  Commencez par uploader un fichier CSV dans l'analyse batch
                </p>
                <a
                  href="/batch"
                  className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Uploader un CSV
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
