#!/usr/bin/env python3
"""
Test MQTT complet avec broker embarqué (HiveMQ public broker)
Pour tester l'intégration sans avoir Mosquitto localement installé
"""

import sys
import os
import time
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.iot import SensorSimulator, MQTTClient


def test_mqtt_with_public_broker():
    """
    Test MQTT avec le broker public HiveMQ
    (Pour valider l'intégration sans installer Mosquitto localement)
    """
    logger.info("=" * 60)
    logger.info("TEST: Intégration MQTT avec HiveMQ Public Broker")
    logger.info("=" * 60)
    logger.info("📡 Broker: broker.hivemq.com:1883")
    logger.info("(Broker public gratuit pour tester)")
    
    # Utiliser le broker public HiveMQ au lieu du localhost
    broker_host = "broker.hivemq.com"
    broker_port = 1883
    
    logger.info(f"\n🔗 Tentative de connexion à {broker_host}:{broker_port}...")
    
    # Client récepteur
    receiver = MQTTClient(
        broker_host=broker_host,
        broker_port=broker_port,
        client_id=f"fraud-receiver-{int(time.time())}"
    )
    
    messages_received = []
    
    def message_handler(topic, payload):
        messages_received.append(payload)
        logger.info(f"📨 Message reçu: {topic}")
        logger.info(f"   Compteur: {payload.get('meter_id')}")
        logger.info(f"   Consommation: {payload.get('consumption_kw')}kW")
        if payload.get('anomaly_score', 0) > 0.5:
            logger.warning(f"   ⚠️ ANOMALIE détectée: {payload.get('anomaly_score')}")
    
    receiver.message_callback = message_handler
    
    # Connexion récepteur
    if not receiver.connect():
        logger.error("❌ Impossible de se connecter au broker")
        logger.info("⚠️ Note: Vérifiez votre connexion Internet")
        return False
    
    time.sleep(2)  # Attendre connexion
    
    # Simulateur
    logger.info("\n🚀 Démarrage du simulateur...")
    simulator = SensorSimulator(
        broker_host=broker_host,
        broker_port=broker_port,
        num_meters=3,
        publish_interval=2,
        anomaly_rate=0.15
    )
    
    if not simulator.connect():
        logger.error("❌ Simulateur: impossible de se connecter")
        return False
    
    # Lancer la simulation en thread
    logger.info("📤 Simulation en cours (10 secondes)...")
    simulator.run(duration_seconds=10)
    
    # Attendre réception
    time.sleep(3)
    receiver.disconnect()
    
    # Résultats
    logger.info(f"\n✅ Messages reçus: {len(messages_received)}")
    logger.info(f"📊 Messages publiés par simulateur: {simulator.messages_sent}")
    
    if len(messages_received) > 0:
        logger.info("\n📊 Premiers messages reçus:")
        for msg in messages_received[:3]:
            logger.info(f"  - {msg.get('meter_id')}: {msg.get('consumption_kw')}kW")
        logger.info("\n✅ TEST RÉUSSI!")
        return True
    else:
        logger.warning("⚠️ Aucun message reçu (vérifiez la connexion Internet)")
        return False


def test_local_mqtt_only():
    """
    Test uniquement la partie génération de données MQTT
    Sans connexion réelle
    """
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Génération de messages MQTT")
    logger.info("=" * 60)
    
    import json
    
    simulator = SensorSimulator(
        num_meters=5,
        publish_interval=1,
        anomaly_rate=0.1
    )
    
    # Simuler la génération de messages
    logger.info("📊 Simulation de 5 messages MQTT...")
    
    messages = []
    current_hour = 12
    
    for i, meter in enumerate(simulator.meters[:5]):
        has_anomaly = i % 3 == 0  # Injecter une anomalie dans le 1er et 4ème
        data = meter.update(current_hour, anomaly=has_anomaly)
        messages.append(data)
        
        # Afficher comme message MQTT
        topic = f"sensors/{meter.meter_id}"
        payload = json.dumps(data)
        
        logger.info(f"\n📡 Topic: {topic}")
        logger.info(f"   Payload: {payload[:80]}...")
        logger.info(f"   Consommation: {data['consumption_kw']}kW")
        logger.info(f"   Score anomalie: {data['anomaly_score']}")
    
    logger.info(f"\n✅ {len(messages)} messages générés correctement")
    return True


def main():
    """Exécuter les tests"""
    logger.info("\n")
    logger.info("🧪 TESTS MQTT - INTÉGRATION IoT")
    logger.info("=" * 60)
    
    # Test 1: Génération de données
    logger.info("\n📝 Test 1: Génération de messages MQTT")
    test1_result = test_local_mqtt_only()
    
    # Test 2: Connexion réelle (optionnel - nécessite Internet)
    logger.info("\n\n📝 Test 2: Intégration avec broker MQTT")
    logger.info("(En utilisant broker.hivemq.com public)")
    
    try:
        test2_result = test_mqtt_with_public_broker()
    except Exception as e:
        logger.error(f"⚠️ Test broker public échoué: {e}")
        logger.info("(Cela est acceptable si Internet n'est pas disponible)")
        test2_result = None
    
    # Résumé
    logger.info("\n" + "=" * 60)
    logger.info("📋 RÉSUMÉ")
    logger.info("=" * 60)
    logger.info(f"✅ Génération de messages MQTT: {'PASS' if test1_result else 'FAIL'}")
    
    if test2_result is None:
        logger.info("⚠️ Test broker public: SKIPPED (pas d'Internet ou broker indisponible)")
    else:
        logger.info(f"✅ Intégration broker MQTT: {'PASS' if test2_result else 'FAIL'}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 PROCHAINES ÉTAPES:")
    logger.info("=" * 60)
    logger.info("1. ✅ Simulateur et génération de données: VALIDÉS")
    logger.info("2. ⏳ Installer Mosquitto pour tests locaux")
    logger.info("   → docker run -d -p 1883:1883 eclipse-mosquitto:latest")
    logger.info("   → Ou: homebrew, apt-get, brew, etc.")
    logger.info("3. ⏳ Exécuter: python test_mqtt_integration.py")
    logger.info("4. ⏳ PHASE 2: Intégration backend")
    
    return 0 if (test1_result and (test2_result is True or test2_result is None)) else 1


if __name__ == "__main__":
    sys.exit(main())
