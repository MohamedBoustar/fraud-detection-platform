"""
Routes API pour les prédictions de fraude
Avec intégration base de données PostgreSQL
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
import logging
import os

from app.ml.predictor import predictor
from app.ml.preprocessing import FraudPreprocessor
from app.database import get_db
from app.services import db_service
from app.services.cloud_storage import s3_service
from app.config import settings

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
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Seuil de décision (0-1)"),
    db: Session = Depends(get_db)
):
    """
    Prédiction batch : Upload un CSV et obtient les prédictions
    ⭐ NOUVEAU : Sauvegarde automatiquement dans PostgreSQL + AWS S3
    
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
        file_size_mb = len(contents) / (1024 * 1024)
        
        # ⭐ NOUVEAU : Upload vers S3 si activé
        s3_file_key = None
        s3_file_url = None
        
        if settings.USE_S3_STORAGE and s3_service:
            try:
                logger.info(f"☁️ Upload vers S3 : {file.filename}")
                s3_file_key = s3_service.upload_file(contents, file.filename)
                
                if s3_file_key:
                    # Génère URL présignée valide 7 jours
                    s3_file_url = s3_service.generate_presigned_url(s3_file_key, expiration=604800)
                    logger.info(f"✅ Fichier uploadé vers S3 : {s3_file_key}")
                else:
                    logger.warning(f"⚠️ Échec upload S3 pour {file.filename}")
                    
            except Exception as s3_error:
                logger.error(f"❌ Erreur S3 : {s3_error}")
                # Continue même si S3 échoue
        
        # Parse le CSV
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
        
        # ⭐ NOUVEAU : Sauvegarde dans la base de données AVEC S3
        batch_id = None
        try:
            # Prépare les données avec features
            predictions_data = []
            for result in results:
                # Récupère les features depuis features_df
                cons_no = result.get('cons_no', result.get('index'))
                feature_row = features_df[features_df['CONS_NO'] == cons_no].iloc[0] if 'CONS_NO' in features_df.columns else None
                
                pred_dict = {
                    'cons_no': cons_no,
                    'prediction': result['prediction'],
                    'probability': result['probability'],
                    'risk_level': result['risk_level']
                }
                
                # Ajoute les 15 features
                if feature_row is not None:
                    for feature in preprocessor.feature_names:
                        if feature in feature_row:
                            pred_dict[feature] = float(feature_row[feature])
                
                predictions_data.append(pred_dict)
            
            # Sauvegarde le batch complet (AVEC s3_file_key et s3_file_url)
            batch_id = db_service.save_batch_predictions(
                db=db,
                filename=file.filename,
                file_size_mb=file_size_mb,
                predictions_data=predictions_data,
                threshold_used=threshold if threshold else 0.5,
                data_period_days=metadata.get('data_days'),
                s3_file_key=s3_file_key,  # ⭐ NOUVEAU
                s3_file_url=s3_file_url   # ⭐ NOUVEAU
            )
            
            logger.info(f"💾 Batch sauvegardé en DB avec ID : {batch_id}")
            
        except Exception as db_error:
            logger.error(f"❌ Erreur sauvegarde DB : {db_error}")
            # Continue même si la sauvegarde échoue
        
        return {
            "success": True,
            "filename": file.filename,
            "batch_id": batch_id,
            "saved_to_db": batch_id is not None,
            "s3_uploaded": s3_file_key is not None,  # ⭐ NOUVEAU
            "s3_file_key": s3_file_key,              # ⭐ NOUVEAU
            "s3_file_url": s3_file_url,              # ⭐ NOUVEAU
            "metadata": metadata,
            "summary": {
                "total_clients": len(results),
                "fraud_detected": fraud_count,
                "fraud_percentage": round(fraud_percentage, 2),
                "normal_count": len(results) - fraud_count
            },
            "predictions": results,
            "threshold_used": threshold if threshold else 0.5
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
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Prédiction en temps réel pour UN client
    ⭐ NOUVEAU : Sauvegarde automatiquement dans PostgreSQL
    
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
        
        # ⭐ NOUVEAU : Sauvegarde dans la base de données
        try:
            cons_no = features.get('cons_no', f"REALTIME_{result.get('timestamp', 'unknown')}")
            
            # Récupère ou crée le client
            client = db_service.get_or_create_client(db, cons_no)
            
            # Crée la prédiction
            db_service.create_prediction(
                db=db,
                client_id=client.id,
                prediction=result['prediction'],
                probability=result['probability'],
                risk_level=result['risk_level'],
                threshold_used=threshold if threshold else 0.5,
                source="realtime",
                features=features
            )
            
            logger.info(f"💾 Prédiction realtime sauvegardée pour {cons_no}")
            result['saved_to_db'] = True
            
        except Exception as db_error:
            logger.error(f"❌ Erreur sauvegarde DB : {db_error}")
            result['saved_to_db'] = False
        
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


# ========== NOUVEAUX ENDPOINTS - BASE DE DONNÉES ==========

@router.get("/history/{cons_no}")
async def get_client_history(
    cons_no: str,
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique complet des prédictions d'un client
    """
    history = db_service.get_client_history(db, cons_no)
    
    if not history:
        raise HTTPException(status_code=404, detail=f"Client {cons_no} non trouvé")
    
    return history


@router.get("/batch/{batch_id}")
async def get_batch_details(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'un batch et toutes ses prédictions
    """
    batch = db_service.get_batch_by_id(db, batch_id)
    
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} non trouvé")
    
    predictions = db_service.get_predictions_by_batch(db, batch_id)
    
    return {
        "batch": {
            "id": batch.id,
            "filename": batch.filename,
            "file_size_mb": batch.file_size_mb,
            "upload_timestamp": batch.upload_timestamp,
            "total_clients": batch.total_clients,
            "fraud_detected": batch.fraud_detected,
            "fraud_percentage": batch.fraud_percentage,
            "threshold_used": batch.threshold_used,
            "status": batch.status
        },
        "predictions": [
            {
                "cons_no": p.client.cons_no,
                "prediction": p.prediction,
                "probability": p.probability,
                "risk_level": p.risk_level,
                "created_at": p.created_at
            }
            for p in predictions
        ]
    }


@router.get("/batches")
async def list_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Liste tous les batches uploadés (avec pagination)
    """
    batches = db_service.get_all_batches(db, skip=skip, limit=limit)
    
    return {
        "total": len(batches),
        "skip": skip,
        "limit": limit,
        "batches": [
            {
                "id": b.id,
                "filename": b.filename,
                "upload_timestamp": b.upload_timestamp,
                "total_clients": b.total_clients,
                "fraud_detected": b.fraud_detected,
                "fraud_percentage": b.fraud_percentage,
                "status": b.status
            }
            for b in batches
        ]
    }


@router.get("/stats")
async def get_global_statistics(db: Session = Depends(get_db)):
    """
    Récupère les statistiques globales de la plateforme
    """
    return db_service.get_global_stats(db)

@router.delete("/batch/{batch_id}")
async def delete_batch(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Supprime un batch et toutes ses prédictions associées
    """
    batch = db_service.get_batch_by_id(db, batch_id)
    
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} non trouvé")
    
    try:
        # Supprime le batch (les prédictions seront supprimées en cascade)
        db.delete(batch)
        db.commit()
        
        logger.info(f"🗑️ Batch supprimé : {batch.filename} (ID: {batch_id})")
        
        return {
            "success": True,
            "message": f"Batch {batch.filename} supprimé avec succès",
            "batch_id": batch_id
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur suppression batch : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression : {str(e)}")