"""
Modèles de base de données
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class PredictionSource(str, enum.Enum):
    """Type de source de prédiction"""
    BATCH = "batch"
    REALTIME = "realtime"


class QualityLevel(str, enum.Enum):
    """Niveau de qualité des données"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"


class FeedbackType(str, enum.Enum):
    """Type de feedback utilisateur"""
    CONFIRMED_FRAUD = "confirmed_fraud"
    FALSE_POSITIVE = "false_positive"
    UNCERTAIN = "uncertain"


class Client(Base):
    """Table des clients"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    cons_no = Column(String, unique=True, index=True, nullable=False)
    date_first_seen = Column(DateTime, default=datetime.utcnow)
    date_last_seen = Column(DateTime, default=datetime.utcnow)
    data_period_days = Column(Integer)  # Nombre de jours d'historique
    total_predictions = Column(Integer, default=0)
    fraud_count = Column(Integer, default=0)
    latest_score = Column(Float)
    latest_prediction = Column(Integer)  # 0 ou 1
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    predictions = relationship("Prediction", back_populates="client")
    feedbacks = relationship("Feedback", back_populates="client")


class Prediction(Base):
    """Table des prédictions (historique)"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    prediction = Column(Integer, nullable=False)  # 0 ou 1
    probability = Column(Float, nullable=False)
    threshold_used = Column(Float, nullable=False)
    source = Column(String)  # "batch" ou "realtime"
    batch_id = Column(Integer, ForeignKey("batch_uploads.id"), nullable=True)
    data_period_days = Column(Integer)
    quality_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    client = relationship("Client", back_populates="predictions")
    batch = relationship("BatchUpload", back_populates="predictions")
    feedbacks = relationship("Feedback", back_populates="prediction")


class BatchUpload(Base):
    """Table des uploads batch"""
    __tablename__ = "batch_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    filename = Column(String, nullable=False)
    file_size_mb = Column(Float)
    total_clients = Column(Integer)
    data_period_days = Column(Integer)
    fraud_detected = Column(Integer)
    fraud_percentage = Column(Float)
    s3_path = Column(String, nullable=True)
    uploaded_by = Column(String, default="anonymous")
    status = Column(String, default="completed")  # processing/completed/failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    predictions = relationship("Prediction", back_populates="batch")


class Feedback(Base):
    """Table des feedbacks utilisateur"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    feedback_type = Column(String, nullable=False)  # confirmed_fraud/false_positive/uncertain
    comment = Column(Text, nullable=True)
    provided_by = Column(String, default="anonymous")
    inspection_date = Column(DateTime, nullable=True)
    inspection_result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    prediction = relationship("Prediction", back_populates="feedbacks")
    client = relationship("Client", back_populates="feedbacks")