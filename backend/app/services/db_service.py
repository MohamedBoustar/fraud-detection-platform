"""
Service de gestion de la base de données
CRUD operations pour les prédictions
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.models.db_models import Client, Prediction, BatchUpload, RawFeature, PredictionSourceEnum
from app.database import get_db

logger = logging.getLogger(__name__)


# ========== CLIENTS ==========

def get_or_create_client(db: Session, cons_no: str) -> Client:
    """
    Récupère un client existant ou en crée un nouveau
    """
    client = db.query(Client).filter(Client.cons_no == cons_no).first()
    
    if not client:
        client = Client(cons_no=cons_no)
        db.add(client)
        db.commit()
        db.refresh(client)
        logger.info(f"✅ Nouveau client créé : {cons_no}")
    else:
        # Met à jour date_last_seen
        client.date_last_seen = func.now()
        db.commit()
    
    return client


def update_client_stats(db: Session, client_id: str, prediction: int, probability: float):
    """
    Met à jour les statistiques d'un client après une prédiction
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if client:
        client.total_predictions += 1
        if prediction == 1:
            client.fraud_count += 1
        client.latest_score = probability
        client.latest_prediction = prediction
        db.commit()
        logger.debug(f"📊 Stats client mises à jour : {client.cons_no}")


def get_client_by_cons_no(db: Session, cons_no: str) -> Optional[Client]:
    """
    Récupère un client par son CONS_NO
    """
    return db.query(Client).filter(Client.cons_no == cons_no).first()


def get_all_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """
    Récupère tous les clients (avec pagination)
    """
    return db.query(Client).offset(skip).limit(limit).all()


# ========== BATCH UPLOADS ==========

def create_batch_upload(
    db: Session,
    filename: str,
    file_size_mb: float,
    total_clients: int,
    fraud_detected: int,
    fraud_percentage: float,
    threshold_used: float,
    data_period_days: Optional[int] = None,
    s3_file_key: Optional[str] = None,     # ⭐ AJOUTÉ
    s3_file_url: Optional[str] = None      # ⭐ AJOUTÉ
) -> BatchUpload:
    """
    Crée un enregistrement de batch upload
    """
    batch = BatchUpload(
        filename=filename,
        file_size_mb=file_size_mb,
        s3_file_key=s3_file_key,      # ⭐ AJOUTÉ
        s3_file_url=s3_file_url,      # ⭐ AJOUTÉ
        total_clients=total_clients,
        fraud_detected=fraud_detected,
        fraud_percentage=fraud_percentage,
        threshold_used=threshold_used,
        data_period_days=data_period_days,
        status="completed"
    )
    
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    logger.info(f"✅ Batch upload créé : {filename} ({total_clients} clients)")
    return batch


def get_batch_by_id(db: Session, batch_id: str) -> Optional[BatchUpload]:
    """
    Récupère un batch par son ID
    """
    return db.query(BatchUpload).filter(BatchUpload.id == batch_id).first()


def get_all_batches(db: Session, skip: int = 0, limit: int = 50) -> List[BatchUpload]:
    """
    Récupère tous les batches (avec pagination, tri par date desc)
    """
    return db.query(BatchUpload).order_by(desc(BatchUpload.upload_timestamp)).offset(skip).limit(limit).all()


# ========== PREDICTIONS ==========

def create_prediction(
    db: Session,
    client_id: str,
    prediction: int,
    probability: float,
    risk_level: str,
    threshold_used: float,
    source: str = "batch",
    batch_id: Optional[str] = None,
    data_period_days: Optional[int] = None,
    features: Optional[Dict[str, float]] = None
) -> Prediction:
    """
    Crée une prédiction et optionnellement les features associées
    """
    # Crée la prédiction
    pred = Prediction(
        client_id=client_id,
        prediction=prediction,
        probability=probability,
        risk_level=risk_level,
        threshold_used=threshold_used,
        source=PredictionSourceEnum.BATCH if source == "batch" else PredictionSourceEnum.REALTIME,
        batch_id=batch_id,
        data_period_days=data_period_days
    )
    
    db.add(pred)
    db.commit()
    db.refresh(pred)
    
    # Crée les features si fournies
    if features:
        raw_feature = RawFeature(
            prediction_id=pred.id,
            client_id=client_id,
            **features
        )
        db.add(raw_feature)
        db.commit()
    
    # Met à jour les stats du client
    update_client_stats(db, client_id, prediction, probability)
    
    return pred


def get_predictions_by_client(db: Session, cons_no: str, limit: int = 10) -> List[Prediction]:
    """
    Récupère l'historique des prédictions d'un client
    """
    client = get_client_by_cons_no(db, cons_no)
    if not client:
        return []
    
    return db.query(Prediction).filter(
        Prediction.client_id == client.id
    ).order_by(desc(Prediction.created_at)).limit(limit).all()


def get_predictions_by_batch(db: Session, batch_id: str) -> List[Prediction]:
    """
    Récupère toutes les prédictions d'un batch
    """
    return db.query(Prediction).filter(Prediction.batch_id == batch_id).all()


def get_all_predictions(db: Session, skip: int = 0, limit: int = 100) -> List[Prediction]:
    """
    Récupère toutes les prédictions (avec pagination)
    """
    return db.query(Prediction).order_by(desc(Prediction.created_at)).offset(skip).limit(limit).all()


# ========== STATISTIQUES ==========

def get_global_stats(db: Session) -> Dict[str, Any]:
    """
    Récupère les statistiques globales
    """
    total_clients = db.query(func.count(Client.id)).scalar()
    total_predictions = db.query(func.count(Prediction.id)).scalar()
    total_frauds = db.query(func.count(Prediction.id)).filter(Prediction.prediction == 1).scalar()
    total_batches = db.query(func.count(BatchUpload.id)).scalar()
    
    fraud_percentage = (total_frauds / total_predictions * 100) if total_predictions > 0 else 0
    
    return {
        "total_clients": total_clients,
        "total_predictions": total_predictions,
        "total_frauds": total_frauds,
        "fraud_percentage": round(fraud_percentage, 2),
        "total_batches": total_batches
    }


def get_client_history(db: Session, cons_no: str) -> Optional[Dict[str, Any]]:
    """
    Récupère l'historique complet d'un client avec ses prédictions
    """
    client = get_client_by_cons_no(db, cons_no)
    if not client:
        return None
    
    predictions = get_predictions_by_client(db, cons_no, limit=50)
    
    return {
        "client": {
            "cons_no": client.cons_no,
            "date_first_seen": client.date_first_seen,
            "date_last_seen": client.date_last_seen,
            "total_predictions": client.total_predictions,
            "fraud_count": client.fraud_count,
            "latest_score": client.latest_score,
            "latest_prediction": client.latest_prediction
        },
        "predictions": [
            {
                "id": p.id,
                "prediction": p.prediction,
                "probability": p.probability,
                "risk_level": p.risk_level,
                "source": p.source.value,
                "created_at": p.created_at
            }
            for p in predictions
        ]
    }


# ========== SAUVEGARDE BATCH ==========

def save_batch_predictions(
    db: Session,
    filename: str,
    file_size_mb: float,
    predictions_data: list,
    threshold_used: float,
    data_period_days: Optional[int] = None,
    s3_file_key: Optional[str] = None,     # ⭐ AJOUTÉ
    s3_file_url: Optional[str] = None      # ⭐ AJOUTÉ
) -> str:
    """
    Sauvegarde un batch complet de prédictions
    
    Args:
        db: Session de base de données
        filename: Nom du fichier CSV
        file_size_mb: Taille du fichier
        predictions_data: Liste des prédictions avec features
        threshold_used: Seuil utilisé
        data_period_days: Nombre de jours de données
        s3_file_key: Chemin du fichier dans S3
        s3_file_url: URL présignée du fichier
        
    Returns:
        batch_id: ID du batch créé
    """
    # Calcule les statistiques
    total_clients = len(predictions_data)
    fraud_detected = sum(1 for p in predictions_data if p['prediction'] == 1)
    fraud_percentage = (fraud_detected / total_clients * 100) if total_clients > 0 else 0
    
    # Crée le batch
    batch = create_batch_upload(
        db=db,
        filename=filename,
        file_size_mb=file_size_mb,
        total_clients=total_clients,
        fraud_detected=fraud_detected,
        fraud_percentage=fraud_percentage,
        threshold_used=threshold_used,
        data_period_days=data_period_days,
        s3_file_key=s3_file_key,      # ⭐ AJOUTÉ
        s3_file_url=s3_file_url       # ⭐ AJOUTÉ
    )
    
    # Sauvegarde chaque prédiction
    for pred_data in predictions_data:
        # Récupère ou crée le client
        client = get_or_create_client(db, pred_data['cons_no'])
        
        # Extrait les features (si présentes)
        features = {
            'mean_consumption': pred_data.get('mean_consumption'),
            'std_consumption': pred_data.get('std_consumption'),
            'median_consumption': pred_data.get('median_consumption'),
            'max_consumption': pred_data.get('max_consumption'),
            'cv': pred_data.get('cv'),
            'zero_ratio': pred_data.get('zero_ratio'),
            'zero_days': pred_data.get('zero_days'),
            'trend': pred_data.get('trend'),
            'n_peaks': pred_data.get('n_peaks'),
            'max_consecutive_zeros': pred_data.get('max_consecutive_zeros'),
            'skewness': pred_data.get('skewness'),
            'kurtosis': pred_data.get('kurtosis'),
            'q25': pred_data.get('q25'),
            'q75': pred_data.get('q75'),
            'iqr': pred_data.get('iqr')
        } if all(k in pred_data for k in ['mean_consumption', 'std_consumption']) else None
        
        # Crée la prédiction
        create_prediction(
            db=db,
            client_id=client.id,
            prediction=pred_data['prediction'],
            probability=pred_data['probability'],
            risk_level=pred_data['risk_level'],
            threshold_used=threshold_used,
            source="batch",
            batch_id=batch.id,
            data_period_days=data_period_days,
            features=features
        )
    
    logger.info(f"✅ Batch {batch.id} sauvegardé : {total_clients} prédictions")
    return batch.id