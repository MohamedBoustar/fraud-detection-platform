/**
 * Service API - Configuration Axios et fonctions d'appel
 */
import axios from 'axios';

// URL de base de l'API (depuis variables d'environnement)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Instance Axios configurée
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 secondes
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur de requêtes (pour ajouter des logs, tokens, etc.)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Intercepteur de réponses (pour gérer les erreurs globalement)
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ========== FONCTIONS API ==========

/**
 * Health check de l'API
 */
export const checkApiHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Health check du service de prédiction
 */
export const checkPredictionHealth = async () => {
  const response = await apiClient.get('/api/predictions/health');
  return response.data;
};

/**
 * Récupère les informations du modèle ML
 */
export const getModelInfo = async () => {
  const response = await apiClient.get('/api/predictions/model/info');
  return response.data;
};

/**
 * Récupère la liste des features et leurs descriptions
 */
export const getFeaturesInfo = async () => {
  const response = await apiClient.get('/api/predictions/model/features');
  return response.data;
};

/**
 * Upload CSV et obtient les prédictions (batch)
 * 
 * @param {File} file - Fichier CSV
 * @param {number} threshold - Seuil de décision (optionnel, 0-1)
 * @returns {Promise} Résultats des prédictions
 */
export const predictBatch = async (file, threshold = null) => {
  const formData = new FormData();
  formData.append('file', file);

  const url = threshold !== null 
    ? `/api/predictions/batch?threshold=${threshold}`
    : '/api/predictions/batch';

  const response = await apiClient.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Prédiction en temps réel pour un client
 * 
 * @param {Object} features - Objet avec les 15 features
 * @param {number} threshold - Seuil de décision (optionnel)
 * @returns {Promise} Résultat de la prédiction
 */
export const predictRealtime = async (features, threshold = null) => {
  const url = threshold !== null
    ? `/api/predictions/realtime?threshold=${threshold}`
    : '/api/predictions/realtime';

  const response = await apiClient.post(url, features);
  return response.data;
};

/**
 * Récupère les informations générales de l'API
 */
export const getApiInfo = async () => {
  const response = await apiClient.get('/');
  return response.data;
};

// Exporte aussi l'instance Axios pour des cas d'usage avancés
export default apiClient;