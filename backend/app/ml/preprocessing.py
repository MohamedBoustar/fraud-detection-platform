"""
Pipeline de preprocessing - Transforme données brutes → 15 features
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from scipy import stats

class FraudPreprocessor:
    """
    Transforme les données de consommation en features pour le modèle ML
    Accepte un nombre variable de jours de données (flexible)
    """
    
    def __init__(self, min_days: int = 7):
        """
        Args:
            min_days: Nombre minimum de jours requis
        """
        self.min_days = min_days
        self.feature_names = [
            'mean_consumption', 'std_consumption', 'median_consumption',
            'max_consumption', 'cv', 'zero_ratio', 'zero_days',
            'trend', 'n_peaks', 'max_consecutive_zeros',
            'skewness', 'kurtosis', 'q25', 'q75', 'iqr'
        ]
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, str, int]:
        """
        Valide le format des données
        
        Returns:
            (is_valid, message, n_days)
        """
        # Vérifie colonne CONS_NO
        if 'CONS_NO' not in df.columns:
            return False, "❌ Colonne 'CONS_NO' manquante", 0
        
        # Identifie colonnes de dates (toutes sauf CONS_NO et FLAG)
        date_columns = [col for col in df.columns if col not in ['CONS_NO', 'FLAG']]
        n_days = len(date_columns)
        
        # Vérifie minimum de jours
        if n_days < self.min_days:
            return False, f"❌ Minimum {self.min_days} jours requis, reçu : {n_days}", n_days
        
        # Vérifie doublons CONS_NO
        if df['CONS_NO'].duplicated().any():
            return False, "❌ CONS_NO contient des doublons", n_days
        
        return True, f"✅ Validation réussie : {n_days} jours de données", n_days
    
    def calculate_features(self, consumption_values: np.ndarray) -> Dict[str, float]:
        """
        Calcule les 15 features à partir d'un array de consommation
        
        Args:
            consumption_values: Array de valeurs de consommation (N jours)
        
        Returns:
            Dictionnaire avec 15 features
        """
        # Remplace NaN par 0
        values = np.nan_to_num(consumption_values, nan=0.0)
        
        # ===== GROUPE 1 : Statistiques de base =====
        mean_consumption = np.mean(values)
        std_consumption = np.std(values)
        median_consumption = np.median(values)
        max_consumption = np.max(values)
        
        # ===== GROUPE 2 : Métriques dérivées =====
        # Coefficient de variation (évite division par 0)
        cv = std_consumption / (mean_consumption + 1e-10)
        
        # ===== GROUPE 3 : Détection des zéros =====
        zero_days = np.sum(values == 0)
        zero_ratio = zero_days / len(values)
        
        # ===== GROUPE 4 : Analyse temporelle =====
        # Tendance (régression linéaire simple)
        x = np.arange(len(values))
        if len(values) > 1 and std_consumption > 0:
            trend = np.polyfit(x, values, 1)[0]  # Pente
        else:
            trend = 0.0
        
        # Nombre de pics (valeurs > mean + 2*std)
        threshold = mean_consumption + 2 * std_consumption
        n_peaks = np.sum(values > threshold)
        
        # Plus longue séquence de zéros consécutifs
        max_consecutive_zeros = self._max_consecutive_zeros(values)
        
        # ===== GROUPE 5 : Distribution =====
        # Gère les cas où tous les valeurs sont identiques
        if std_consumption > 1e-10:
            skewness = float(stats.skew(values))
            kurtosis = float(stats.kurtosis(values))
        else:
            skewness = 0.0
            kurtosis = 0.0
        
        # Quartiles
        q25 = np.percentile(values, 25)
        q75 = np.percentile(values, 75)
        iqr = q75 - q25
        
        return {
            'mean_consumption': mean_consumption,
            'std_consumption': std_consumption,
            'median_consumption': median_consumption,
            'max_consumption': max_consumption,
            'cv': cv,
            'zero_ratio': zero_ratio,
            'zero_days': zero_days,
            'trend': trend,
            'n_peaks': n_peaks,
            'max_consecutive_zeros': max_consecutive_zeros,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'q25': q25,
            'q75': q75,
            'iqr': iqr
        }
    
    def _max_consecutive_zeros(self, values: np.ndarray) -> int:
        """Calcule la plus longue séquence de 0 consécutifs"""
        max_count = 0
        current_count = 0
        
        for val in values:
            if val == 0:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Transforme le DataFrame complet en features
        
        Args:
            df: DataFrame avec colonnes [CONS_NO, date1, date2, ..., dateN]
        
        Returns:
            (features_df, metadata)
        """
        # Validation
        is_valid, message, n_days = self.validate_data(df)
        if not is_valid:
            raise ValueError(message)
        
        print(f"📊 Transformation de {len(df)} clients ({n_days} jours de données)...")
        
        # Identifie colonnes de dates
        date_columns = [col for col in df.columns if col not in ['CONS_NO', 'FLAG']]
        
        # Calcule features pour chaque client
        features_list = []
        
        for idx, row in df.iterrows():
            cons_no = row['CONS_NO']
            consumption_values = row[date_columns].values.astype(float)
            
            # Calcule les 15 features
            features = self.calculate_features(consumption_values)
            features['CONS_NO'] = cons_no
            
            # Ajoute FLAG si présente (pour validation)
            if 'FLAG' in df.columns:
                features['FLAG'] = row['FLAG']
            
            features_list.append(features)
        
        # Crée DataFrame
        features_df = pd.DataFrame(features_list)
        
        # Métadonnées
        metadata = {
            'n_clients': len(df),
            'n_days': n_days,
            'date_columns': date_columns,
            'validation_message': message
        }
        
        print(f"✅ Transformation terminée : {len(features_df)} clients → 15 features")
        
        return features_df, metadata
    
    def get_quality_level(self, n_days: int) -> str:
        """
        Détermine la qualité de l'analyse selon le nombre de jours
        
        Returns:
            'low', 'medium', 'high', ou 'excellent'
        """
        if n_days < 30:
            return 'low'
        elif n_days < 90:
            return 'medium'
        elif n_days < 365:
            return 'high'
        else:
            return 'excellent'