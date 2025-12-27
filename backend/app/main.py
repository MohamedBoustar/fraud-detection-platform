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
from app.services.realtime_service import initialize_realtime_service
from app.services.mqtt_consumer import initialize_mqtt_consumer

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
    
    # ⭐ NOUVEAU : Initialiser le service realtime WebSocket
    logger.info("🔔 Initialisation du service Realtime...")
    realtime_service = initialize_realtime_service(max_history=100)
    app.state.realtime_service = realtime_service
    
    # ⭐ NOUVEAU : Démarrer le Consumer MQTT
    logger.info("📡 Démarrage du Consumer MQTT...")
    mqtt_success = await initialize_mqtt_consumer(realtime_service=realtime_service)
    
    if mqtt_success:
        logger.info("✅ Consumer MQTT démarré avec succès")
    else:
        logger.warning("⚠️ Consumer MQTT: impossible de se connecter (mais l'API continue)")
    
    logger.info("=" * 50)
    logger.info("✅ API prête ! Serveur démarré avec succès")
    logger.info(f"📍 Environnement : {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"🔗 Documentation : http://localhost:{settings.API_PORT}/docs")
    logger.info(f"📡 Realtime : {len(realtime_service.connected_clients)} clients connectés")
    logger.info("=" * 50)
    
    yield  # L'application tourne ici
    
    # 🛑 SHUTDOWN
    logger.info("🛑 Arrêt de l'API...")
    
    # Arrêter le consumer MQTT
    from app.services.mqtt_consumer import get_mqtt_consumer
    consumer = get_mqtt_consumer()
    if consumer:
        consumer.stop()


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
            "realtime_stats": "/api/realtime/stats",
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


# ========== ROUTES REALTIME ==========

@app.get("/api/realtime/stats")
async def get_realtime_stats():
    """Obtenir les statistiques du service realtime"""
    from app.services.realtime_service import get_realtime_service
    realtime_service = get_realtime_service()
    
    if not realtime_service:
        return {"error": "Realtime service not initialized"}
    
    # Aussi inclure les stats du consumer MQTT
    from app.services.mqtt_consumer import get_mqtt_consumer
    mqtt_consumer = get_mqtt_consumer()
    
    return {
        "realtime": realtime_service.get_stats(),
        "mqtt_consumer": mqtt_consumer.get_stats() if mqtt_consumer else None,
    }


@app.get("/api/realtime/history")
async def get_realtime_history(limit: int = 50):
    """Obtenir l'historique des prédictions récentes"""
    from app.services.realtime_service import get_realtime_service
    realtime_service = get_realtime_service()
    
    if not realtime_service:
        return {"error": "Realtime service not initialized"}
    
    return {
        "history": realtime_service.get_history(limit=limit),
        "count": len(realtime_service.message_queue),
    }


# ========== WEBSOCKET ENDPOINT ==========

from fastapi import WebSocket, WebSocketDisconnect
import uuid

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket pour les prédictions temps réel
    Les clients se connectent ici pour recevoir les prédictions en direct
    """
    client_id = str(uuid.uuid4())
    
    await websocket.accept()
    logger.info(f"✅ WebSocket connecté: {client_id}")
    
    from app.services.realtime_service import get_realtime_service
    realtime_service = get_realtime_service()
    
    if realtime_service:
        realtime_service.add_client(client_id)
        
        # Envoyer le message de bienvenue
        welcome_message = {
            "type": "welcome",
            "client_id": client_id,
            "message": "Connecté au service de prédictions temps réel",
            "stats": realtime_service.get_stats(),
        }
        
        try:
            await websocket.send_json(welcome_message)
        except Exception as e:
            logger.error(f"Erreur envoi message bienvenue: {e}")
    
    try:
        # Garder la connexion ouverte et recevoir les messages
        while True:
            # Attendre un message du client (pour keep-alive)
            data = await websocket.receive_text()
            
            if data == "ping":
                # Répondre au ping
                await websocket.send_json({"type": "pong"})
            elif data == "stats":
                # Envoyer les stats
                if realtime_service:
                    await websocket.send_json({
                        "type": "stats",
                        "data": realtime_service.get_stats()
                    })
    
    except WebSocketDisconnect:
        logger.info(f"👋 WebSocket déconnecté: {client_id}")
        if realtime_service:
            realtime_service.remove_client(client_id)
    
    except Exception as e:
        logger.error(f"❌ Erreur WebSocket: {e}")
        if realtime_service:
            realtime_service.remove_client(client_id)


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