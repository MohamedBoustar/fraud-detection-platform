# Plateforme de Détection de Fraude Électrique

Plateforme complète de détection de fraude électrique utilisant Machine Learning, IoT et architecture full-stack.

## Description

Ce projet développe une solution intégrée pour détecter les fraudes de consommation électrique en utilisant un modèle LightGBM entraîné sur le dataset SGCC (42,372 clients sur 3 ans). La plateforme combine analyse batch et détection temps réel via MQTT.

## Objectifs

- Préparer et analyser les données de consommation électrique
- Développer un modèle ML performant (71.6% Recall)
- Créer une API REST avec FastAPI
- Concevoir une interface React interactive
- Intégrer la détection temps réel via IoT/MQTT
- Stocker les données sur AWS S3 et PostgreSQL
- Déployer avec Docker Compose

## Stack Technologique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Backend | FastAPI (Python) | API REST + WebSocket |
| Frontend | React 18 + Vite | Interface utilisateur |
| Base de données | PostgreSQL 15 | Stockage prédictions |
| Stockage Cloud | AWS S3 | Fichiers CSV |
| Message Broker | Mosquitto MQTT | Communication IoT |
| ML Engine | LightGBM | Modèle prédiction |
| Containerisation | Docker Compose | Orchestration |

## Architecture

```
┌─────────────────────────────────────────────┐
│         DOCKER COMPOSE NETWORK              │
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │  Frontend    │  │   Backend    │        │
│  │  React:5173  │→│ FastAPI:8000 │        │
│  └──────────────┘  └──────┬───────┘        │
│                           │                │
│  ┌──────────────────────────┴────────────┐ │
│  │                                       │ │
│  ▼                ▼                  ▼   │
│ ┌────────────┐ ┌──────────────┐ ┌──────┐ │
│ │ PostgreSQL │ │  Mosquitto   │ │ ML   │ │
│ │  :5432     │ │  :1883       │ │ Model│ │
│ └────────────┘ └──────────────┘ └──────┘ │
│                                             │
└─────────────────────────────────────────────┘
        IoT Simulator / Capteurs
```

## Installation

### Prérequis

- Docker et Docker Compose
- Python 3.9+
- Node.js 18+
- AWS S3 (optionnel)

### Déploiement avec Docker

```bash
cd fraud-detection-platform
docker-compose up -d
```

Services lancés:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Mosquitto: localhost:1883

### Installation manuelle

Backend:
```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Modèle Machine Learning

### Dataset
- Source: State Grid Corporation of China (SGCC)
- Clients: 42,372
- Période: 01/01/2014 - 31/10/2016 (3 ans)
- Colonnes: 1,036 (CONS_NO + 1,033 jours + FLAG)
- Déséquilibre: 91.47% Normal vs 8.53% Fraudeurs

### Features (15 total)
- Statistiques de base: mean, std, median, max, cv (5)
- Détection zéros: zero_days, zero_ratio (2)
- Temporelles: trend, n_peaks, max_consecutive_zeros (3)
- Distribution: skewness, kurtosis, q25, q75, iqr (5)

### Performances du Modèle

| Métrique | Valeur |
|----------|--------|
| Recall | 71.6% |
| Precision | 16.9% |
| F1-Score | 0.278 |
| AUC-ROC | 0.780 |
| Accuracy | 68.3% |

**Modèle sélectionné**: LightGBM avec Undersampling

**Stratégie**: Privilégie le Recall pour maximiser la détection des fraudeurs (518/723 détectés).

## Pages de l'Application

1. **Dashboard**: Vue d'ensemble avec statistiques globales et graphiques
2. **Batch**: Upload CSV et analyse en masse de clients
3. **Realtime**: Monitoring temps réel des capteurs IoT via WebSocket
4. **History**: Historique complet des analyses batch
5. **Client Details**: Profil détaillé d'un client avec features et tendances

## API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| /api/predict/batch | POST | Prédiction batch CSV |
| /api/predict/single | POST | Prédiction simple client |
| /api/clients | GET | Liste clients |
| /api/history | GET | Historique prédictions |
| /ws/realtime | WebSocket | Flux temps réel |

## Analyse des Données

### Valeurs Manquantes
- Global: 25.64% NaN
- Normaux: 264 jours manquants/client
- Fraudeurs: 329 jours manquants/client (+65 jours)

Stratégie: Imputation par 0 (hypothèse = compteur trafiqué)

### Profil du Fraudeur
- Consommation: +227% plus élevée
- Jours à zéro: +45% plus fréquents
- Zéros consécutifs: +110% plus longs
- Variabilité: +275% plus élevée

## Fichier Project Structure

```
fraud-detection-platform/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI entry point
│       ├── api/predictions.py    # Endpoints
│       ├── ml/
│       │   ├── predictor.py     # ML inference
│       │   ├── preprocessing.py  # Feature engineering
│       │   └── models/           # Modèles sauvegardés
│       ├── iot/
│       │   ├── mqtt_client.py
│       │   └── sensor_simulator.py
│       └── services/
│           ├── cloud_storage.py  # AWS S3
│           └── db_service.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── pages/
│       ├── components/
│       └── services/
├── mosquitto/
│   └── config/mosquitto.conf
├── notebooks/
│   ├── 1_data_preparation_feature_engineering.ipynb
│   └── 2_model_training_evaluation.ipynb
└── rapport/
    └── rapport_resume.tex       # Rapport technique
```

## Dépendances

### Backend
- fastapi, uvicorn
- scikit-learn, lightgbm, xgboost, imbalanced-learn
- pandas, numpy, scipy
- sqlalchemy, psycopg2-binary
- boto3 (AWS S3)
- paho-mqtt

### Frontend
- react@18.2.0
- recharts (graphiques)
- axios (requêtes HTTP)
- tailwindcss (styling)
- vite (build tool)

## Configuration

### Variables d'environnement (backend/.env)
```
DATABASE_URL=postgresql://fraud_user:fraud_password@postgres:5432/fraud_detection
AWS_ACCESS_KEY_ID=votre_cle
AWS_SECRET_ACCESS_KEY=votre_secret
AWS_BUCKET_NAME=votre_bucket
MQTT_BROKER_URL=mosquitto
MQTT_BROKER_PORT=1883
```

### PostgreSQL
- User: fraud_user
- Password: fraud_password
- Database: fraud_detection

## Utilisation

### Prédiction Batch
```bash
curl -X POST "http://localhost:8000/api/predict/batch" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@clients.csv" \
  -F "threshold=0.5"
```

### Prédiction Simple
```bash
curl -X POST "http://localhost:8000/api/predict/single" \
  -H "Content-Type: application/json" \
  -d '{"mean_consumption": 5.77, "std_consumption": 12.4, ...}'
```

### WebSocket Temps Réel
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/realtime');
ws.onmessage = (event) => {
  const prediction = JSON.parse(event.data);
  console.log(prediction);
};
```

## Rapport Technique

Un rapport complet (30 pages) est disponible en LaTeX: `rapport/rapport_resume.tex`

Couverture:
- Chapitre 1: Introduction et contexte
- Chapitre 2: Architecture technique
- Chapitre 3: Analyse et préparation des données
- Chapitre 4: Feature engineering
- Chapitre 5: Modélisation ML
- Chapitre 6: Intégration et déploiement
- Chapitre 7: Démonstration interface utilisateur
- Chapitre 8: Conclusion

## Résultats et Impact

- Détection: 518/723 fraudeurs (71.6%)
- Économies potentielles: ~518,000 EUR/an (au coût moyen de 1,000 EUR par fraudeur)
- Fausses alertes: 2,480 (à investiguer par équipe terrain)
- Temps d'inférence: < 100ms par client

## Perspectives d'Amélioration

- Enrichissement des données: météo, profil client, historique paiement
- Deep Learning: LSTM ou Transformer pour séries temporelles
- Système de feedback: amélioration continue
- Détection d'anomalies: Isolation Forest
- Déploiement cloud: AWS ECS ou Kubernetes

## Auteur

Mohamed Boustar



## Établissement

École Nationale des Sciences Appliquées d'Oujda // 
Filière: Ingénierie Data Science & Cloud Computing (IDSCC)



