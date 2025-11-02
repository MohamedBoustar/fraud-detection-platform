"""
Point d'entrée principal de l'API FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.database import init_db


from app.config import settings, verify_setup
from app.ml.predictor import predictor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    Exécuté au démarrage et à l'arrêt
    """
    # 🚀 STARTUP
    logger.info("=" * 50)
    logger.info("🚀 Démarrage de l'API Fraud Detection...")
    logger.info("=" * 50)
    
    # Vérifie la configuration
    try:
        verify_setup()
    except Exception as e:
        logger.error(f"❌ Erreur de configuration : {e}")
        raise
    
    # Charge les modèles ML
    logger.info("📦 Chargement des modèles ML...")
    success = predictor.load_models()
    
    if not success:
        logger.error("❌ Échec du chargement des modèles ML")
        raise RuntimeError("Impossible de charger les modèles ML")
    
    # ⭐ NOUVEAU : Initialise la base de données
    init_db()
    
    logger.info("=" * 50)
    logger.info("✅ API prête ! Serveur démarré avec succès")
    logger.info(f"📍 Environnement : {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"🔗 Documentation : http://localhost:{settings.API_PORT}/docs")
    logger.info("=" * 50)
    
    yield  # L'application tourne ici
    
    # 🛑 SHUTDOWN
    logger.info("🛑 Arrêt de l'API...")


# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API de détection de fraude électrique par analyse ML",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS (pour permettre les requêtes depuis le frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== ROUTES DE BASE ==========

@app.get("/")
async def root():
    """Route racine - Information API"""
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
async def health_check():
    """Health check basique"""
    return {
        "status": "healthy",
        "service": "fraud-detection-api"
    }


# ========== IMPORT DES ROUTES ==========
# Import après création de app pour éviter circular imports
from app.api.predictions import router as predictions_router

# Enregistre les routes
app.include_router(
    predictions_router,
    prefix="/api/predictions",
    tags=["Predictions"]
)


# ========== GESTION DES ERREURS ==========

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestion globale des erreurs"""
    logger.error(f"❌ Erreur globale : {exc}")
    return {
        "error": "Internal Server Error",
        "detail": str(exc) if settings.DEBUG else "Une erreur est survenue"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.DEBUG
    )