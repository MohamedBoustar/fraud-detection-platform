# 📡 INTÉGRATION IoT - MQTT EN TEMPS RÉEL

## Vue d'ensemble

Ce module fournit une intégration MQTT complète pour la détection de fraude en temps réel:

- **Broker MQTT** (Mosquitto) - Centralise les données des capteurs
- **Simulateur de Capteurs** - Génère des données réalistes + anomalies
- **Client MQTT** - Consomme les données et publie les prédictions
- **WebSocket** - Diffuse les prédictions en temps réel au frontend

---

## 📁 Structure du Projet

```
backend/app/iot/
├── __init__.py                    # Exports du module
├── mqtt_client.py                 # Client MQTT asynchrone
└── sensor_simulator.py            # Simulateur de capteurs

mosquitto/
├── config/
│   ├── mosquitto.conf             # Configuration broker
│   └── passwd                     # Credentials MQTT
├── data/                          # Persistence
└── log/                           # Logs
```

---

## 🚀 DÉMARRAGE RAPIDE

### 1️⃣ Démarrer les services Docker

```bash
# Démarrer tous les services (incluant Mosquitto)
docker-compose up -d

# Vérifier que Mosquitto est actif
docker-compose ps | grep mosquitto
```

### 2️⃣ Installer les dépendances Python

```bash
cd backend
pip install -r requirements.txt
```

### 3️⃣ Lancer le simulateur de capteurs

```bash
# Depuis le dossier backend
python -m app.iot.sensor_simulator

# Ou utiliser le script de test
python test_mqtt_integration.py
```

### 4️⃣ Vérifier avec mosquitto_sub

```bash
# Dans un autre terminal
mosquitto_sub -h localhost -p 1883 \
  -u dev -P dev_password \
  -t "sensors/METER_0000"
```

---

## 📊 Configuration MQTT

### Credentials par défaut

```
Username: dev
Password: dev_password
```

### Topics

```
sensors/METER_*           # Données des compteurs (publié par simulateur)
predictions/fraud/*       # Prédictions de fraude (publié par backend)
```

### Paramètres Docker

Définis dans `docker-compose.yml`:

```env
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=dev
MQTT_PASSWORD=dev_password
MQTT_TOPIC_SENSORS=sensors/meter_+
MQTT_TOPIC_PREDICTIONS=predictions/fraud
```

---

## 🔧 Utilisation en Code

### Démarrer le Simulateur

```python
from app.iot import SensorSimulator

simulator = SensorSimulator(
    num_meters=10,              # 10 compteurs
    publish_interval=5,         # 1 message par 5 sec
    anomaly_rate=0.05          # 5% anomalies
)

# Connexion et démarrage
if simulator.connect():
    simulator.run()  # Infini
    # ou
    simulator.run(duration_seconds=300)  # 5 minutes
```

### Recevoir les Données (Backend)

```python
from app.iot import MQTTClient

mqtt = MQTTClient()

def handle_sensor_data(topic, payload):
    print(f"Données du capteur: {payload}")
    # Appliquer le ML ici
    # Publier la prédiction
    mqtt.publish_prediction(
        meter_id=payload['meter_id'],
        is_fraud=True,
        fraud_probability=0.85
    )

mqtt.message_callback = handle_sensor_data
mqtt.connect()
# ... boucle événementielle
```

---

## 📈 Données Simulées

### Format des messages de capteurs

```json
{
  "meter_id": "METER_0000",
  "timestamp": "2025-12-27T14:30:45.123456",
  "consumption_kw": 2.456,
  "voltage_v": 219.85,
  "current_a": 11.234,
  "power_factor": 0.95,
  "frequency_hz": 50,
  "cumulative_energy_kwh": 12543.67,
  "anomaly_score": 0.0,
  "is_night": false,
  "hour": 14
}
```

### Caractéristiques simulées

- **Consommation**: Pattern jour/nuit réaliste
- **Voltage/Courant**: Variance naturelle ±5V, ±2A
- **Anomalies**: Pics 2.5-4x la consommation normale
- **Variabilité**: Gaussienne avec écart-type 20%

---

## 🧪 Tests

### Exécuter la suite complète

```bash
python test_mqtt_integration.py
```

Tests inclus:
1. ✅ Connectivité MQTT
2. ✅ Simulateur de capteurs
3. ✅ Réception des messages

### Tester manuellement

```bash
# Terminal 1: Voir tous les messages
mosquitto_sub -h localhost -t "sensors/#" -v

# Terminal 2: Lancer simulateur
python -m app.iot.sensor_simulator

# Terminal 3: Voir prédictions
mosquitto_sub -h localhost -t "predictions/#" -v
```

---

## 🔒 Sécurité

### Credentials MQTT

Les credentials sont stockés dans `mosquitto/config/passwd`:

```
dev:$7$101$aT0Ecp3PH7m3VJ+u$...
```

Pour changer les passwords:

```bash
docker exec fraud-mosquitto mosquitto_passwd -c /mosquitto/config/passwd dev
docker restart fraud-mosquitto
```

### En Production

⚠️ **NE PAS UTILISER EN PRODUCTION** sans:
- TLS/SSL activé
- Credentials forts
- Firewall configuré
- ACL MQTT restrictive

---

## 📊 Monitoring

### Stats du simulateur

```python
simulator = SensorSimulator(...)
simulator.connect()

# Après quelques secondes
stats = simulator.get_stats()
print(stats)
# {
#   "is_connected": True,
#   "messages_sent": 156,
#   "anomalies_injected": 8,
#   "elapsed_seconds": 45.2,
#   "avg_rate": 3.45,
#   "num_meters": 10
# }
```

### Logs Mosquitto

```bash
docker logs -f fraud-mosquitto
```

---

## ⚙️ Configuration Avancée

### Ajuster la simulation

```python
simulator = SensorSimulator(
    num_meters=50,              # Plus de compteurs
    publish_interval=2,         # Messages plus fréquents
    anomaly_rate=0.1           # Plus d'anomalies
)
```

### Personnaliser les données

Voir `sensor_simulator.py` classe `MeterData`:
- `base_consumption`: Consommation de base (kWh/jour)
- `anomaly_score`: Scoreee d'anomalie (0-1)
- `is_night`: Pattern jour/nuit

---

## 🐛 Dépannage

### Mosquitto ne démarre pas

```bash
# Vérifier les logs
docker logs fraud-mosquitto

# Vérifier le port
netstat -an | grep 1883

# Reconstruire
docker-compose down -v
docker-compose up -d mosquitto
```

### Pas de connexion MQTT

```bash
# Vérifier les credentials
docker exec fraud-mosquitto cat /mosquitto/config/passwd

# Tester manuellement
mosquitto_pub -h localhost -u dev -P dev_password -t test -m "hello"
```

### Simulateur ne publie pas

```bash
# Vérifier MQTT_BROKER variable
echo $MQTT_BROKER  # doit être "mosquitto" dans Docker

# Tester depuis le container
docker exec fraud-backend python -c "
from app.iot import SensorSimulator
s = SensorSimulator()
print(s.connect())
"
```

---

## 📚 Prochaines Étapes

1. ✅ **PHASE 1** - Infrastructure MQTT (ACTUELLE)
2. ⏳ **PHASE 2** - Integration backend (MQTT → Prédictions)
3. ⏳ **PHASE 3** - WebSocket (Temps réel frontend)
4. ⏳ **PHASE 4** - Dashboard temps réel
5. ⏳ **PHASE 5** - Optimisations & scaling

---

## 📖 Ressources

- [Mosquitto MQTT](https://mosquitto.org/)
- [Paho Python Client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [MQTT Protocol](http://mqtt.org/)
- [IoT Best Practices](https://www.iotforall.com/)

---

**Version**: 1.0  
**Date**: 2025-12-27  
**Status**: ✅ En développement (Phase 1)
