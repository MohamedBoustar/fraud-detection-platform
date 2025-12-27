/**
 * Hook React pour les données temps réel (WebSocket)
 * Gère la connexion, reconnexion, et mise à jour des prédictions
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import config from '../config';

const useRealtimeData = (url = null) => {
  const finalUrl = url || config.WEBSOCKET_URL;
  // État
  const [isConnected, setIsConnected] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [clientId, setClientId] = useState(null);

  // Refs
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 secondes

  // Connecter au WebSocket
  const connect = useCallback(() => {
    try {
      console.log('🔗 Connexion WebSocket...', finalUrl);

      const ws = new WebSocket(finalUrl);

      ws.onopen = () => {
        console.log('✅ WebSocket connecté');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.debug('📨 Message reçu:', message.type);

          if (message.type === 'welcome') {
            // Message de bienvenue
            setClientId(message.client_id);
            setStats(message.stats);
            
            // Charger l'historique
            if (message.history) {
              setPredictions(message.history.reverse());
            }
          } else if (message.type === 'prediction') {
            // Nouvelle prédiction
            setPredictions((prev) => {
              const newPredictions = [message, ...prev];
              // Garder seulement les 100 derniers
              return newPredictions.slice(0, 100);
            });

            // Mettre à jour stats
            if (message.is_fraud) {
              console.warn('🚨 FRAUDE DÉTECTÉE:', message.meter_id);
            }
          } else if (message.type === 'stats') {
            // Mise à jour stats
            setStats(message.data);
          } else if (message.type === 'pong') {
            // Keep-alive
            console.debug('💓 Keep-alive');
          }
        } catch (e) {
          console.error('❌ Erreur parsing message:', e);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ Erreur WebSocket:', error);
        setError('Erreur WebSocket');
      };

      ws.onclose = () => {
        console.log('👋 WebSocket fermé');
        setIsConnected(false);
        wsRef.current = null;

        // Tenter de reconnecter
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          console.log(
            `⏱️ Reconnexion dans ${reconnectDelay / 1000}s (tentative ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, config.RECONNECT_INTERVAL);
        } else {
          setError('Impossible de se connecter au serveur');
        }
      };

      wsRef.current = ws;
    } catch (e) {
      console.error('❌ Erreur connexion:', e);
      setError('Erreur connexion WebSocket');
    }
  }, [url]);

  // Déconnecter
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    setIsConnected(false);
  }, []);

  // Envoyer un message au serveur
  const send = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    } else {
      console.warn('⚠️ WebSocket non connecté');
    }
  }, []);

  // Ping keep-alive
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      send('ping');
    }, 30000); // Ping tous les 30 secondes

    return () => clearInterval(interval);
  }, [isConnected, send]);

  // Connexion initiale
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect, finalUrl]);

  // Ajouter une prédiction manuellement
  const addPrediction = useCallback((prediction) => {
    setPredictions((prev) => [prediction, ...prev].slice(0, 100));
  }, []);

  // Effacer l'historique
  const clearPredictions = useCallback(() => {
    setPredictions([]);
  }, []);

  // Obtenir les stats
  const requestStats = useCallback(() => {
    send('stats');
  }, [send]);

  return {
    // État
    isConnected,
    predictions,
    stats,
    error,
    clientId,

    // Méthodes
    connect,
    disconnect,
    send,
    addPrediction,
    clearPredictions,
    requestStats,

    // Computed
    fraudCount: predictions.filter((p) => p.is_fraud).length,
    normalCount: predictions.filter((p) => !p.is_fraud).length,
    avgScore:
      predictions.length > 0
        ? (
            predictions.reduce((sum, p) => sum + (p.fraud_probability || 0), 0) /
            predictions.length
          ).toFixed(3)
        : 0,
  };
};

export default useRealtimeData;
