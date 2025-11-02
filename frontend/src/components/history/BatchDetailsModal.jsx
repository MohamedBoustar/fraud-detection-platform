/**
 * Composant BatchDetailsModal - Modal avec détails d'un batch
 */
import React from 'react';
import RiskBadge from '../common/RiskBadge';
import { formatDate, formatPredictionLabel, formatNumber } from '../../utils/formatters';

const BatchDetailsModal = ({ batch, predictions, onClose }) => {
  if (!batch) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">
                📄 {batch.filename}
              </h2>
              <p className="text-blue-100">
                Uploadé le {formatDate(batch.upload_timestamp, 'datetime')}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-3xl leading-none"
            >
              ×
            </button>
          </div>
        </div>

        {/* Stats Résumées */}
        <div className="grid grid-cols-4 gap-4 p-6 border-b">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Total</p>
            <p className="text-3xl font-bold text-blue-600">{batch.total_clients}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Fraudeurs</p>
            <p className="text-3xl font-bold text-red-600">{batch.fraud_detected}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Normaux</p>
            <p className="text-3xl font-bold text-green-600">
              {batch.total_clients - batch.fraud_detected}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Taux</p>
            <p className="text-3xl font-bold text-yellow-600">
              {formatNumber(batch.fraud_percentage, 1)}%
            </p>
          </div>
        </div>

        {/* Liste des Prédictions */}
        <div className="flex-1 overflow-y-auto p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            📋 Prédictions ({predictions?.length || 0})
          </h3>

          {predictions && predictions.length > 0 ? (
            <div className="space-y-3">
              {predictions.map((pred, index) => {
                const predLabel = formatPredictionLabel(pred.prediction);
                
                return (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 mb-1">
                          {pred.cons_no}
                        </p>
                        <p className="text-sm text-gray-600">
                          {formatDate(pred.created_at, 'datetime')}
                        </p>
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="text-sm text-gray-600 mb-1">Score</p>
                          <p className="text-lg font-bold" style={{ color: predLabel.color }}>
                            {formatNumber(pred.probability * 100, 1)}%
                          </p>
                        </div>

                        <span
                          className="px-4 py-2 rounded-full font-semibold text-sm"
                          style={{
                            backgroundColor: predLabel.bgColor,
                            color: predLabel.color,
                          }}
                        >
                          {predLabel.icon} {predLabel.text}
                        </span>

                        <RiskBadge riskLevel={pred.risk_level} size="sm" />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">
              Aucune prédiction disponible
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};

export default BatchDetailsModal;