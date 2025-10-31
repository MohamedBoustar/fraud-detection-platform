"""
Configuration de la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Crée le moteur SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Fonction pour obtenir une session DB
def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()