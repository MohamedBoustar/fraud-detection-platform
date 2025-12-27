"""
Modèles de base de données SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class PredictionSourceEnum(str, enum.Enum):
    """Type de source de prédiction"""
    BATCH = "batch"
    REALTIME = "realtime"


class FeedbackTypeEnum(str, enum.Enum):
    """Type de feedback"""
    CONFIRMED_FRAUD = "confirmed_fraud"
    FALSE_POSITIVE = "false_positive"
    UNCERTAIN = "uncertain"


# ========== TABLE 1 : CLIENTS ==========
class Client(Base):
    """
    Table des clients analysés
    """
    __tablename__ = "clients"
    
    # Clé primaire
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informations client
    cons_no = Column(String, unique=True, nullable=False, index=True)
    
    # Dates
    date_first_seen = Column(DateTime, default=func.now())
    date_last_seen = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Statistiques
    total_predictions = Column(Integer, default=0)
    fraud_count = Column(Integer, default=0)
    latest_score = Column(Float, nullable=True)
    latest_prediction = Column(Integer, nullable=True)
    
    # Métadonnées
    data_period_days = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relations
    predictions = relationship("Prediction", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client {self.cons_no}>"


# ========== TABLE 2 : PREDICTIONS ==========
class Prediction(Base):
    """
    Table de l'historique des prédictions
    """
    __tablename__ = "predictions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clé étrangère
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Résultats
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    threshold_used = Column(Float, nullable=False)
    
    # Métadonnées
    source = Column(Enum(PredictionSourceEnum), nullable=False)
    batch_id = Column(String, ForeignKey("batch_uploads.id"), nullable=True, index=True)
    data_period_days = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relations
    client = relationship("Client", back_populates="predictions")
    batch = relationship("BatchUpload", back_populates="predictions")
    feedbacks = relationship("Feedback", back_populates="prediction", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prediction {self.id}>"


# ========== TABLE 3 : BATCH UPLOADS ==========
# ========== TABLE 3 : BATCH UPLOADS ==========
class BatchUpload(Base):
    """
    Table des uploads batch
    """
    __tablename__ = "batch_uploads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informations fichier
    filename = Column(String, nullable=False)
    file_size_mb = Column(Float, nullable=True)
    
    # AWS S3 Storage (nouvelles colonnes)
    s3_file_key = Column(String, nullable=True)  # Chemin dans S3
    s3_file_url = Column(Text, nullable=True)    # URL présignée
    
    # Statistiques
    total_clients = Column(Integer, nullable=False)
    fraud_detected = Column(Integer, nullable=False)
    fraud_percentage = Column(Float, nullable=False)
    data_period_days = Column(Integer, nullable=True)
    
    # Métadonnées
    threshold_used = Column(Float, nullable=False)
    status = Column(String, default="completed")
    
    # Timestamp
    upload_timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relations
    predictions = relationship("Prediction", back_populates="batch")
    
    def __repr__(self):
        return f"<BatchUpload {self.filename}>"

# ========== TABLE 4 : FEEDBACKS ==========
class Feedback(Base):
    """
    Table des feedbacks sur les prédictions
    """
    __tablename__ = "feedbacks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clés étrangères
    prediction_id = Column(String, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    # Feedback
    feedback_type = Column(Enum(FeedbackTypeEnum), nullable=False)
    comment = Column(Text, nullable=True)
    provided_by = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now())
    
    # Relations
    prediction = relationship("Prediction", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback {self.feedback_type}>"


# ========== TABLE 5 : RAW FEATURES ==========
class RawFeature(Base):
    """
    Table pour stocker les 15 features calculées
    """
    __tablename__ = "raw_features"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Clés étrangères
    prediction_id = Column(String, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, unique=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    # 15 Features
    mean_consumption = Column(Float, nullable=False)
    std_consumption = Column(Float, nullable=False)
    median_consumption = Column(Float, nullable=False)
    max_consumption = Column(Float, nullable=False)
    cv = Column(Float, nullable=False)
    zero_ratio = Column(Float, nullable=False)
    zero_days = Column(Integer, nullable=False)
    trend = Column(Float, nullable=False)
    n_peaks = Column(Integer, nullable=False)
    max_consecutive_zeros = Column(Integer, nullable=False)
    skewness = Column(Float, nullable=False)
    kurtosis = Column(Float, nullable=False)
    q25 = Column(Float, nullable=False)
    q75 = Column(Float, nullable=False)
    iqr = Column(Float, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<RawFeature for {self.client_id}>"


# ========== TABLE 5 : PRÉDICTIONS TEMPS RÉEL MQTT ==========
class RealtimePrediction(Base):
    """
    Table des prédictions temps réel à partir des flux MQTT
    (IoT sensors / smart meters)
    """
    __tablename__ = "realtime_predictions"
    
    # Clé primaire
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source des données
    meter_id = Column(String, nullable=False, index=True)  # ID du capteur/compteur
    source = Column(Enum(PredictionSourceEnum), default=PredictionSourceEnum.REALTIME)
    
    # Données du capteur
    consumption_kw = Column(Float, nullable=True)
    voltage_v = Column(Float, nullable=True)
    current_a = Column(Float, nullable=True)
    power_factor = Column(Float, nullable=True)
    frequency_hz = Column(Float, nullable=True)
    is_night = Column(Boolean, default=False)
    hour = Column(Integer, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    
    # Prédictions
    is_fraud = Column(Boolean, nullable=False, index=True)
    fraud_probability = Column(Float, nullable=False)  # Score 0-1
    risk_level = Column(String, nullable=True)  # MINIMAL, LOW, MEDIUM, HIGH, CRITICAL
    
    # Métadonnées
    features_json = Column(Text, nullable=True)  # Features en JSON
    raw_data_json = Column(Text, nullable=True)  # Données brutes MQTT
    
    # Client associé (si connu)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True, index=True)
    
    # Timestamps
    sensor_timestamp = Column(DateTime, nullable=True)  # Timestamp du capteur
    prediction_timestamp = Column(DateTime, default=func.now(), index=True)  # Quand la prédiction a été faite
    
    # Feedback utilisateur (optionnel)
    feedback_type = Column(Enum(FeedbackTypeEnum), nullable=True)
    feedback_timestamp = Column(DateTime, nullable=True)
    feedback_notes = Column(Text, nullable=True)
    
    # Version du modèle
    model_version = Column(String, nullable=True)  # Ex: "1.0.0"
    
    def __repr__(self):
        return f"<RealtimePrediction {self.meter_id} {'🔴 FRAUD' if self.is_fraud else '✅ NORMAL'}>"


# ========== INDICE POUR LES REQUÊTES FRÉQUENTES ==========
# Index pour les requêtes temps réel
from sqlalchemy import Index

# Prédictions par mètre et timestamp
Index('idx_realtime_meter_timestamp', 
      RealtimePrediction.meter_id, 
      RealtimePrediction.prediction_timestamp)