"""
Configuration de la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Crée le moteur SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,  # Affiche les requêtes SQL en mode debug
    pool_pre_ping=True,   # Vérifie la connexion avant utilisation
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données (crée les tables)
    À appeler au démarrage de l'application
    """
    try:
        logger.info("🔄 Initialisation de la base de données...")
        
        # Importe tous les modèles pour que SQLAlchemy les connaisse
        from app.models import db_models
        
        # Crée toutes les tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Base de données initialisée avec succès")
        logger.info(f"📊 Tables créées : {', '.join(Base.metadata.tables.keys())}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la DB : {e}")
        raise