"""
Point d'entrée principal de l'API FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings, verify_setup
from app.ml.predictor import predictor
from app.api.predictions import router as predictions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application"""
    # Startup
    print("🚀 Démarrage de l'application...")
    
    # Vérifie la configuration
    verify_setup()
    
    # Charge les modèles ML
    print("📦 Chargement des modèles ML...")
    predictor.load_models()
    
    print("✅ Application prête !")
    
    yield
    
    # Shutdown
    print("👋 Arrêt de l'application...")


# Crée l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API de détection de fraude électrique avec Machine Learning",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS (pour permettre les requêtes depuis React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistre les routes
app.include_router(predictions_router)


@app.get("/")
async def root():
    """Endpoint racine - Info sur l'API"""
    return {
        "message": "🔍 Fraud Detection API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/api/predictions/health",
            "batch_prediction": "/api/predictions/batch",
            "realtime_prediction": "/api/predictions/realtime",
            "model_info": "/api/predictions/model/info",
            "features_info": "/api/predictions/model/features",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check simple"""
    return {"status": "healthy"}