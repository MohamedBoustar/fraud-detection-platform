/**
 * Composant ClientProfile - Profil détaillé d'un client
 */
import React from 'react';
import RiskBadge from '../common/RiskBadge';
import { formatPredictionLabel, formatNumber, formatPercentage } from '../../utils/formatters';

const ClientProfile = ({ client, features }) => {
  const predLabel = formatPredictionLabel(client.prediction);

  // Features avec descriptions
  const featureDescriptions = {
    mean_consumption: 'Consommation moyenne (kWh/jour)',
    std_consumption: 'Écart-type de consommation',
    median_consumption: 'Médiane de consommation',
    max_consumption: 'Consommation maximale',
    cv: 'Coefficient de variation',
    zero_ratio: 'Proportion de jours à 0 kWh',
    zero_days: 'Nombre de jours à 0 kWh',
    trend: 'Tendance (évolution)',
    n_peaks: 'Nombre de pics anormaux',
    max_consecutive_zeros: 'Plus longue séquence de 0',
    skewness: 'Asymétrie de distribution',
    kurtosis: 'Aplatissement de distribution',
    q25: '1er quartile (25%)',
    q75: '3ème quartile (75%)',
    iqr: 'Écart interquartile'
  };

  // Détecte les features anormales (valeurs suspectes)
  const detectAnomalies = () => {
    if (!features) return [];
    
    const anomalies = [];

    // Zero ratio élevé
    if (features.zero_ratio > 0.5) {
      anomalies.push({
        feature: 'zero_ratio',
        value: features.zero_ratio,
        severity: 'high',
        message: `${formatPercentage(features.zero_ratio)} des jours à 0 kWh (suspect !)`
      });
    }

    // Longue séquence de zéros
    if (features.max_consecutive_zeros > 30) {
      anomalies.push({
        feature: 'max_consecutive_zeros',
        value: features.max_consecutive_zeros,
        severity: 'high',
        message: `${features.max_consecutive_zeros} jours consécutifs à 0 (très suspect !)`
      });
    }

    // Tendance négative (consommation diminue)
    if (features.trend < -0.01) {
      anomalies.push({
        feature: 'trend',
        value: features.trend,
        severity: 'medium',
        message: 'Consommation en baisse continue (anormal)'
      });
    }

    // Peu de pics (compteur bloqué ?)
    if (features.n_peaks < 2) {
      anomalies.push({
        feature: 'n_peaks',
        value: features.n_peaks,
        severity: 'medium',
        message: 'Très peu de variations (compteur suspect ?)'
      });
    }

    // CV très élevé (comportement erratique)
    if (features.cv > 2) {
      anomalies.push({
        feature: 'cv',
        value: features.cv,
        severity: 'medium',
        message: 'Variations extrêmes (comportement erratique)'
      });
    }

    return anomalies;
  };

  const anomalies = detectAnomalies();

  return (
    <div className="space-y-6">
      {/* Header - Informations Principales */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Client : {client.cons_no || `Client ${client.index}`}
            </h2>
            <p className="text-gray-600">
              Analyse de détection de fraude
            </p>
          </div>
          
          <RiskBadge 
            riskLevel={client.risk_level} 
            probability={client.probability}
            size="lg"
          />
        </div>

        {/* Score et Prédiction */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-600 font-medium mb-1">
              Score de Risque
            </p>
            <p className="text-3xl font-bold" style={{ color: predLabel.color }}>
              {formatPercentage(client.probability)}
            </p>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 font-medium mb-1">
              Prédiction
            </p>
            <div className="flex items-center space-x-2">
              <span className="text-2xl">{predLabel.icon}</span>
              <span className="text-xl font-bold" style={{ color: predLabel.color }}>
                {predLabel.text}
              </span>
            </div>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 font-medium mb-1">
              Seuil Utilisé
            </p>
            <p className="text-3xl font-bold text-gray-900">
              {client.threshold_used || 0.5}
            </p>
          </div>
        </div>
      </div>

      {/* Anomalies Détectées */}
      {anomalies.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            🚨 Anomalies Détectées
          </h3>
          
          <div className="space-y-3">
            {anomalies.map((anomaly, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  anomaly.severity === 'high'
                    ? 'bg-red-50 border-red-500'
                    : 'bg-yellow-50 border-yellow-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className={`font-semibold ${
                      anomaly.severity === 'high' ? 'text-red-900' : 'text-yellow-900'
                    }`}>
                      {featureDescriptions[anomaly.feature]}
                    </p>
                    <p className={`text-sm ${
                      anomaly.severity === 'high' ? 'text-red-700' : 'text-yellow-700'
                    }`}>
                      {anomaly.message}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    anomaly.severity === 'high'
                      ? 'bg-red-200 text-red-900'
                      : 'bg-yellow-200 text-yellow-900'
                  }`}>
                    {anomaly.severity === 'high' ? 'CRITIQUE' : 'ATTENTION'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Features Complètes */}
      {features && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            📊 Features Calculées (15)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.keys(featureDescriptions).map((key) => (
              <div
                key={key}
                className="bg-gray-50 border border-gray-200 rounded-lg p-3"
              >
                <p className="text-xs text-gray-600 mb-1">
                  {featureDescriptions[key]}
                </p>
                <p className="text-lg font-bold text-gray-900">
                  {formatNumber(features[key], 2)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientProfile;