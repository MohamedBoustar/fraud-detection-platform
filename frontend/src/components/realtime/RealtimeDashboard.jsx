/**
 * RealtimeDashboard - Dashboard des prédictions temps réel
 * Affiche les données et prédictions de manière claire et visuelle
 */

import React, { useState } from 'react';
import useRealtimeData from '../../hooks/useRealtimeData';
import './RealtimeDashboard.css';

const RealtimeDashboard = () => {
  const realtime = useRealtimeData();
  const [filterFraud, setFilterFraud] = useState(null);

  // Filtrer les prédictions
  const filteredPredictions = realtime.predictions.filter((p) => {
    if (filterFraud === null) return true;
    return p.is_fraud === filterFraud;
  });

  // Formater le timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '--:--:--';
    return new Date(timestamp).toLocaleTimeString('fr-FR');
  };

  return (
    <div className="realtime-dashboard">
      {/* Header */}
      <div className="realtime-header">
        <div className="header-left">
          <h1>Détection Temps Réel</h1>
          <p>Surveillance des compteurs électriques</p>
        </div>

        <div className={`connection-badge ${realtime.isConnected ? 'connected' : 'disconnected'}`}>
          <span className="pulse"></span>
          {realtime.isConnected ? 'CONNECTÉ' : 'DÉCONNECTÉ'}
        </div>
      </div>

      {/* Stats principales */}
      <div className="main-stats">
        <div className="stat-box total">
          <div className="stat-number">{realtime.predictions.length}</div>
          <div className="stat-text">PRÉDICTIONS</div>
        </div>
        <div className="stat-box fraud">
          <div className="stat-number">{realtime.fraudCount}</div>
          <div className="stat-text">FRAUDES</div>
        </div>
        <div className="stat-box normal">
          <div className="stat-number">{realtime.normalCount}</div>
          <div className="stat-text">NORMAUX</div>
        </div>
        <div className="stat-box avg">
          <div className="stat-number">{realtime.avgScore}%</div>
          <div className="stat-text">SCORE MOYEN</div>
        </div>
      </div>

      {/* Filtres */}
      <div className="filter-buttons">
        <button
          className={filterFraud === null ? 'active' : ''}
          onClick={() => setFilterFraud(null)}
        >
          Tous ({realtime.predictions.length})
        </button>
        <button
          className={`fraud-btn ${filterFraud === true ? 'active' : ''}`}
          onClick={() => setFilterFraud(true)}
        >
          Fraudes ({realtime.fraudCount})
        </button>
        <button
          className={`normal-btn ${filterFraud === false ? 'active' : ''}`}
          onClick={() => setFilterFraud(false)}
        >
          Normaux ({realtime.normalCount})
        </button>
      </div>

      {/* Tableau des prédictions */}
      <div className="predictions-table-container">
        {filteredPredictions.length === 0 ? (
          <div className="waiting-state">
            <div className="spinner"></div>
            <p>En attente des données des capteurs...</p>
            <small>Le simulateur envoie des données automatiquement</small>
          </div>
        ) : (
          <table className="predictions-table">
            <thead>
              <tr>
                <th>STATUT</th>
                <th>COMPTEUR</th>
                <th>HEURE</th>
                <th>CONSOMMATION</th>
                <th>SCORE FRAUDE</th>
                <th>RISQUE</th>
              </tr>
            </thead>
            <tbody>
              {filteredPredictions.slice(0, 50).map((pred, idx) => (
                <tr key={idx} className={pred.is_fraud ? 'fraud-row' : 'normal-row'}>
                  <td className="status-cell">
                    {pred.is_fraud ? (
                      <span className="status-fraud">FRAUDE</span>
                    ) : (
                      <span className="status-normal">OK</span>
                    )}
                  </td>
                  <td className="meter-cell">
                    <strong>{pred.meter_id}</strong>
                  </td>
                  <td className="time-cell">
                    {formatTime(pred.timestamp)}
                  </td>
                  <td className="consumption-cell">
                    <span className={pred.consumption_kw > 100 ? 'high-value' : ''}>
                      {pred.consumption_kw?.toFixed(1)} kW
                    </span>
                  </td>
                  <td className="score-cell">
                    <div className="score-bar-container">
                      <div 
                        className="score-bar-fill"
                        style={{
                          width: `${pred.fraud_probability * 100}%`,
                          backgroundColor: pred.fraud_probability > 0.5 ? '#ef4444' : 
                                          pred.fraud_probability > 0.3 ? '#f59e0b' : '#10b981'
                        }}
                      ></div>
                      <span className="score-text">
                        {(pred.fraud_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="risk-cell">
                    <span className={`risk-badge ${pred.risk_level?.toLowerCase()}`}>
                      {pred.risk_level || 'N/A'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Dernière fraude détectée */}
      {realtime.fraudCount > 0 && (
        <div className="last-fraud-alert">
          <h3>Dernière Fraude Détectée</h3>
          {(() => {
            const lastFraud = realtime.predictions.find(p => p.is_fraud);
            if (!lastFraud) return null;
            return (
              <div className="fraud-details">
                <div className="fraud-detail">
                  <span>Compteur:</span>
                  <strong>{lastFraud.meter_id}</strong>
                </div>
                <div className="fraud-detail">
                  <span>Consommation:</span>
                  <strong>{lastFraud.consumption_kw?.toFixed(1)} kW</strong>
                </div>
                <div className="fraud-detail">
                  <span>Score:</span>
                  <strong className="fraud-score">{(lastFraud.fraud_probability * 100).toFixed(0)}%</strong>
                </div>
                <div className="fraud-detail">
                  <span>Heure:</span>
                  <strong>{formatTime(lastFraud.timestamp)}</strong>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Footer */}
      <div className="dashboard-footer">
        <span>{realtime.stats?.connected_clients || 0} clients</span>
        <span>{realtime.stats?.messages_sent || 0} messages</span>
        <span>Mise à jour en temps réel</span>
      </div>
    </div>
  );
};

export default RealtimeDashboard;
