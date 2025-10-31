"""
Routes API pour les prédictions de fraude
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
import pandas as pd
import io
import logging

from app.ml.predictor import predictor
from app.ml.preprocessing import FraudPreprocessor

logger = logging.getLogger(__name__)

# Créer le router
router = APIRouter()


# ========== HEALTH & INFO ENDPOINTS ==========

@router.get("/health")
async def health():
    """
    Vérifie l'état de santé du service de prédiction
    """
    return {
        "status": "healthy" if predictor.is_loaded else "unhealthy",
        "model_loaded": predictor.is_loaded,
        "service": "fraud-prediction"
    }


@router.get("/model/info")
async def get_model_info():
    """
    Retourne les informations sur le modèle ML chargé
    """
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    return predictor.get_model_info()


@router.get("/model/features")
async def get_features_info():
    """
    Liste les 15 features utilisées par le modèle
    """
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    preprocessor = FraudPreprocessor()
    
    return {
        "count": len(preprocessor.feature_names),
        "features": preprocessor.feature_names,
        "descriptions": {
            "mean_consumption": "Consommation moyenne (kWh/jour)",
            "std_consumption": "Écart-type de la consommation",
            "median_consumption": "Médiane de la consommation",
            "max_consumption": "Consommation maximale",
            "cv": "Coefficient de variation (std/mean)",
            "zero_ratio": "Proportion de jours à 0 kWh",
            "zero_days": "Nombre de jours à 0 kWh",
            "trend": "Tendance (pente régression linéaire)",
            "n_peaks": "Nombre de pics (> mean + 2*std)",
            "max_consecutive_zeros": "Plus longue séquence de 0",
            "skewness": "Asymétrie de la distribution",
            "kurtosis": "Aplatissement de la distribution",
            "q25": "1er quartile (25%)",
            "q75": "3ème quartile (75%)",
            "iqr": "Écart interquartile (Q75 - Q25)"
        }
    }


# ========== PREDICTION ENDPOINTS ==========

@router.post("/batch")
async def predict_batch(
    file: UploadFile = File(...),
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Seuil de décision (0-1)")
):
    """
    Prédiction batch : Upload un CSV et obtient les prédictions
    
    Format CSV attendu :
    - Colonne CONS_NO (obligatoire) : ID unique du client
    - Colonnes de dates (au moins 7) : consommation journalière en kWh
    
    Exemple :
    CONS_NO,2024-01-01,2024-01-02,2024-01-03,...
    CN_0001,12.5,15.3,8.2,...
    CN_0002,0.0,0.0,156.8,...
    """
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    # Vérifie le type de fichier
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés")
    
    try:
        # Lit le CSV
        logger.info(f"📤 Upload fichier : {file.filename}")
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        logger.info(f"📊 Fichier chargé : {len(df)} clients, {len(df.columns)} colonnes")
        
        # Préprocessing : transforme données brutes → 15 features
        preprocessor = FraudPreprocessor()
        features_df, metadata = preprocessor.transform(df)
        
        logger.info(f"✅ Preprocessing terminé : {len(features_df)} clients")
        
        # Prédictions
        results = predictor.predict_batch(features_df, threshold=threshold)
        
        # Statistiques
        fraud_count = sum(1 for r in results if r['prediction'] == 1)
        fraud_percentage = (fraud_count / len(results)) * 100 if results else 0
        
        logger.info(f"🎯 Prédictions : {fraud_count}/{len(results)} fraudeurs ({fraud_percentage:.1f}%)")
        
        return {
            "success": True,
            "filename": file.filename,
            "metadata": metadata,
            "summary": {
                "total_clients": len(results),
                "fraud_detected": fraud_count,
                "fraud_percentage": round(fraud_percentage, 2),
                "normal_count": len(results) - fraud_count
            },
            "predictions": results,
            "threshold_used": threshold or predictor.preprocessor.min_days
        }
        
    except ValueError as e:
        logger.error(f"❌ Erreur de validation : {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction batch : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


@router.post("/realtime")
async def predict_realtime(
    features: dict,
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0)
):
    """
    Prédiction en temps réel pour UN client
    
    Body JSON attendu (15 features) :
    {
        "mean_consumption": 10.5,
        "std_consumption": 5.2,
        "median_consumption": 8.3,
        "max_consumption": 50.0,
        "cv": 0.5,
        "zero_ratio": 0.2,
        "zero_days": 73,
        "trend": 0.01,
        "n_peaks": 5,
        "max_consecutive_zeros": 10,
        "skewness": 1.2,
        "kurtosis": 2.5,
        "q25": 3.0,
        "q75": 15.0,
        "iqr": 12.0
    }
    """
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    try:
        # Prédiction
        result = predictor.predict_single(features, threshold=threshold)
        
        logger.info(f"🎯 Prédiction temps réel : {result['label']} (prob={result['probability']:.3f})")
        
        return {
            "success": True,
            "result": result
        }
        
    except ValueError as e:
        logger.error(f"❌ Features invalides : {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"❌ Erreur prédiction temps réel : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")