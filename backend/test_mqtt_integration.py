#!/usr/bin/env python3
"""
Script de test de l'intégration MQTT
Vérifie que tous les composants fonctionnent correctement
"""

import os
import sys
import time
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ajouter le backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.iot import SensorSimulator, MQTTClient


def test_mqtt_connectivity():
    """Test 1: Vérifier la connectivité MQTT"""
    logger.info("=" * 60)
    logger.info("TEST 1: Connectivité MQTT")
    logger.info("=" * 60)
    
    client = MQTTClient(client_id="test-client")
    
    if client.connect():
        logger.info("✅ Connexion réussie")
        stats = client.get_stats()
        logger.info(f"📊 Statuts: {stats}")
        client.disconnect()
        return True
    else:
        logger.error("❌ Connexion échouée")
        return False


def test_sensor_simulator():
    """Test 2: Lancer le simulateur et vérifier les publications"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Simulateur de Capteurs (10 secondes)")
    logger.info("=" * 60)
    
    simulator = SensorSimulator(
        num_meters=3,
        publish_interval=1,
        anomaly_rate=0.1
    )
    
    if not simulator.connect():
        logger.error("❌ Simulateur: connexion échouée")
        return False
    
    # Lancer pour 10 secondes
    logger.info("🚀 Simulation démarrée (10 secondes)...")
    simulator.run(duration_seconds=10)
    
    # Afficher les stats
    stats = simulator.get_stats()
    logger.info(f"📊 Statistiques:\n{stats}")
    
    if stats['messages_sent'] > 0:
        logger.info("✅ Simulateur fonctionne correctement")
        return True
    else:
        logger.error("❌ Aucun message envoyé")
        return False


def test_mqtt_reception():
    """Test 3: Recevoir les messages du simulateur"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Réception des messages MQTT")
    logger.info("=" * 60)
    
    messages_received = []
    
    def message_handler(topic, payload):
        messages_received.append({
            "topic": topic,
            "meter_id": payload.get("meter_id"),
            "consumption_kw": payload.get("consumption_kw"),
            "anomaly_score": payload.get("anomaly_score")
        })
        logger.info(f"📨 Message reçu de {topic}: {payload['meter_id']}")
    
    # Client recepteur
    receiver = MQTTClient(client_id="test-receiver")
    receiver.message_callback = message_handler
    
    if not receiver.connect():
        logger.error("❌ Récepteur: connexion échouée")
        return False
    
    # Simulateur
    simulator = SensorSimulator(
        num_meters=2,
        publish_interval=1,
        anomaly_rate=0.1
    )
    
    if not simulator.connect():
        logger.error("❌ Simulateur: connexion échouée")
        return False
    
    logger.info("🚀 Lancement simulateur + récepteur (8 secondes)...")
    simulator.run(duration_seconds=8)
    
    time.sleep(2)  # Attendre les derniers messages
    receiver.disconnect()
    
    logger.info(f"✅ Reçu {len(messages_received)} messages")
    if messages_received:
        logger.info("📊 Premiers messages:")
        for msg in messages_received[:3]:
            logger.info(f"  - {msg}")
        return True
    else:
        logger.error("❌ Aucun message reçu")
        return False


def main():
    """Exécuter tous les tests"""
    logger.info("\n")
    logger.info("🧪 SUITE DE TESTS - INTÉGRATION MQTT IoT")
    logger.info("=" * 60)
    logger.info(f"Broker: {os.getenv('MQTT_BROKER', 'localhost')}:{os.getenv('MQTT_PORT', '1883')}")
    logger.info("=" * 60)
    
    tests = [
        ("Connectivité MQTT", test_mqtt_connectivity),
        ("Simulateur de Capteurs", test_sensor_simulator),
        ("Réception des messages", test_mqtt_reception),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Erreur test {test_name}: {e}")
            results.append((test_name, False))
        
        time.sleep(1)
    
    # Résumé
    logger.info("\n" + "=" * 60)
    logger.info("📋 RÉSUMÉ DES TESTS")
    logger.info("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, r in results if r)
    logger.info(f"\nTotal: {total_passed}/{len(results)} tests réussis")
    
    if total_passed == len(results):
        logger.info("🎉 TOUS LES TESTS SONT PASSÉS!")
        return 0
    else:
        logger.error("⚠️ Certains tests ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
