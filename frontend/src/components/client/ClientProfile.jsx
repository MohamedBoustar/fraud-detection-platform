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
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
              <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Client : {client.cons_no || `Client ${client.index}`}
              </h2>
              <p className="text-gray-600 mt-1">
                Analyse de détection de fraude
              </p>
            </div>
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
            <div className="flex items-center space-x-2 mb-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <p className="text-sm text-blue-600 font-medium">
                Score de Risque
              </p>
            </div>
            <p className="text-3xl font-bold" style={{ color: predLabel.color }}>
              {formatPercentage(client.probability)}
            </p>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-gray-600 font-medium">
                Prédiction
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {client.prediction === 1 ? (
                <div className="inline-flex items-center">
                  <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span className="text-xl font-bold text-red-600 ml-2">
                    FRAUDEUR
                  </span>
                </div>
              ) : (
                <div className="inline-flex items-center">
                  <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-xl font-bold text-green-600 ml-2">
                    NORMAL
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              <p className="text-sm text-gray-600 font-medium">
                Seuil Utilisé
              </p>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {client.threshold_used || 0.5}
            </p>
          </div>
        </div>
      </div>

      {/* Anomalies Détectées */}
      {anomalies.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900">
              Anomalies Détectées
            </h3>
          </div>
          
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
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <svg className={`w-4 h-4 ${
                        anomaly.severity === 'high' ? 'text-red-600' : 'text-yellow-600'
                      }`} fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      <p className={`font-semibold ${
                        anomaly.severity === 'high' ? 'text-red-900' : 'text-yellow-900'
                      }`}>
                        {featureDescriptions[anomaly.feature]}
                      </p>
                    </div>
                    <p className={`text-sm ${
                      anomaly.severity === 'high' ? 'text-red-700' : 'text-yellow-700'
                    }`}>
                      {anomaly.message}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold flex-shrink-0 ml-3 ${
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
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900">
              Features Calculées (15)
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.keys(featureDescriptions).map((key) => (
              <div
                key={key}
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:border-blue-300 transition-colors"
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