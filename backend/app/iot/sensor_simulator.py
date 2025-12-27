"""
Simulateur de capteurs IoT (Compteurs électriques)
Publie des données réalistes + anomalies vers Mosquitto MQTT
"""

import json
import time
import logging
import random
import math
from datetime import datetime
from typing import Dict, List
import paho.mqtt.client as mqtt
import os
import threading

logger = logging.getLogger(__name__)


class MeterData:
    """Structure pour les données d'un compteur"""
    
    def __init__(self, meter_id: str):
        self.meter_id = meter_id
        self.base_consumption = random.uniform(50, 300)  # kWh/jour
        self.current_consumption = self.base_consumption
        self.voltage = 220  # Volts
        self.current = 10   # Amperes
        self.power_factor = 0.95
        self.frequency = 50  # Hz
        self.cumulative_energy = random.uniform(1000, 50000)  # kWh total
        self.anomaly_score = 0
        self.timestamp = None
        
        # Pattern jour/nuit
        self.is_night = False
        self.hour = 0
    
    def update(self, current_hour: int, anomaly: bool = False) -> Dict:
        """
        Mettre à jour les données du compteur
        
        Args:
            current_hour: Heure actuelle (0-23)
            anomaly: Injecter une anomalie
            
        Returns:
            Dict avec toutes les données
        """
        self.hour = current_hour
        self.is_night = (current_hour >= 22 or current_hour < 6)
        
        # Consommation normalisée par heure
        if self.is_night:
            base = self.base_consumption * 0.3 / 24  # 30% la nuit
        else:
            base = self.base_consumption / 24
        
        # Ajouter de la variance naturelle
        variance = random.gauss(0, base * 0.2)
        self.current_consumption = max(0, base + variance)
        
        # Tension/courant
        self.voltage = 220 + random.gauss(0, 5)  # ±5V variance
        self.current = (self.current_consumption * 1000) / (self.voltage * self.power_factor)
        self.current = max(0, self.current + random.gauss(0, 2))
        
        # Anomalies
        if anomaly:
            self.current_consumption *= random.uniform(2.5, 4.0)  # Pic anormal
            self.anomaly_score = random.uniform(0.7, 0.95)
        else:
            self.anomaly_score = max(0, self.anomaly_score * 0.9)  # Décroissance
        
        # Énergie cumulée
        self.cumulative_energy += self.current_consumption / 24
        self.timestamp = datetime.utcnow().isoformat()
        
        return {
            "meter_id": self.meter_id,
            "timestamp": self.timestamp,
            "consumption_kw": round(self.current_consumption, 3),
            "voltage_v": round(self.voltage, 2),
            "current_a": round(self.current, 2),
            "power_factor": round(self.power_factor, 3),
            "frequency_hz": self.frequency,
            "cumulative_energy_kwh": round(self.cumulative_energy, 2),
            "anomaly_score": round(self.anomaly_score, 3),
            "is_night": self.is_night,
            "hour": self.hour
        }


class SensorSimulator:
    """
    Simulateur de capteurs électriques MQTT
    Publie des données réalistes de compteurs
    """
    
    def __init__(
        self,
        broker_host: str = None,
        broker_port: int = None,
        username: str = None,
        password: str = None,
        num_meters: int = 10,
        publish_interval: int = 5,
        anomaly_rate: float = 0.05
    ):
        """
        Initialiser le simulateur
        
        Args:
            broker_host: Adresse broker MQTT
            broker_port: Port broker
            username: Username MQTT
            password: Password MQTT
            num_meters: Nombre de compteurs à simuler
            publish_interval: Intervalle de publication (secondes)
            anomaly_rate: Probabilité d'anomalie par capteur (0-1)
        """
        self.broker_host = broker_host or os.getenv("MQTT_BROKER", "localhost")
        self.broker_port = broker_port or int(os.getenv("MQTT_PORT", "1883"))
        self.username = username or os.getenv("MQTT_USERNAME", "sensor_simulator")
        self.password = password or os.getenv("MQTT_PASSWORD", "dev_password")
        
        self.num_meters = num_meters
        self.publish_interval = publish_interval
        self.anomaly_rate = anomaly_rate
        
        # Créer les compteurs
        self.meters: List[MeterData] = [
            MeterData(f"METER_{i:04d}") for i in range(num_meters)
        ]
        
        # Client MQTT
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "sensor-simulator")
        self.client.username_pw_set(self.username, self.password)
        
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # État
        self.is_connected = False
        self.is_running = False
        self.messages_sent = 0
        self.anomalies_injected = 0
        self.start_time = None
        
        logger.info(f"🔧 Simulateur initialisé: {num_meters} compteurs")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback de connexion"""
        if rc == 0:
            self.is_connected = True
            logger.info(f"✅ Simulateur connecté au broker: {self.broker_host}:{self.broker_port}")
        else:
            logger.error(f"❌ Erreur connexion (code {rc})")
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion"""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"⚠️ Déconnexion inattendue (code {rc})")
    
    def _on_publish(self, client, userdata, mid):
        """Callback de publication"""
        self.messages_sent += 1
        if self.messages_sent % 10 == 0:
            logger.debug(f"📡 {self.messages_sent} messages publiés")
    
    def connect(self) -> bool:
        """Établir la connexion"""
        try:
            logger.info(f"🔗 Connexion au broker {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            
            # Attendre connexion
            for i in range(30):
                if self.is_connected:
                    return True
                time.sleep(1)
            
            logger.error("❌ Timeout connexion")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def disconnect(self):
        """Déconnecter"""
        try:
            self.is_running = False
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("👋 Simulateur déconnecté")
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion: {e}")
    
    def run(self, duration_seconds: int = None):
        """
        Lancer la simulation
        
        Args:
            duration_seconds: Durée en secondes (None = infini)
        """
        if not self.is_connected:
            logger.error("❌ Non connecté au broker")
            return
        
        self.is_running = True
        self.start_time = time.time()
        iteration = 0
        
        logger.info(f"🚀 Simulation démarrée ({self.num_meters} compteurs)")
        logger.info(f"📤 Intervalle: {self.publish_interval}s | Taux anomalies: {self.anomaly_rate*100}%")
        
        try:
            while self.is_running:
                iteration += 1
                
                # Heure simulée (cycle jour/nuit rapide)
                current_hour = (iteration // (3600 // self.publish_interval)) % 24
                
                # Publier les données de chaque compteur
                for meter in self.meters:
                    # Vérifier si anomalie
                    has_anomaly = random.random() < self.anomaly_rate
                    if has_anomaly:
                        self.anomalies_injected += 1
                    
                    # Mettre à jour et récupérer les données
                    data = meter.update(current_hour, anomaly=has_anomaly)
                    
                    # Publier vers MQTT
                    topic = f"sensors/{meter.meter_id}"
                    self.client.publish(
                        topic,
                        json.dumps(data),
                        qos=1,
                        retain=False
                    )
                    
                    if has_anomaly:
                        logger.warning(
                            f"⚠️ ANOMALIE injectée: {meter.meter_id} "
                            f"(consommation: {data['consumption_kw']}kW)"
                        )
                
                # Afficher statut toutes les 10 itérations
                if iteration % 10 == 0:
                    elapsed = time.time() - self.start_time
                    logger.info(
                        f"📊 Itération {iteration} | "
                        f"Messages: {self.messages_sent} | "
                        f"Anomalies: {self.anomalies_injected} | "
                        f"Temps: {elapsed:.0f}s"
                    )
                
                # Vérifier durée
                if duration_seconds and (time.time() - self.start_time) >= duration_seconds:
                    logger.info(f"⏱️ Durée atteinte ({duration_seconds}s)")
                    break
                
                # Attendre avant prochaine publication
                time.sleep(self.publish_interval)
        
        except KeyboardInterrupt:
            logger.info("⚠️ Arrêt par utilisateur")
        except Exception as e:
            logger.error(f"❌ Erreur simulation: {e}")
        finally:
            self.disconnect()
    
    def run_async(self):
        """Démarrer la simulation dans un thread séparé"""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Arrêter la simulation"""
        self.is_running = False
        logger.info("⏹️ Arrêt simulation demandé")
    
    def get_stats(self) -> Dict:
        """Retourner les statistiques"""
        elapsed = (time.time() - self.start_time) if self.start_time else 0
        
        return {
            "is_connected": self.is_connected,
            "is_running": self.is_running,
            "messages_sent": self.messages_sent,
            "anomalies_injected": self.anomalies_injected,
            "elapsed_seconds": round(elapsed, 2),
            "avg_rate": round(self.messages_sent / elapsed, 2) if elapsed > 0 else 0,
            "num_meters": self.num_meters,
            "anomaly_rate": self.anomaly_rate
        }


# ============ SCRIPT STANDALONE ============
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer et lancer le simulateur
    simulator = SensorSimulator(
        num_meters=10,
        publish_interval=5,
        anomaly_rate=0.05  # 5% des messages contiennent anomalies
    )
    
    if simulator.connect():
        try:
            simulator.run()  # Infini
        except KeyboardInterrupt:
            simulator.stop()
