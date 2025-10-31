"""
Service de prédiction ML - Charge et utilise le modèle entraîné
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

from app.config import settings
from app.ml.preprocessing import FraudPreprocessor


class FraudPredictor:
    """
    Service de prédiction de fraude
    Charge le modèle et le scaler, fait des prédictions
    """
    
    def __init__(self):
        """Initialise le prédicteur"""
        self.model = None
        self.scaler = None
        self.preprocessor = FraudPreprocessor(min_days=settings.MIN_DATA_DAYS)
        self.is_loaded = False
        
    def load_models(self):
        """Charge le modèle ML et le scaler"""
        try:
            print(f"📦 Chargement du modèle depuis : {settings.MODEL_PATH}")
            self.model = joblib.load(settings.MODEL_PATH)
            
            print(f"📦 Chargement du scaler depuis : {settings.SCALER_PATH}")
            self.scaler = joblib.load(settings.SCALER_PATH)
            
            self.is_loaded = True
            print("✅ Modèles chargés avec succès !")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des modèles : {e}")
            raise
    
    def predict_batch(
        self, 
        df: pd.DataFrame, 
        threshold: float = None
    ) -> Dict:
        """
        Prédiction batch (plusieurs clients)
        
        Args:
            df: DataFrame avec colonnes [CONS_NO, date1, date2, ..., dateN]
            threshold: Seuil de décision (par défaut: settings.DEFAULT_THRESHOLD)
        
        Returns:
            Dictionnaire avec résultats de prédiction
        """
        if not self.is_loaded:
            self.load_models()
        
        threshold = threshold or settings.DEFAULT_THRESHOLD
        
        # 1. Préprocessing : données brutes → features
        features_df, metadata = self.preprocessor.transform(df)
        
        # 2. Prépare les features pour le modèle
        cons_nos = features_df['CONS_NO'].values
        X = features_df[self.preprocessor.feature_names].values
        
        # 3. Normalisation
        X_scaled = self.scaler.transform(X)
        
        # 4. Prédiction
        probabilities = self.model.predict_proba(X_scaled)[:, 1]  # Proba classe 1 (fraud)
        predictions = (probabilities >= threshold).astype(int)
        
        # 5. Calcule le niveau de qualité
        quality_level = self.preprocessor.get_quality_level(metadata['n_days'])
        
        # 6. Prépare les résultats
        results = []
        for i, cons_no in enumerate(cons_nos):
            result = {
                'cons_no': cons_no,
                'prediction': int(predictions[i]),
                'probability': float(probabilities[i]),
                'risk_level': self._get_risk_level(probabilities[i]),
                'threshold_used': threshold,
                'features': {
                    name: float(X[i, j]) 
                    for j, name in enumerate(self.preprocessor.feature_names)
                }
            }
            results.append(result)
        
        # 7. Statistiques globales
        fraud_count = int(predictions.sum())
        fraud_rate = fraud_count / len(predictions) if len(predictions) > 0 else 0
        
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': {
                'total_clients': len(df),
                'data_period_days': metadata['n_days'],
                'quality_level': quality_level,
                'threshold': threshold
            },
            'statistics': {
                'fraud_detected': fraud_count,
                'normal_detected': len(predictions) - fraud_count,
                'fraud_rate': round(fraud_rate * 100, 2)
            },
            'predictions': results
        }
        
        return response
    
    def predict_single(
        self, 
        cons_no: str, 
        consumption_data: List[float],
        threshold: float = None
    ) -> Dict:
        """
        Prédiction pour un seul client (temps réel)
        
        Args:
            cons_no: ID du client
            consumption_data: Liste de valeurs de consommation
            threshold: Seuil de décision
        
        Returns:
            Résultat de prédiction pour ce client
        """
        if not self.is_loaded:
            self.load_models()
        
        threshold = threshold or settings.DEFAULT_THRESHOLD
        
        # 1. Crée un DataFrame temporaire
        data = {'CONS_NO': [cons_no]}
        for i, value in enumerate(consumption_data):
            data[f'day_{i}'] = [value]
        
        df = pd.DataFrame(data)
        
        # 2. Utilise predict_batch
        batch_result = self.predict_batch(df, threshold)
        
        # 3. Retourne le résultat du seul client
        return batch_result['predictions'][0]
    
    def _get_risk_level(self, probability: float) -> str:
        """
        Détermine le niveau de risque selon la probabilité
        
        Returns:
            'low', 'medium', 'high', ou 'critical'
        """
        if probability < 0.3:
            return 'low'
        elif probability < 0.5:
            return 'medium'
        elif probability < 0.8:
            return 'high'
        else:
            return 'critical'
    
    def get_model_info(self) -> Dict:
        """Retourne les informations sur le modèle chargé"""
        if not self.is_loaded:
            return {'status': 'not_loaded'}
        
        return {
            'status': 'loaded',
            'model_type': type(self.model).__name__,
            'feature_names': self.preprocessor.feature_names,
            'n_features': len(self.preprocessor.feature_names),
            'default_threshold': settings.DEFAULT_THRESHOLD,
            'min_data_days': settings.MIN_DATA_DAYS
        }


# Instance globale (singleton)
predictor = FraudPredictor()