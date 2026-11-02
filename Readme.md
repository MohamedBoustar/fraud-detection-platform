# Fraud Detection Platform

> Plateforme intelligente de détection de fraude électrique combinant Machine Learning, IoT, MQTT et application web full-stack.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=20232A)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

## Présentation

**Fraud Detection Platform** est une solution de supervision et d’analyse de la consommation électrique. Elle permet de :

- analyser un fichier CSV contenant les consommations de plusieurs clients ;
- calculer automatiquement des indicateurs statistiques et temporels ;
- détecter les profils susceptibles de présenter une fraude ;
- recevoir des mesures IoT en temps réel via MQTT ;
- diffuser les prédictions instantanément dans une interface WebSocket ;
- conserver l’historique des analyses dans PostgreSQL ;
- visualiser les résultats dans une interface React moderne.

Le modèle de classification utilisé est un modèle **LightGBM**, entraîné sur le dataset SGCC (*State Grid Corporation of China*).

## Fonctionnalités

### Analyse batch

- Import d’un fichier CSV ;
- validation de la structure et du nombre de jours disponibles ;
- calcul de 15 features de consommation ;
- prédiction individuelle pour chaque client ;
- seuil de décision configurable ;
- classement par niveau de risque ;
- sauvegarde des résultats en base de données ;
- stockage optionnel du fichier source sur Amazon S3.

### Surveillance temps réel

- simulation de compteurs électriques ;
- publication des mesures via Mosquitto MQTT ;
- consommation des messages par le backend ;
- prédiction en temps réel ;
- transmission des alertes via WebSocket ;
- affichage des compteurs, scores et niveaux de risque dans le dashboard.

### Historique et suivi

- historique des fichiers analysés ;
- détail des prédictions d’un batch ;
- historique par client ;
- statistiques globales ;
- indicateurs de fraude et de risque.

## Architecture

```text
                         +----------------------+
                         |  Interface React     |
                         |  Vite - port 5173   |
                         +----------+-----------+
                                    |
                         REST API / WebSocket
                                    |
                         +----------v-----------+
                         |  Backend FastAPI     |
                         |  port 8000           |
                         +----+------------+----+
                              |            |
                    +---------v--+   +-----v------+
                    | PostgreSQL |   | ML Engine  |
                    | Historique |   | LightGBM   |
                    +------------+   +------------+
                              ^
                              |
                    +---------+----------+
                    | Mosquitto MQTT     |
                    | port 1883          |
                    +---------+----------+
                              ^
                              |
                    +---------+----------+
                    | Simulateur IoT     |
                    | Compteurs virtuels |
                    +--------------------+
```

## Technologies

| Domaine | Technologies |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Machine Learning | LightGBM, scikit-learn, pandas, NumPy, SciPy |
| Base de données | PostgreSQL, SQLAlchemy |
| IoT et messaging | MQTT, Eclipse Mosquitto, Paho MQTT |
| Frontend | React, Vite, Axios, Recharts |
| Temps réel | WebSocket natif FastAPI |
| Stockage optionnel | Amazon S3 avec boto3 |
| Déploiement | Docker, Docker Compose |

## Prérequis

- Docker Desktop et Docker Compose ;
- Git ;
- Python 3.11 ou version compatible avec les dépendances ;
- Node.js 18+ pour une installation locale ;
- AWS S3 uniquement si le stockage cloud est activé.

## Installation avec Docker

Clonez le dépôt puis démarrez les services :

```bash
git clone https://github.com/MohamedBoustar/fraud-detection-platform.git
cd fraud-detection-platform
docker compose up --build
```

Les services sont ensuite disponibles à l’adresse suivante :

| Service | Adresse |
|---|---|
| Application frontend | http://localhost:5173 |
| API backend | http://localhost:8000 |
| Documentation Swagger | http://localhost:8000/docs |
| Documentation ReDoc | http://localhost:8000/redoc |
| PostgreSQL | localhost:5432 |
| MQTT | localhost:1883 |

Pour arrêter les services :

```bash
docker compose down
```

Pour supprimer également les données PostgreSQL persistées :

```bash
docker compose down -v
```

## Installation locale

### Backend

```bash
cd backend
python -m venv venv
```

Sous Windows :

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

Dans un autre terminal :

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Copiez [.env.example](./.env.example) vers `.env`, puis adaptez les valeurs à votre environnement. Ne publiez jamais le fichier `.env`.

Variables principales :

```env
DATABASE_URL=postgresql://fraud_user:fraud_password@postgres:5432/fraud_detection
DEBUG=True
API_PORT=8000
SECRET_KEY=change-this-secret
VITE_API_URL=http://localhost:8000
```

Configuration AWS S3 facultative :

```env
USE_S3_STORAGE=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=eu-west-3
AWS_BUCKET_NAME=
```

En environnement Docker, les services utilisent les noms `postgres` et `mosquitto` comme noms d’hôtes internes.

## Format du fichier CSV

Le fichier doit contenir :

- une colonne `CONS_NO` identifiant chaque client ;
- au moins 7 colonnes de consommation journalière ;
- une colonne `FLAG` facultative, utile pour l’analyse et la validation.

Exemple :

```csv
CONS_NO,2024-01-01,2024-01-02,2024-01-03,2024-01-04,2024-01-05,2024-01-06,2024-01-07
CN_0001,12.5,15.3,8.2,10.4,11.8,9.7,13.1
CN_0002,0.0,0.0,156.8,0.0,0.0,142.4,0.0
```

Un fichier de démonstration est disponible dans [demo_batch.csv](./demo_batch.csv).

## Features du modèle

Le preprocessing est implémenté dans [preprocessing.py](./backend/app/ml/preprocessing.py).

| Catégorie | Features |
|---|---|
| Statistiques | moyenne, écart-type, médiane, maximum |
| Variabilité | coefficient de variation, IQR |
| Zéros | nombre de jours à zéro, ratio de zéros, séquence maximale |
| Temporalité | tendance, nombre de pics |
| Distribution | skewness, kurtosis, Q25, Q75 |

Les artefacts du modèle sont chargés depuis `backend/app/ml/models/` :

```text
fraud_detection_model.pkl
scaler.pkl
```

Ces fichiers sont exclus du suivi Git par défaut. Ils doivent être fournis séparément lors d’un déploiement.

## API principale

Toutes les routes de prédiction utilisent le préfixe `/api/predictions`.

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Santé générale de l’API |
| `GET` | `/api/predictions/health` | État du service ML |
| `GET` | `/api/predictions/model/info` | Informations du modèle |
| `GET` | `/api/predictions/model/features` | Liste des features |
| `POST` | `/api/predictions/batch` | Analyse d’un fichier CSV |
| `POST` | `/api/predictions/realtime` | Prédiction à partir de features |
| `GET` | `/api/predictions/batches` | Liste des analyses batch |
| `GET` | `/api/predictions/batch/{batch_id}` | Détail d’un batch |
| `GET` | `/api/predictions/history/{cons_no}` | Historique d’un client |
| `GET` | `/api/predictions/stats` | Statistiques globales |
| `DELETE` | `/api/predictions/batch/{batch_id}` | Suppression d’un batch |
| `GET` | `/api/realtime/stats` | Statistiques MQTT/WebSocket |
| `GET` | `/api/realtime/history` | Historique temps réel |
| `WebSocket` | `/ws/realtime` | Flux des prédictions IoT |

Exemple d’analyse batch avec PowerShell :

```powershell
curl.exe -X POST "http://localhost:8000/api/predictions/batch?threshold=0.5" `
  -F "file=@demo_batch.csv"
```

Exemple de connexion WebSocket :

```javascript
const socket = new WebSocket("ws://localhost:8000/ws/realtime");

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
};
```

## Structure du projet

```text
fraud-detection-platform/
├── backend/
│   ├── app/
│   │   ├── api/                 # Routes FastAPI
│   │   ├── database/            # Connexion et initialisation DB
│   │   ├── iot/                 # Client MQTT et simulateur
│   │   ├── ml/                  # Preprocessing et prédiction
│   │   ├── models/              # Modèles SQLAlchemy
│   │   └── services/            # DB, S3, MQTT et temps réel
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Composants React
│   │   ├── hooks/               # Hooks temps réel
│   │   ├── pages/               # Pages de l’application
│   │   └── services/            # Client API
│   ├── package.json
│   └── Dockerfile
├── mosquitto/
│   └── config/                  # Configuration du broker MQTT
├── notebooks/                   # Préparation et entraînement ML
├── docker-compose.yml
├── demo_batch.csv
└── rapport_projet_tutore.tex
```

## Résultats du modèle

Les métriques obtenues lors de l’évaluation sont :

| Métrique | Résultat |
|---|---:|
| Recall | 71,6 % |
| Precision | 16,9 % |
| F1-score | 0,278 |
| AUC-ROC | 0,780 |
| Accuracy | 68,3 % |

Le modèle privilégie le **recall** afin de limiter le nombre de fraudes manquées. Les alertes produites doivent donc être interprétées comme une aide à l’investigation, et non comme une preuve définitive de fraude.

## Notebooks et documentation

- [Préparation et feature engineering](./notebooks/1_data_preparation_feature_engineering.ipynb)
- [Entraînement et évaluation](./notebooks/2_model_training_evaluation.ipynb)
- [Rapport technique LaTeX](./rapport_projet_tutore.tex)
- [Rapport PDF](./Rapport_Mo_Boustar_iot.pdf)
- [Présentation finale](./Presentation_Finale_Iot.pdf)

## Sécurité et bonnes pratiques

- Ne jamais versionner `.env`, les mots de passe ou les clés AWS.
- Remplacer les identifiants de développement avant toute mise en production.
- Désactiver le mode `DEBUG` en production.
- Configurer une authentification MQTT adaptée à l’environnement cible.
- Protéger l’API et le WebSocket derrière HTTPS/WSS en production.
- Ne pas considérer automatiquement une prédiction comme une décision métier.

## Limites actuelles

- Le simulateur IoT est destiné à la démonstration.
- Le stockage temps réel doit être renforcé pour un usage industriel.
- Les fichiers du modèle ML doivent être distribués séparément.
- L’authentification utilisateur et la gestion des rôles restent à ajouter.
- Le système nécessite une validation sur des données opérationnelles réelles.

## Perspectives

- Ajouter une authentification JWT et une gestion des rôles ;
- intégrer un système de feedback des équipes terrain ;
- enrichir les données avec la météo, le calendrier et l’historique client ;
- améliorer la détection par des modèles temporels ou non supervisés ;
- ajouter des notifications e-mail et SMS ;
- préparer un déploiement cloud avec AWS ECS ou Kubernetes.

## Auteur

**Mohamed Boustar**

Projet réalisé dans le cadre d’un projet tutoré à l’École Nationale des Sciences Appliquées d’Oujda.

## Licence

Projet académique. Tous droits réservés à l’auteur, sauf indication contraire.
