"""
Client MQTT asynchrone pour consommer les données des capteurs
Détecte les fraudes en temps réel
"""

import paho.mqtt.client as mqtt
import json
import logging
import asyncio
from typing import Callable, Optional, Dict
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class MQTTClient:
    """
    Client MQTT asynchrone pour recevoir les données des capteurs
    et publier les prédictions de fraude
    """
    
    def __init__(
        self,
        broker_host: str = None,
        broker_port: int = None,
        username: str = None,
        password: str = None,
        client_id: str = "fraud-detector"
    ):
        """
        Initialiser le client MQTT
        
        Args:
            broker_host: Adresse du broker MQTT (défaut: env MQTT_BROKER)
            broker_port: Port du broker (défaut: env MQTT_PORT ou 1883)
            username: Username MQTT (défaut: env MQTT_USERNAME)
            password: Password MQTT (défaut: env MQTT_PASSWORD)
            client_id: ID unique du client
        """
        self.broker_host = broker_host or os.getenv("MQTT_BROKER", "localhost")
        self.broker_port = broker_port or int(os.getenv("MQTT_PORT", "1883"))
        self.username = username or os.getenv("MQTT_USERNAME", "dev")
        self.password = password or os.getenv("MQTT_PASSWORD", "dev_password")
        self.client_id = client_id
        
        # Topics
        self.sensor_topic = os.getenv("MQTT_TOPIC_SENSORS", "sensors/meter_+")
        self.predictions_topic = os.getenv("MQTT_TOPIC_PREDICTIONS", "predictions/fraud")
        
        # Client MQTT
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        
        # Définir les credentials seulement si fournis
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        elif self.username:
            self.client.username_pw_set(self.username)
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        
        # État
        self.is_connected = False
        self.message_callback: Optional[Callable] = None
        self.messages_received = 0
        self.messages_processed = 0
        
        logger.info(f"🔧 Client MQTT initialisé: {self.client_id}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback de connexion au broker"""
        if rc == 0:
            self.is_connected = True
            logger.info(f"✅ Connecté au broker MQTT: {self.broker_host}:{self.broker_port}")
            
            # S'abonner aux topics de capteurs (seulement si on a un callback)
            if self.message_callback:
                # Remplacer "meter_+" par un wildcard compatible
                topic = self.sensor_topic.replace("meter_+", "#")
                client.subscribe(topic, qos=1)
                logger.info(f"📡 Abonné au topic: {topic}")
        else:
            logger.error(f"❌ Erreur de connexion MQTT (code {rc})")
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion"""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"⚠️ Déconnexion inattendue MQTT (code {rc})")
        else:
            logger.info("👋 Déconnecté du broker MQTT")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback d'abonnement"""
        logger.info(f"✅ Abonnement accepté (QoS: {granted_qos})")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback de réception de message
        Appelle le message_callback si défini
        """
        self.messages_received += 1
        
        try:
            # Parser le message JSON
            payload = json.loads(msg.payload.decode())
            
            logger.debug(f"📨 Message reçu de {msg.topic}: {payload}")
            
            # Appeler le callback si défini
            if self.message_callback:
                self.message_callback(msg.topic, payload)
            
            self.messages_processed += 1
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
    
    def connect(self) -> bool:
        """
        Établir la connexion au broker MQTT
        
        Returns:
            True si succès, False sinon
        """
        try:
            logger.info(f"🔗 Tentative de connexion à {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            
            # Démarrer la boucle MQTT
            self.client.loop_start()
            
            # Attendre la connexion
            import time
            for i in range(30):  # Max 30 secondes
                if self.is_connected:
                    return True
                time.sleep(1)
            
            logger.error("❌ Timeout connexion MQTT")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion MQTT: {e}")
            return False
    
    def disconnect(self):
        """Déconnecter du broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("👋 Client MQTT déconnecté")
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion: {e}")
    
    def publish_prediction(
        self,
        meter_id: str,
        is_fraud: bool,
        fraud_probability: float,
        features: Dict = None,
        metadata: Dict = None
    ) -> bool:
        """
        Publier une prédiction de fraude
        
        Args:
            meter_id: ID du compteur
            is_fraud: True si fraude détectée
            fraud_probability: Probabilité de fraude (0-1)
            features: Features utilisées pour la prédiction
            metadata: Métadonnées additionnelles
            
        Returns:
            True si succès, False sinon
        """
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "meter_id": meter_id,
                "is_fraud": is_fraud,
                "fraud_probability": round(fraud_probability, 4),
                "risk_level": self._get_risk_level(fraud_probability),
                "features": features or {},
                "metadata": metadata or {}
            }
            
            topic = f"{self.predictions_topic}/{meter_id}"
            
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=1,
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"✅ Prédiction publiée: {topic}")
                return True
            else:
                logger.error(f"❌ Erreur publication: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur publication prédiction: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Retourner les statistiques du client"""
        return {
            "is_connected": self.is_connected,
            "messages_received": self.messages_received,
            "messages_processed": self.messages_processed,
            "broker": f"{self.broker_host}:{self.broker_port}"
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
