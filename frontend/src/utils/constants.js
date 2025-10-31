/**
 * Constantes globales de l'application
 */

// ========== COULEURS ==========
export const COLORS = {
  // Statuts de prédiction
  fraud: '#EF4444',      // Rouge pour fraudeurs
  normal: '#10B981',     // Vert pour normaux
  suspect: '#F59E0B',    // Orange pour suspects
  
  // Niveaux de risque
  riskLow: '#10B981',       // Vert
  riskMedium: '#F59E0B',    // Orange
  riskHigh: '#EF4444',      // Rouge
  riskCritical: '#DC2626',  // Rouge foncé
  
  // UI
  primary: '#3B82F6',    // Bleu
  secondary: '#6B7280',  // Gris
  background: '#F9FAFB', // Gris très clair
  text: '#111827',       // Noir
  border: '#E5E7EB',     // Gris clair
};

// ========== SEUILS ==========
export const THRESHOLDS = {
  default: 0.5,          // Seuil par défaut
  conservative: 0.7,     // Seuil conservateur (moins de faux positifs)
  aggressive: 0.3,       // Seuil agressif (détecte plus de fraudeurs)
  
  // Niveaux de risque
  riskLow: 0.3,
  riskMedium: 0.5,
  riskHigh: 0.8,
};

// ========== LABELS ==========
export const LABELS = {
  prediction: {
    0: 'Normal',
    1: 'Fraudeur',
  },
  
  riskLevel: {
    LOW: 'Faible',
    MEDIUM: 'Moyen',
    HIGH: 'Élevé',
    CRITICAL: 'Critique',
  },
};

// ========== MESSAGES ==========
export const MESSAGES = {
  errors: {
    apiDown: "Impossible de contacter l'API. Vérifiez que le serveur est démarré.",
    modelNotLoaded: "Le modèle ML n'est pas chargé. Contactez l'administrateur.",
    invalidFile: "Fichier invalide. Seuls les fichiers CSV sont acceptés.",
    uploadFailed: "Échec de l'upload. Vérifiez votre fichier et réessayez.",
    predictionFailed: "Erreur lors de la prédiction. Réessayez.",
  },
  
  success: {
    uploadSuccess: "Fichier uploadé avec succès !",
    predictionComplete: "Prédictions terminées !",
  },
  
  info: {
    processing: "Traitement en cours...",
    analyzing: "Analyse des données...",
    minDataDays: "Minimum 7 jours de données requis par client.",
  },
};

// ========== CONFIGURATION CSV ==========
export const CSV_CONFIG = {
  maxSizeMB: 100,        // Taille maximale du fichier (MB)
  requiredColumns: ['CONS_NO'],  // Colonnes obligatoires
  minDays: 7,            // Nombre minimum de jours de données
  acceptedExtensions: ['.csv'],
};

// ========== FEATURES ==========
export const FEATURES = [
  'mean_consumption',
  'std_consumption',
  'median_consumption',
  'max_consumption',
  'cv',
  'zero_ratio',
  'zero_days',
  'trend',
  'n_peaks',
  'max_consecutive_zeros',
  'skewness',
  'kurtosis',
  'q25',
  'q75',
  'iqr',
];

// ========== ROUTES ==========
export const ROUTES = {
  home: '/',
  batch: '/batch',
  realtime: '/realtime',
  client: '/client/:id',
  history: '/history',
  dashboard: '/dashboard',
};