"""
Configuration de l'application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

class Settings:
    """Configuration globale de l'application"""
    
    # Informations de base
    APP_NAME: str = os.getenv("APP_NAME", "Fraud Detection API")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    
    # Base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fraud_detection.db")
    
    # Sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # Chemins des modèles ML
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    ML_MODELS_DIR: Path = BASE_DIR / "app" / "ml" / "models"
    MODEL_PATH: Path = ML_MODELS_DIR / "fraud_detection_model.pkl"
    SCALER_PATH: Path = ML_MODELS_DIR / "scaler.pkl"
    
    # Paramètres de prédiction
    DEFAULT_THRESHOLD: float = 0.5
    MIN_DATA_DAYS: int = 7  # Minimum de jours de données requis
    
    # CORS (pour permettre frontend React)
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative
        "http://127.0.0.1:5173",
    ]
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-west-3")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME", "")
    
    # Feature: Enable/Disable S3 Storage
    USE_S3_STORAGE: bool = os.getenv("USE_S3_STORAGE", "True").lower() == "true"

# Instance unique
settings = Settings()

# Vérification au démarrage
def verify_setup():
    """Vérifie que tout est configuré correctement"""
    errors = []
    
    if not settings.MODEL_PATH.exists():
        errors.append(f"❌ Modèle non trouvé : {settings.MODEL_PATH}")
    
    if not settings.SCALER_PATH.exists():
        errors.append(f"❌ Scaler non trouvé : {settings.SCALER_PATH}")
    
    # Vérifier AWS S3 si activé
    if settings.USE_S3_STORAGE:
        if not settings.AWS_ACCESS_KEY_ID:
            errors.append("⚠️ AWS_ACCESS_KEY_ID manquant (S3 désactivé)")
            settings.USE_S3_STORAGE = False
        if not settings.AWS_SECRET_ACCESS_KEY:
            errors.append("⚠️ AWS_SECRET_ACCESS_KEY manquant (S3 désactivé)")
            settings.USE_S3_STORAGE = False
        if not settings.AWS_BUCKET_NAME:
            errors.append("⚠️ AWS_BUCKET_NAME manquant (S3 désactivé)")
            settings.USE_S3_STORAGE = False
    
    if errors:
        for error in errors:
            print(error)
        if "❌" in " ".join(errors):
            raise FileNotFoundError("Fichiers de modèles ML manquants !")
    
    print("✅ Configuration vérifiée avec succès")
    print(f"✅ Modèle trouvé : {settings.MODEL_PATH}")
    print(f"✅ Scaler trouvé : {settings.SCALER_PATH}")
    
    if settings.USE_S3_STORAGE:
        print(f"✅ AWS S3 activé : {settings.AWS_BUCKET_NAME} ({settings.AWS_REGION})")
    else:
        print("⚠️ AWS S3 désactivé - Stockage local uniquement")