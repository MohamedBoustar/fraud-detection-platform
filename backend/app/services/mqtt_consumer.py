"""
Consumer MQTT asynchrone - Écoute les données des capteurs
et déclenche les prédictions ML en temps réel
"""

import asyncio
import logging
from typing import Callable, Optional, Dict, List
from datetime import datetime
import json

from app.iot.mqtt_client import MQTTClient
from app.ml.predictor import predictor
from app.ml.preprocessing import FraudPreprocessor
from app.database import get_db
from app.services import db_service

logger = logging.getLogger(__name__)


class MQTTConsumer:
    """
    Consomme les messages MQTT et exécute les prédictions ML
    
    Pipeline:
    MQTT (sensors/METER_*) → Preprocessing → ML Model → Prédictions → BD + WebSocket
    """
    
    def __init__(self, realtime_service=None):
        """
        Initialiser le consumer
        
        Args:
            realtime_service: Service pour broadcast WebSocket (optionnel)
        """
        self.mqtt_client = MQTTClient()
        self.realtime_service = realtime_service
        self.preprocessor = FraudPreprocessor()
        
        # Stats
        self.messages_received = 0
        self.predictions_made = 0
        self.frauds_detected = 0
        self.errors = 0
        
        # Attacher le callback
        self.mqtt_client.message_callback = self._handle_sensor_message
        
        logger.info("🔧 Consumer MQTT initialisé")
    
    async def start(self) -> bool:
        """
        Démarrer le consumer - se connecte au broker MQTT
        
        Returns:
            True si succès, False sinon
        """
        logger.info("🚀 Démarrage du Consumer MQTT...")
        
        # Connexion MQTT
        if not self.mqtt_client.connect():
            logger.error("❌ Impossible de se connecter au broker MQTT")
            return False
        
        logger.info("✅ Consumer MQTT démarré")
        return True
    
    def stop(self):
        """Arrêter le consumer"""
        logger.info("⏹️ Arrêt du Consumer MQTT...")
        self.mqtt_client.disconnect()
    
    def _handle_sensor_message(self, topic: str, payload: Dict):
        """
        Callback appelé à la réception d'un message MQTT
        Exécute le pipeline complet de prédiction
        
        Args:
            topic: Topic MQTT (ex: sensors/METER_0000)
            payload: Données du capteur (JSON)
        """
        try:
            self.messages_received += 1
            
            # Parser les données
            meter_id = payload.get("meter_id")
            timestamp = payload.get("timestamp")
            consumption = payload.get("consumption_kw")
            
            if not meter_id:
                logger.warning("⚠️ meter_id manquant dans le message")
                return
            
            logger.debug(f"📨 Message reçu: {meter_id} ({consumption}kW)")
            
            # ============ PRÉDICTION ML ============
            
            if not predictor.is_loaded:
                logger.error("❌ Modèle ML non chargé")
                self.errors += 1
                return
            
            # Faire la prédiction avec les données IoT temps réel
            # predict_realtime() génère les features statistiques à partir des valeurs instantanées
            prediction_result = predictor.predict_realtime(payload)
            
            if not prediction_result:
                logger.error(f"❌ Erreur prédiction pour {meter_id}")
                self.errors += 1
                return
            
            is_fraud = prediction_result.get("is_fraud", False)
            fraud_probability = prediction_result.get("fraud_probability", 0.0)
            features = prediction_result.get("features", {})
            
            self.predictions_made += 1
            
            if is_fraud:
                self.frauds_detected += 1
                logger.warning(
                    f"🚨 FRAUDE DÉTECTÉE: {meter_id} "
                    f"(Score: {fraud_probability:.3f})"
                )
            else:
                logger.debug(
                    f"✅ Normal: {meter_id} (Score: {fraud_probability:.3f})"
                )
            
            # ============ STOCKAGE BD ============
            
            self._save_prediction(
                meter_id=meter_id,
                timestamp=timestamp,
                is_fraud=is_fraud,
                fraud_probability=fraud_probability,
                features=features,
                raw_data=payload
            )
            
            # ============ BROADCAST WEBSOCKET ============
            
            if self.realtime_service:
                self._broadcast_prediction(
                    meter_id=meter_id,
                    is_fraud=is_fraud,
                    fraud_probability=fraud_probability,
                    consumption=consumption,
                    timestamp=timestamp
                )
        
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
            self.errors += 1
            import traceback
            traceback.print_exc()
    
    def _extract_features(self, payload: Dict) -> Dict:
        """
        Extraire les features pour le modèle ML
        
        Args:
            payload: Données MQTT brutes
            
        Returns:
            Dict avec features prétraitées
        """
        features = {
            "consumption_kw": payload.get("consumption_kw", 0),
            "voltage_v": payload.get("voltage_v", 220),
            "current_a": payload.get("current_a", 0),
            "power_factor": payload.get("power_factor", 0.95),
            "frequency_hz": payload.get("frequency_hz", 50),
            "is_night": payload.get("is_night", False),
            "hour": payload.get("hour", 12),
            "anomaly_score": payload.get("anomaly_score", 0),
        }
        
        # Prétraitement si nécessaire
        # (normalization, scaling, etc.)
        
        return features
    
    def _save_prediction(
        self,
        meter_id: str,
        timestamp: str,
        is_fraud: bool,
        fraud_probability: float,
        features: Dict,
        raw_data: Dict
    ):
        """
        Sauvegarder la prédiction en BD
        
        Args:
            meter_id: ID du compteur
            timestamp: Timestamp du capteur
            is_fraud: Si fraude détectée
            fraud_probability: Score de fraude
            features: Features utilisées
            raw_data: Données brutes MQTT
        """
        try:
            # Utiliser db_service pour insérer en BD
            # (À implémenter selon le modèle existant)
            
            logger.debug(
                f"💾 Prédiction sauvegardée: {meter_id} "
                f"(fraude={is_fraud}, score={fraud_probability:.3f})"
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde BD: {e}")
            self.errors += 1
    
    def _broadcast_prediction(
        self,
        meter_id: str,
        is_fraud: bool,
        fraud_probability: float,
        consumption: float,
        timestamp: str
    ):
        """
        Envoyer la prédiction via WebSocket aux clients connectés
        
        Args:
            meter_id: ID du compteur
            is_fraud: Si fraude
            fraud_probability: Score fraude
            consumption: Consommation en kW
            timestamp: Timestamp
        """
        try:
            if not self.realtime_service:
                return
            
            # Créer le message
            message = {
                "type": "prediction",
                "meter_id": meter_id,
                "timestamp": timestamp,
                "is_fraud": is_fraud,
                "fraud_probability": round(fraud_probability, 4),
                "risk_level": self._get_risk_level(fraud_probability),
                "consumption_kw": round(consumption, 3),
            }
            
            # Broadcast - utiliser asyncio pour appeler la fonction async
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(self.realtime_service.broadcast(message))
                else:
                    loop.run_until_complete(self.realtime_service.broadcast(message))
            except RuntimeError:
                # Pas de loop, créer une nouvelle
                asyncio.run(self.realtime_service.broadcast(message))
            
            logger.debug(f"📡 Message WebSocket envoyé: {meter_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur broadcast WebSocket: {e}")
    
    def get_stats(self) -> Dict:
        """Retourner les statistiques du consumer"""
        return {
            "status": "running" if self.mqtt_client.is_connected else "stopped",
            "messages_received": self.messages_received,
            "predictions_made": self.predictions_made,
            "frauds_detected": self.frauds_detected,
            "error_count": self.errors,
            "fraud_rate": (
                self.frauds_detected / self.predictions_made * 100
                if self.predictions_made > 0
                else 0
            ),
        }
    
    @staticmethod
    def _get_risk_level(fraud_probability: float) -> str:
        """Déterminer le niveau de risque"""
        if fraud_probability >= 0.8:
            return "CRITICAL"
        elif fraud_probability >= 0.6:
            return "HIGH"
        elif fraud_probability >= 0.4:
            return "MEDIUM"
        elif fraud_probability >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"


# Instance globale
mqtt_consumer: Optional[MQTTConsumer] = None


async def initialize_mqtt_consumer(realtime_service=None) -> bool:
    """
    Initialiser le consumer MQTT global
    À appeler au startup de l'application
    """
    global mqtt_consumer
    
    mqtt_consumer = MQTTConsumer(realtime_service=realtime_service)
    
    return await mqtt_consumer.start()


def get_mqtt_consumer() -> Optional[MQTTConsumer]:
    """Obtenir l'instance du consumer"""
    return mqtt_consumer
