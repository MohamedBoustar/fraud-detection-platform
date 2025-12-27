/**
 * Config.js - Configuration globale de l'application
 */

// Déterminer l'URL du WebSocket basée sur l'environnement
const getWebSocketURL = () => {
  if (import.meta.env.DEV) {
    // En développement, utiliser localhost
    return 'ws://localhost:8000/ws/realtime';
  } else {
    // En production, utiliser l'URL du serveur
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/ws/realtime`;
  }
};

// Déterminer l'URL de l'API REST
const getAPIURL = () => {
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  } else {
    return window.location.origin;
  }
};

export const config = {
  WEBSOCKET_URL: getWebSocketURL(),
  API_URL: getAPIURL(),
  RECONNECT_INTERVAL: 3000, // 3 secondes
  MAX_RECONNECT_ATTEMPTS: 5,
  KEEP_ALIVE_INTERVAL: 30000, // 30 secondes
  MESSAGE_HISTORY_SIZE: 100,
  CHART_LIMIT: 30,
};

export default config;
