"""
ML Predictor Service - Charge et utilise le modèle ML
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, List
import logging

from app.config import settings
from app.ml.preprocessing import FraudPreprocessor

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FraudPredictor:
    """
    Service de prédiction de fraude
    Charge le modèle LightGBM et le scaler au démarrage
    """
    
    def __init__(self):
        """Initialise le prédicteur (sans charger les modèles)"""
        self.model = None
        self.scaler = None
        self.preprocessor = FraudPreprocessor(min_days=settings.MIN_DATA_DAYS)
        self.is_loaded = False
        
    def load_models(self) -> bool:
        """
        Charge le modèle ML et le scaler depuis les fichiers .pkl
        
        Returns:
            bool: True si chargement réussi, False sinon
        """
        try:
            logger.info("🔄 Chargement du modèle ML...")
            
            # Vérifie que les fichiers existent
            if not settings.MODEL_PATH.exists():
                logger.error(f"❌ Modèle introuvable : {settings.MODEL_PATH}")
                return False
            
            if not settings.SCALER_PATH.exists():
                logger.error(f"❌ Scaler introuvable : {settings.SCALER_PATH}")
                return False
            
            # Charge le modèle
            self.model = joblib.load(settings.MODEL_PATH)
            logger.info(f"✅ Modèle chargé : {type(self.model).__name__}")
            
            # Charge le scaler
            self.scaler = joblib.load(settings.SCALER_PATH)
            logger.info(f"✅ Scaler chargé : {type(self.scaler).__name__}")
            
            self.is_loaded = True
            logger.info("🎉 Modèles ML chargés avec succès !")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des modèles : {e}")
            self.is_loaded = False
            return False
    
    def predict_single(
    self, 
    features: Dict[str, float], 
    threshold: float = None
) -> Dict:
     if not self.is_loaded:
        raise RuntimeError("Modèles non chargés. Appelez load_models() d'abord.")
    
     if threshold is None:
        threshold = settings.DEFAULT_THRESHOLD
    
     try:
        # Vérifie que toutes les features sont présentes
        expected_features = self.preprocessor.feature_names
        missing = set(expected_features) - set(features.keys())
        if missing:
            raise ValueError(f"Features manquantes : {missing}")
        
        # ⭐ IMPORTANT : Crée un array numpy dans le BON ORDRE
        # Au lieu d'un DataFrame qui peut mélanger l'ordre
        features_array = np.array([[features[f] for f in expected_features]])
        
        # Applique le scaler
        features_scaled = self.scaler.transform(features_array)
        
        # Prédiction
        probability = self.model.predict_proba(features_scaled)[0, 1]  # Proba classe 1 (fraude)
        prediction = int(probability >= threshold)
        
        # Détermine le niveau de risque
        risk_level = self._get_risk_level(probability)
        
        return {
            "prediction": prediction,
            "probability": float(probability),
            "risk_level": risk_level,
            "threshold_used": threshold,
            "label": "FRAUD" if prediction == 1 else "NORMAL"
        }
        
     except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction : {e}")
        raise
    
    def predict_batch(
        self, 
        features_df: pd.DataFrame, 
        threshold: float = None
    ) -> List[Dict]:
        """
        Fait des prédictions pour PLUSIEURS clients
        
        Args:
            features_df: DataFrame avec colonnes = 15 features, lignes = clients
            threshold: Seuil de décision
        
        Returns:
            Liste de dictionnaires avec résultats pour chaque client
        """
        if not self.is_loaded:
            raise RuntimeError("Modèles non chargés. Appelez load_models() d'abord.")
        
        if threshold is None:
            threshold = settings.DEFAULT_THRESHOLD
        
        try:
            logger.info(f"📊 Prédiction batch pour {len(features_df)} clients...")
            
            # Extrait CONS_NO si présent
            cons_no_col = None
            if 'CONS_NO' in features_df.columns:
                cons_no_col = features_df['CONS_NO'].values
                features_only = features_df.drop('CONS_NO', axis=1)
            else:
                features_only = features_df
            
            # Vérifie les colonnes
            # ⭐ Vérifie et réordonne les colonnes selon le scaler
            if hasattr(self.scaler, 'feature_names_in_'):
              expected_order = list(self.scaler.feature_names_in_)
            else:
              expected_order = self.preprocessor.feature_names

            # Réordonne les features
            features_only = features_only[expected_order]
            
            # Applique le scaler
            features_scaled = self.scaler.transform(features_only)
            
            # Prédictions
            probabilities = self.model.predict_proba(features_scaled)[:, 1]
            predictions = (probabilities >= threshold).astype(int)
            
            # Construit les résultats
            results = []
            for idx in range(len(features_df)):
                result = {
                    "index": idx,
                    "prediction": int(predictions[idx]),
                    "probability": float(probabilities[idx]),
                    "risk_level": self._get_risk_level(probabilities[idx]),
                    "threshold_used": threshold,
                    "label": "FRAUD" if predictions[idx] == 1 else "NORMAL"
                }
                
                # Ajoute CONS_NO si disponible
                if cons_no_col is not None:
                    result["cons_no"] = str(cons_no_col[idx])
                
                results.append(result)
            
            logger.info(f"✅ {len(results)} prédictions effectuées")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur batch prediction : {e}")
            raise
    
    def _get_risk_level(self, probability: float) -> str:
        """
        Détermine le niveau de risque selon la probabilité
        
        Args:
            probability: Probabilité de fraude (0-1)
        
        Returns:
            'LOW', 'MEDIUM', 'HIGH', ou 'CRITICAL'
        """
        if probability < 0.3:
            return "LOW"
        elif probability < 0.5:
            return "MEDIUM"
        elif probability < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def predict_realtime(self, iot_data: Dict[str, float], threshold: float = None) -> Dict:
        """
        Prédiction temps réel à partir de données IoT instantanées
        Génère des features statistiques simulées basées sur les valeurs capteur
        
        Args:
            iot_data: Données IoT (consumption_kw, voltage_v, current_a, etc.)
            threshold: Seuil de classification
            
        Returns:
            Dict avec is_fraud, fraud_probability, risk_level
        """
        try:
            consumption = iot_data.get("consumption_kw", 5.0)
            voltage = iot_data.get("voltage_v", 230.0)
            power_factor = iot_data.get("power_factor", 0.95)
            anomaly_score = iot_data.get("anomaly_score", 0.0)
            
            # Générer des features statistiques simulées basées sur les valeurs IoT
            # La logique : des valeurs anormales → features anormales
            
            base_mean = consumption
            
            # Détection d'anomalies basée sur les valeurs IoT
            voltage_anomaly = abs(voltage - 230) / 230  # Écart par rapport à 230V
            pf_anomaly = max(0, 0.95 - power_factor)  # Power factor trop bas
            
            # Score d'anomalie combiné
            combined_anomaly = anomaly_score + voltage_anomaly + pf_anomaly
            
            # Générer les 15 features statistiques
            features = {
                'mean_consumption': base_mean,
                'std_consumption': base_mean * (0.1 + combined_anomaly * 0.5),
                'median_consumption': base_mean * (0.95 + combined_anomaly * 0.1),
                'max_consumption': base_mean * (1.5 + combined_anomaly * 2),
                'cv': 0.15 + combined_anomaly * 0.8,  # Coefficient de variation
                'zero_ratio': combined_anomaly * 0.3,  # Ratio de zéros suspect
                'zero_days': int(combined_anomaly * 10),
                'trend': combined_anomaly * 0.5 - 0.1,  # Tendance
                'n_peaks': int(2 + combined_anomaly * 5),  # Nombre de pics
                'max_consecutive_zeros': int(combined_anomaly * 5),
                'skewness': combined_anomaly * 2,
                'kurtosis': combined_anomaly * 3,
                'q25': base_mean * 0.75,
                'q75': base_mean * 1.25,
                'iqr': base_mean * 0.5
            }
            
            # Utiliser predict_single avec les features générées
            result = self.predict_single(features, threshold)
            
            return {
                "is_fraud": result.get("prediction") == 1,
                "fraud_probability": result.get("probability", 0.0),
                "risk_level": result.get("risk_level", "UNKNOWN"),
                "threshold_used": result.get("threshold_used"),
                "label": result.get("label", "UNKNOWN"),
                "source": "realtime",
                "features": features  # Inclure les features générées
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur predict_realtime: {e}")
            return None

    def predict(self, features: Dict[str, float], threshold: float = None) -> Dict:
        """
        Prédiction intelligente - détecte automatiquement le type de données
        
        Args:
            features: Dict des features (IoT ou statistiques)
            threshold: Seuil de classification
            
        Returns:
            Dict avec is_fraud, fraud_probability, risk_level
        """
        try:
            # Détecter si c'est des données IoT ou des features statistiques
            iot_keys = {'consumption_kw', 'voltage_v', 'current_a', 'power_factor'}
            stat_keys = {'mean_consumption', 'std_consumption', 'median_consumption'}
            
            has_iot = any(k in features for k in iot_keys)
            has_stats = any(k in features for k in stat_keys)
            
            if has_iot and not has_stats:
                # Données IoT → utiliser predict_realtime
                return self.predict_realtime(features, threshold)
            else:
                # Features statistiques → utiliser predict_single
                result = self.predict_single(features, threshold)
                return {
                    "is_fraud": result.get("prediction") == 1,
                    "fraud_probability": result.get("probability", 0.0),
                    "risk_level": result.get("risk_level", "UNKNOWN"),
                    "threshold_used": result.get("threshold_used"),
                    "label": result.get("label", "UNKNOWN")
                }
        except Exception as e:
            logger.error(f"❌ Erreur predict: {e}")
            return None
    
    def get_model_info(self) -> Dict:
        """
        Retourne les informations sur le modèle chargé
        
        Returns:
            Dict avec type de modèle, features, etc.
        """
        if not self.is_loaded:
            return {"error": "Modèles non chargés"}
        
        return {
            "model_type": type(self.model).__name__,
            "scaler_type": type(self.scaler).__name__,
            "n_features": len(self.preprocessor.feature_names),
            "features": self.preprocessor.feature_names,
            "default_threshold": settings.DEFAULT_THRESHOLD,
            "min_data_days": settings.MIN_DATA_DAYS
        }


# Instance globale (singleton)
predictor = FraudPredictor()