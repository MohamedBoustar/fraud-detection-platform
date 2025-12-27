#!/usr/bin/env python3
"""
Test local sans Docker - Simulateur MQTT uniquement
Pour vérifier que les modules fonctionnent sans dépendre de Mosquitto en Container
"""

import sys
import os
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

from app.iot.sensor_simulator import SensorSimulator, MeterData


def test_meter_data():
    """Test 1: Vérifier la génération de données de compteurs"""
    logger.info("=" * 60)
    logger.info("TEST 1: Génération de données de compteurs")
    logger.info("=" * 60)
    
    meter = MeterData("METER_TEST_001")
    
    # Générer quelques données
    logger.info("📊 Génération de 5 points de données...")
    
    data_points = []
    for hour in range(5):
        data = meter.update(hour, anomaly=False)
        data_points.append(data)
        logger.info(f"  Heure {hour}: {data['consumption_kw']}kW, "
                   f"Tension: {data['voltage_v']}V, "
                   f"Courant: {data['current_a']}A")
    
    # Vérifier que les données varient
    consumptions = [d['consumption_kw'] for d in data_points]
    if len(set([round(c) for c in consumptions])) > 1:
        logger.info("✅ Les données varient correctement")
        return True
    else:
        logger.error("❌ Pas de variation dans les données")
        return False


def test_anomaly_injection():
    """Test 2: Vérifier l'injection d'anomalies"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Injection d'anomalies")
    logger.info("=" * 60)
    
    meter = MeterData("METER_ANOMALY")
    
    # Données normales
    normal_data = meter.update(12, anomaly=False)
    normal_consumption = normal_data['consumption_kw']
    logger.info(f"📊 Consommation normale: {normal_consumption}kW")
    
    # Données avec anomalie
    anomaly_data = meter.update(12, anomaly=True)
    anomaly_consumption = anomaly_data['consumption_kw']
    logger.info(f"⚠️ Consommation avec anomalie: {anomaly_consumption}kW")
    
    anomaly_score = anomaly_data['anomaly_score']
    logger.info(f"🔴 Score d'anomalie: {anomaly_score}")
    
    # Vérifier que l'anomalie est significative
    if anomaly_consumption > normal_consumption * 1.5 and anomaly_score > 0.5:
        logger.info("✅ Anomalies injectées correctement")
        return True
    else:
        logger.error("❌ Anomalies insuffisantes")
        return False


def test_day_night_pattern():
    """Test 3: Vérifier le pattern jour/nuit"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Pattern jour/nuit réaliste")
    logger.info("=" * 60)
    
    meter = MeterData("METER_PATTERN")
    
    consumptions_day = []
    consumptions_night = []
    
    logger.info("📈 Simulation de 24 heures...")
    
    for hour in range(24):
        data = meter.update(hour, anomaly=False)
        consumption = data['consumption_kw']
        
        if data['is_night']:
            consumptions_night.append(consumption)
        else:
            consumptions_day.append(consumption)
    
    avg_day = sum(consumptions_day) / len(consumptions_day)
    avg_night = sum(consumptions_night) / len(consumptions_night)
    
    logger.info(f"📊 Consommation jour (moyenne): {avg_day:.2f}kW")
    logger.info(f"🌙 Consommation nuit (moyenne): {avg_night:.2f}kW")
    
    # La nuit doit être < jour
    if avg_night < avg_day * 0.8:
        logger.info("✅ Pattern jour/nuit réaliste")
        return True
    else:
        logger.warning("⚠️ Pattern jour/nuit pas optimal")
        return False


def test_simulator_initialization():
    """Test 4: Initialisation du simulateur (sans connexion)"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Initialisation du simulateur")
    logger.info("=" * 60)
    
    try:
        simulator = SensorSimulator(
            num_meters=5,
            publish_interval=1,
            anomaly_rate=0.1
        )
        
        logger.info(f"✅ Simulateur créé avec {simulator.num_meters} compteurs")
        logger.info(f"📊 Taux d'anomalies: {simulator.anomaly_rate*100}%")
        logger.info(f"⏱️ Intervalle: {simulator.publish_interval}s")
        
        # Vérifier les compteurs
        if len(simulator.meters) == 5:
            logger.info(f"✅ {len(simulator.meters)} compteurs initialisés")
            for meter in simulator.meters[:2]:
                logger.info(f"  - {meter.meter_id}")
            return True
        else:
            logger.error(f"❌ Mauvais nombre de compteurs")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        return False


def test_json_serialization():
    """Test 5: Vérifier que les données sont sérialisables en JSON"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Sérialisation JSON")
    logger.info("=" * 60)
    
    try:
        import json
        
        meter = MeterData("METER_JSON")
        data = meter.update(12, anomaly=False)
        
        # Essayer de sérialiser
        json_str = json.dumps(data)
        logger.info(f"✅ Données sérialisées: {len(json_str)} caractères")
        
        # Vérifier les clés
        required_keys = [
            'meter_id', 'timestamp', 'consumption_kw',
            'voltage_v', 'current_a', 'frequency_hz'
        ]
        
        for key in required_keys:
            if key not in data:
                logger.error(f"❌ Clé manquante: {key}")
                return False
        
        logger.info(f"✅ Toutes les clés requises présentes")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur sérialisation: {e}")
        return False


def main():
    """Exécuter tous les tests"""
    logger.info("\n")
    logger.info("🧪 TESTS LOCAUX - SIMULATEUR IoT")
    logger.info("=" * 60)
    logger.info("(Sans dépendre de Mosquitto en Docker)")
    logger.info("=" * 60)
    
    tests = [
        ("Génération données compteurs", test_meter_data),
        ("Injection d'anomalies", test_anomaly_injection),
        ("Pattern jour/nuit", test_day_night_pattern),
        ("Initialisation simulateur", test_simulator_initialization),
        ("Sérialisation JSON", test_json_serialization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Exception en testant {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
        
        time.sleep(0.5)
    
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
        logger.info("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        logger.info("\n📝 Prochaines étapes:")
        logger.info("  1. Démarrer Mosquitto en Docker")
        logger.info("  2. Exécuter: python test_mqtt_integration.py")
        logger.info("  3. Vérifier la connexion MQTT")
        return 0
    else:
        logger.error("\n⚠️ Certains tests ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
