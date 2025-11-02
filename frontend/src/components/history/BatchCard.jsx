/**
 * Composant BatchCard - Carte d'un batch uploadé
 */
import React, { useState } from 'react';
import { formatDate, formatPercentage } from '../../utils/formatters';

const BatchCard = ({ batch, onViewDetails, onDelete }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDelete = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    setIsDeleting(true);
    
    try {
      const response = await fetch(`http://localhost:8000/api/predictions/batch/${batch.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      // Appelle la fonction de callback
      if (onDelete) {
        onDelete(batch.id);
      }

    } catch (error) {
      console.error('Erreur suppression:', error);
      alert('Erreur lors de la suppression du batch');
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  const handleCancelDelete = () => {
    setShowConfirm(false);
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow ${
      isDeleting ? 'opacity-50 pointer-events-none' : ''
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 mb-1">
            📄 {batch.filename}
          </h3>
          <p className="text-sm text-gray-500">
            {formatDate(batch.upload_timestamp, 'datetime')}
          </p>
        </div>
        
        {/* Status Badge */}
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
          batch.status === 'completed' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-yellow-100 text-yellow-800'
        }`}>
          {batch.status === 'completed' ? '✅ Terminé' : '⏳ En cours'}
        </span>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-xs text-blue-600 font-medium mb-1">Total Clients</p>
          <p className="text-2xl font-bold text-blue-900">{batch.total_clients}</p>
        </div>

        <div className="bg-red-50 rounded-lg p-3">
          <p className="text-xs text-red-600 font-medium mb-1">Fraudeurs</p>
          <p className="text-2xl font-bold text-red-900">{batch.fraud_detected}</p>
        </div>

        <div className="bg-yellow-50 rounded-lg p-3">
          <p className="text-xs text-yellow-600 font-medium mb-1">Taux Fraude</p>
          <p className="text-2xl font-bold text-yellow-900">
            {formatPercentage(batch.fraud_percentage / 100)}
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 font-medium mb-1">Seuil</p>
          <p className="text-2xl font-bold text-gray-900">
            {batch.threshold_used || 0.5}
          </p>
        </div>
      </div>

      {/* Actions */}
      {!showConfirm ? (
        <div className="flex space-x-3">
          <button
            onClick={() => onViewDetails(batch.id)}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            disabled={isDeleting}
          >
            👁️ Voir Détails
          </button>
          
          <button
            onClick={() => window.open(`http://localhost:8000/api/predictions/batch/${batch.id}`, '_blank')}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            title="Voir JSON"
            disabled={isDeleting}
          >
            📋 API
          </button>

          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg font-medium hover:bg-red-200 transition-colors"
            title="Supprimer"
            disabled={isDeleting}
          >
            {isDeleting ? '⏳' : '🗑️'}
          </button>
        </div>
      ) : (
        /* Confirmation de suppression */
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
          <p className="text-sm font-semibold text-red-900 mb-3">
            ⚠️ Êtes-vous sûr de vouloir supprimer ce batch ?
          </p>
          <div className="flex space-x-3">
            <button
              onClick={handleDelete}
              className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors"
            >
              ✓ Oui, supprimer
            </button>
            <button
              onClick={handleCancelDelete}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              ✕ Annuler
            </button>
          </div>
        </div>
      )}

      {/* ID (pour debug) */}
      <p className="text-xs text-gray-400 mt-3 font-mono truncate">
        ID: {batch.id}
      </p>
    </div>
  );
};

export default BatchCard;