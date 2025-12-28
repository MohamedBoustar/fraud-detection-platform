/**
 * AlertNotification - Système de notifications en temps réel
 * Affiche les alertes de fraude avec toast notifications
 */

import React, { useState, useEffect } from 'react';
import useRealtimeData from '../../hooks/useRealtimeData';
import './AlertNotification.css';

const AlertNotification = () => {
  const realtime = useRealtimeData();
  const [alerts, setAlerts] = useState([]);
  const [lastPredictionId, setLastPredictionId] = useState(null);

  useEffect(() => {
    // Récupérer les nouvelles fraudes et les ajouter aux alertes
    realtime.predictions.forEach((pred) => {
      const predId = `${pred.meter_id}-${pred.fraud_probability}`;
      if (predId !== lastPredictionId && pred.is_fraud) {
        // Nouvelle fraude détectée
        addAlert({
          type: 'fraud',
          meter_id: pred.meter_id,
          score: (pred.fraud_probability * 100).toFixed(1),
          risk_level: pred.risk_level,
        });

        // Play sound if available
        playSound();

        // Send browser notification if permitted
        sendBrowserNotification(pred);

        setLastPredictionId(predId);
      }
    });
  }, [realtime.predictions, lastPredictionId]);

  const addAlert = (alert) => {
    const id = Date.now();
    const alertWithId = { ...alert, id };
    setAlerts((prev) => [alertWithId, ...prev].slice(0, 10)); // Max 10 alertes

    // Auto-remove after 5 seconds
    setTimeout(() => {
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    }, 5000);
  };

  const playSound = () => {
    // Utiliser Web Audio API pour un son court
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      // Beep rapide (600Hz)
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        audioContext.currentTime + 0.1
      );

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.1);
    } catch (e) {
      console.error('Audio notification error:', e);
    }
  };

  const sendBrowserNotification = (pred) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('FRAUDE DÉTECTÉE!', {
        body: `Compteur ${pred.meter_id}: Score ${(
          pred.fraud_probability * 100
        ).toFixed(1)}%`,
        icon: '/fraud-icon.png',
        tag: 'fraud-alert',
        requireInteraction: true,
      });
    }
  };

  return (
    <div className="alert-container">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`alert alert-${alert.type}`}
        >
          <div className="alert-content">
            <div className="alert-icon">!</div>
            <div className="alert-details">
              <h4>FRAUDE DÉTECTÉE</h4>
              <p>
                Compteur: <strong>{alert.meter_id}</strong>
              </p>
              <p>
                Score: <strong>{alert.score}%</strong>
              </p>
              <p>
                Risque: <strong>{alert.risk_level}</strong>
              </p>
            </div>
          </div>
          <button
            className="alert-close"
            onClick={() =>
              setAlerts((prev) => prev.filter((a) => a.id !== alert.id))
            }
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};

// Demander permission pour les notifications au premier lancement
if ('Notification' in window && Notification.permission === 'default') {
  Notification.requestPermission();
}

export default AlertNotification;
