# 🔍 Fraud Detection Platform

Plateforme de détection de fraude électrique par analyse de profils de consommation.

**Projet académique** - École Nationale des Sciences Appliquées d'Oujda (ENSAO)  
**Filière:** Ingénierie Data Science & Cloud Computing (IDSCC) - 3ème année  
**Année:** 2025-2026

---

## 📋 Description

Application web de détection de fraude électrique utilisant le Machine Learning pour identifier les consommateurs ayant des profils de consommation anormaux. Le système analyse les données de consommation historiques et génère des prédictions en temps réel.

### Fonctionnalités principales
- 📤 Upload et analyse de fichiers CSV (mode batch)
- 🔴 Détection en temps réel via WebSocket
- 📊 Dashboard avec statistiques et visualisations
- 👤 Profils détaillés des clients suspects
- 📜 Historique des prédictions
- 💬 Système de feedback (validation des prédictions)

---

## 🐳 Démarrage avec Docker

### Prérequis
- Docker Desktop installé et démarré
- Docker Compose v2+
- Git

### Installation rapide
```bash
# 1. Clone le projet
git clone https://github.com/TON_USERNAME/fraud-detection-platform.git
cd fraud-detection-platform

# 2. Configure les variables d'environnement
cp .env.example .env
# Édite .env avec tes valeurs si nécessaire

# 3. Place les modèles ML
# Copie tes fichiers dans backend/app/ml/models/ :
# - fraud_detection_model.pkl
# - scaler.pkl

# 4. Lance l'application (tous les services)
docker-compose up -d

# 5. Vérifie que tout tourne
docker-compose ps
```

### Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Interface React |
| **Backend API** | http://localhost:8000 | API FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentation Swagger |
| **PostgreSQL** | localhost:5432 | Base de données |

---

## 🛠️ Commandes Docker utiles
```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs backend
docker-compose logs frontend

# Arrêter tous les services
docker-compose down

# Arrêter + supprimer volumes (⚠️ efface la DB)
docker-compose down -v

# Redémarrer un service
docker-compose restart backend

# Rebuild après modification
docker-compose build
docker-compose up -d

# Accéder au shell d'un container
docker exec -it fraud-backend bash
docker exec -it fraud-frontend sh
```

---

## 📊 Architecture
```
fraud-detection-platform/
├── backend/              # API FastAPI + Machine Learning
│   ├── app/
│   │   ├── api/         # Endpoints REST
│   │   ├── ml/          # Modèles ML + Preprocessing
│   │   ├── models/      # Modèles de données
│   │   ├── services/    # Logique métier
│   │   └── main.py      # Point d'entrée FastAPI
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/             # Application React
│   ├── src/
│   │   ├── components/  # Composants réutilisables
│   │   ├── pages/       # Pages de l'app
│   │   ├── services/    # Appels API
│   │   └── App.jsx
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml    # Orchestration des services
├── .env.example          # Template de configuration
└── README.md
```

---

## 🚀 Technologies utilisées

### Backend
- **FastAPI** - Framework web moderne et rapide
- **LightGBM** - Modèle de classification gradient boosting
- **Scikit-learn** - Preprocessing et feature engineering
- **PostgreSQL** - Base de données relationnelle
- **SQLAlchemy** - ORM Python
- **Pydantic** - Validation des données

### Frontend
- **React 18** - Bibliothèque UI
- **Vite** - Build tool rapide
- **TailwindCSS** - Framework CSS utility-first
- **Axios** - Client HTTP
- **Socket.IO** - Communication temps réel
- **Recharts** - Visualisations de données

### Infrastructure
- **Docker** - Conteneurisation
- **Docker Compose** - Orchestration multi-containers
- **PostgreSQL 15** - Base de données

---

## 📈 Modèle Machine Learning

### Features utilisées (15)
1. **Statistiques de base**: mean, std, median, max
2. **Métriques dérivées**: cv (coefficient de variation), iqr
3. **Détection de zéros**: zero_days, zero_ratio, max_consecutive_zeros
4. **Analyse temporelle**: trend, n_peaks
5. **Distribution**: skewness, kurtosis, quartiles (q25, q75)

### Performance
- **Recall**: 71.6% (détecte 72% des fraudeurs)
- **AUC**: 0.780
- **Méthode**: Undersampling + LightGBM

---

## 👤 Auteur

**[Ton Nom]**  
Étudiant en 3ème année - Ingénierie Data Science & Cloud Computing  
École Nationale des Sciences Appliquées d'Oujda (ENSAO)

---

## 📅 Période de développement

Septembre - Décembre 2025

---

## 📄 Licence

Projet académique - ENSAO 2025