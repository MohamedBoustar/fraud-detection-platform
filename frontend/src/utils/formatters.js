/**
 * Fonctions utilitaires de formatage
 */

/**
 * Formate un nombre avec des décimales
 * @param {number} value - Valeur à formater
 * @param {number} decimals - Nombre de décimales (défaut: 2)
 * @returns {string} Valeur formatée
 */
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  return Number(value).toFixed(decimals);
};

/**
 * Formate un pourcentage
 * @param {number} value - Valeur entre 0 et 1 (ou 0-100)
 * @param {number} decimals - Nombre de décimales
 * @returns {string} Pourcentage formaté (ex: "75.5%")
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  
  // Si la valeur est entre 0 et 1, multiplie par 100
  const percentage = value <= 1 ? value * 100 : value;
  return `${formatNumber(percentage, decimals)}%`;
};

/**
 * Formate une probabilité (0-1) en pourcentage avec couleur
 * @param {number} probability - Probabilité (0-1)
 * @returns {Object} { text, color }
 */
export const formatProbability = (probability) => {
  const percentage = formatPercentage(probability);
  
  let color = '#10B981'; // Vert par défaut
  if (probability >= 0.8) color = '#DC2626'; // Rouge critique
  else if (probability >= 0.5) color = '#EF4444'; // Rouge
  else if (probability >= 0.3) color = '#F59E0B'; // Orange
  
  return { text: percentage, color };
};

/**
 * Formate une date
 * @param {string|Date} date - Date à formater
 * @param {string} format - Format ('short', 'long', 'datetime')
 * @returns {string} Date formatée
 */
export const formatDate = (date, format = 'short') => {
  if (!date) return 'N/A';
  
  const d = new Date(date);
  
  if (isNaN(d.getTime())) return 'Date invalide';
  
  const options = {
    short: { year: 'numeric', month: '2-digit', day: '2-digit' },
    long: { year: 'numeric', month: 'long', day: 'numeric' },
    datetime: { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    },
  };
  
  return d.toLocaleDateString('fr-FR', options[format] || options.short);
};

/**
 * Formate un temps relatif (ex: "il y a 2 heures")
 * @param {string|Date} date - Date
 * @returns {string} Temps relatif
 */
export const formatRelativeTime = (date) => {
  if (!date) return 'N/A';
  
  const d = new Date(date);
  const now = new Date();
  const diffMs = now - d;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  
  if (diffSec < 60) return 'À l\'instant';
  if (diffMin < 60) return `Il y a ${diffMin} min`;
  if (diffHour < 24) return `Il y a ${diffHour}h`;
  if (diffDay < 30) return `Il y a ${diffDay}j`;
  
  return formatDate(date);
};

/**
 * Formate la taille d'un fichier
 * @param {number} bytes - Taille en bytes
 * @returns {string} Taille formatée (ex: "1.5 MB")
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${formatNumber(bytes / Math.pow(k, i), 1)} ${units[i]}`;
};

/**
 * Formate un niveau de risque avec icône
 * @param {string} riskLevel - 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
 * @returns {Object} { text, color, icon }
 */
export const formatRiskLevel = (riskLevel) => {
  const levels = {
    LOW: { text: 'Faible', color: '#10B981', icon: '' },
    MEDIUM: { text: 'Moyen', color: '#F59E0B', icon: '' },
    HIGH: { text: 'Élevé', color: '#EF4444', icon: '' },
    CRITICAL: { text: 'Critique', color: '#DC2626', icon: '' },
  };
  
  return levels[riskLevel] || levels.LOW;
};

/**
 * Formate un ID client (tronque si trop long)
 * @param {string} consNo - ID client
 * @param {number} maxLength - Longueur max
 * @returns {string} ID formaté
 */
export const formatClientId = (consNo, maxLength = 20) => {
  if (!consNo) return 'N/A';
  if (consNo.length <= maxLength) return consNo;
  return `${consNo.substring(0, maxLength)}...`;
};

/**
 * Formate un label de prédiction
 * @param {number} prediction - 0 ou 1
 * @returns {Object} { text, color, icon }
 */
export const formatPredictionLabel = (prediction) => {
  if (prediction === 1) {
    return {
      text: 'FRAUDEUR',
      color: '#EF4444',
      icon: '',
      bgColor: '#FEE2E2',
    };
  }
  
  return {
    text: 'NORMAL',
    color: '#10B981',
    icon: '',
    bgColor: '#D1FAE5',
  };
};