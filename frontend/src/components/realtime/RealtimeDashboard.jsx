/**
 * RealtimeDashboard - Dashboard des prédictions temps réel
 * Affiche les prédictions en direct avec alertes
 */

import React, { useState } from 'react';
import useRealtimeData from '../../hooks/useRealtimeData';
import RiskBadge from '../common/RiskBadge';
import LoadingSpinner from '../common/LoadingSpinner';
import RealtimeChart from './RealtimeChart';
import './RealtimeDashboard.css';

const RealtimeDashboard = () => {
  const realtime = useRealtimeData();
  const [filterFraud, setFilterFraud] = useState(null); // null = all, true = fraude, false = normal

  // Filtrer les prédictions
  const filteredPredictions = realtime.predictions.filter((p) => {
    if (filterFraud === null) return true;
    return p.is_fraud === filterFraud;
  });

  // Déterminer la couleur du statut de connexion
  const statusColor = realtime.isConnected ? 'green' : 'red';

  return (
    <div className="realtime-dashboard">
      {/* Header */}
      <div className="realtime-header">
        <div className="header-left">
          <h1>📊 Dashboard Temps Réel</h1>
          <p>Prédictions de fraude en direct</p>
        </div>

        <div className="header-right">
          {/* Statut de connexion */}
          <div className="connection-status">
            <div
              className="status-indicator"
              style={{ backgroundColor: statusColor }}
            />
            <span>
              {realtime.isConnected ? '🟢 Connecté' : '🔴 Déconnecté'}
            </span>
          </div>

          {/* Client ID */}
          {realtime.clientId && (
            <div className="client-info">
              <small>Client ID: {realtime.clientId.substring(0, 8)}...</small>
            </div>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{realtime.predictions.length}</div>
          <div className="stat-label">Prédictions reçues</div>
        </div>

        <div className="stat-card fraud">
          <div className="stat-value">{realtime.fraudCount}</div>
          <div className="stat-label">🚨 Fraudes détectées</div>
        </div>

        <div className="stat-card normal">
          <div className="stat-value">{realtime.normalCount}</div>
          <div className="stat-label">✅ Normal</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{realtime.avgScore}</div>
          <div className="stat-label">Score moyen</div>
        </div>
      </div>

      {/* Erreur */}
      {realtime.error && (
        <div className="error-banner">
          <span>❌ {realtime.error}</span>
          <button onClick={realtime.connect}>Reconnecter</button>
        </div>
      )}

      {/* Filtres */}
      <div className="filters">
        <button
          className={`filter-btn ${filterFraud === null ? 'active' : ''}`}
          onClick={() => setFilterFraud(null)}
        >
          Tous ({realtime.predictions.length})
        </button>
        <button
          className={`filter-btn fraud ${filterFraud === true ? 'active' : ''}`}
          onClick={() => setFilterFraud(true)}
        >
          🚨 Fraudes ({realtime.fraudCount})
        </button>
        <button
          className={`filter-btn normal ${filterFraud === false ? 'active' : ''}`}
          onClick={() => setFilterFraud(false)}
        >
          ✅ Normal ({realtime.normalCount})
        </button>
      </div>

      {/* Section Graphiques */}
      <div className="charts-section">
        <h2>📈 Analyse Graphique</h2>
        <RealtimeChart type="line" limit={30} />
        <RealtimeChart type="bar" limit={20} />
      </div>

      {/* Liste des prédictions */}
      <div className="predictions-container">
        {filteredPredictions.length === 0 ? (
          <div className="empty-state">
            <LoadingSpinner />
            <p>En attente des prédictions...</p>
          </div>
        ) : (
          <div className="predictions-list">
            {filteredPredictions.map((pred, idx) => (
              <div
                key={idx}
                className={`prediction-card ${
                  pred.is_fraud ? 'fraud' : 'normal'
                }`}
              >
                {/* Alerte fraude */}
                {pred.is_fraud && (
                  <div className="fraud-alert">
                    🚨 FRAUDE DÉTECTÉE
                  </div>
                )}

                {/* Contenu */}
                <div className="prediction-content">
                  {/* Gauche - Info compteur */}
                  <div className="prediction-info">
                    <div className="meter-id">
                      📊 {pred.meter_id}
                    </div>
                    <div className="timestamp">
                      {new Date(pred.timestamp).toLocaleTimeString('fr-FR')}
                    </div>
                    <div className="consumption">
                      ⚡ {pred.consumption_kw?.toFixed(2)}kW
                    </div>
                  </div>

                  {/* Centre - Scores */}
                  <div className="prediction-scores">
                    <div className="score-row">
                      <span>Score fraude:</span>
                      <strong>{(pred.fraud_probability * 100).toFixed(1)}%</strong>
                    </div>
                    <div className="score-bar">
                      <div
                        className="score-fill"
                        style={{
                          width: `${pred.fraud_probability * 100}%`,
                          backgroundColor: pred.is_fraud ? '#ef4444' : '#10b981',
                        }}
                      />
                    </div>
                  </div>

                  {/* Droite - Badge */}
                  <div className="prediction-badge">
                    <RiskBadge
                      riskLevel={pred.risk_level || 'MINIMAL'}
                      score={pred.fraud_probability}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer - Stats serveur */}
      {realtime.stats && (
        <div className="server-stats">
          <small>
            🖥️ Clients connectés: {realtime.stats.connected_clients} | 
            Messages: {realtime.stats.messages_sent} | 
            Pic: {realtime.stats.peak_clients}
          </small>
        </div>
      )}
    </div>
  );
};

export default RealtimeDashboard;
