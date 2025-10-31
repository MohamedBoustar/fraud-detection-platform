"""
Endpoints pour les prédictions de fraude
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import pandas as pd
import io
from datetime import datetime

from app.ml.predictor import predictor

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/health")
async def health_check():
    """Vérifie que l'API et le modèle sont opérationnels"""
    try:
        model_info = predictor.get_model_info()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "model": model_info
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@router.post("/batch")
async def predict_batch(
    file: UploadFile = File(...),
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Seuil de décision (0-1)")
):
    """
    Prédiction batch - Upload d'un fichier CSV
    
    Le CSV doit contenir :
    - Colonne CONS_NO (obligatoire)
    - Colonnes de dates avec valeurs de consommation
    - Minimum 7 jours de données
    
    Args:
        file: Fichier CSV uploadé
        threshold: Seuil de décision (défaut: 0.5)
    
    Returns:
        Résultats de prédiction pour tous les clients
    """
    # Validation du fichier
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="Format invalide. Seuls les fichiers CSV sont acceptés."
        )
    
    try:
        # Lecture du CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validation basique
        if df.empty:
            raise HTTPException(status_code=400, detail="Le fichier CSV est vide")
        
        if 'CONS_NO' not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail="Colonne 'CONS_NO' manquante dans le CSV"
            )
        
        # Prédiction
        result = predictor.predict_batch(df, threshold=threshold)
        
        # Ajoute info sur le fichier
        result['file_info'] = {
            'filename': file.filename,
            'size_mb': len(contents) / (1024 * 1024),
            'upload_timestamp': datetime.utcnow().isoformat()
        }
        
        return result
        
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400, 
            detail="Erreur de parsing CSV. Vérifiez le format du fichier."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


@router.post("/realtime")
async def predict_realtime(
    cons_no: str,
    consumption_data: List[float],
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0)
):
    """
    Prédiction en temps réel pour un seul client
    
    Args:
        cons_no: ID du client
        consumption_data: Liste de valeurs de consommation (min 7 jours)
        threshold: Seuil de décision
    
    Returns:
        Résultat de prédiction pour ce client
    """
    # Validation
    if len(consumption_data) < 7:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum 7 jours de données requis. Reçu : {len(consumption_data)}"
        )
    
    try:
        # Prédiction
        result = predictor.predict_single(cons_no, consumption_data, threshold)
        
        return {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'result': result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@router.get("/model/info")
async def get_model_info():
    """Retourne les informations sur le modèle ML chargé"""
    return predictor.get_model_info()


@router.get("/model/features")
async def get_features_info():
    """Liste les 15 features utilisées par le modèle"""
    return {
        "features": predictor.preprocessor.feature_names,
        "descriptions": {
            "mean_consumption": "Consommation moyenne (kWh/jour)",
            "std_consumption": "Écart-type de la consommation",
            "median_consumption": "Consommation médiane",
            "max_consumption": "Consommation maximale",
            "cv": "Coefficient de variation (std/mean)",
            "zero_ratio": "Proportion de jours à 0 kWh",
            "zero_days": "Nombre de jours à 0 kWh",
            "trend": "Tendance temporelle (pente régression)",
            "n_peaks": "Nombre de pics (> mean + 2*std)",
            "max_consecutive_zeros": "Plus longue séquence de 0",
            "skewness": "Asymétrie de la distribution",
            "kurtosis": "Aplatissement de la distribution",
            "q25": "1er quartile (25%)",
            "q75": "3ème quartile (75%)",
            "iqr": "Écart interquartile (Q75 - Q25)"
        }
    }