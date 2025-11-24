# 📓 Notebooks - Fraud Detection ML Development

Ce dossier contient les notebooks Jupyter utilisés pour développer le modèle de Machine Learning.

---

## 📚 Liste des Notebooks

### **1️⃣ Notebook 1 : Data Preparation & Feature Engineering**
**Fichier** : `1_data_preparation_feature_engineering.ipynb`

**Objectif** : Analyser le dataset SGCC, nettoyer les données et créer les features ML

**Contenu** :
- **Partie 1** : Compréhension du Dataset
  - Chargement du dataset (42,372 clients × 1,036 colonnes)
  - Analyse descriptive (shape, types, statistiques)
  - Distribution de la variable cible FLAG (91.47% Normal, 8.53% Fraudeur)

- **Partie 2** : Détection des Valeurs Manquantes
  - Analyse des NaN (25.64% du dataset)
  - Comparaison Fraudeurs vs Normaux (+65 jours de NaN pour fraudeurs)
  - Imputation par 0 (stratégie : "pas de donnée = pas de consommation")

- **Partie 3** : Feature Engineering (1034 → 18 features)
  - Statistiques basiques (mean, std, median, min, max, total)
  - Métriques dérivées (cv, range, iqr)
  - Détection des zéros (zero_days, zero_ratio)
  - Analyse temporelle (trend, n_peaks, max_consecutive_zeros)
  - Distribution (skewness, kurtosis, q25, q75)

- **Partie 4** : Comparaison Profils Fraudeurs vs Normaux
  - Fraudeurs : +227% consommation moyenne (18.87 kWh vs 5.77 kWh)
  - Fraudeurs : +275% variabilité (comportement erratique)
  - Fraudeurs : +211% pics maximums (427 kWh vs 137 kWh)
  - Insight clé : Fraudeurs consomment beaucoup mais paient peu (compteur trafiqué)

- **Partie 5** : Nettoyage des Features Redondantes
  - Détection corrélations > 0.9
  - Suppression : total_consumption, range_consumption, min_consumption
  - Résultat final : 15 features optimisées

**Durée estimée** : 1-2 heures

**Dataset utilisé** : `data/raw/client_data.csv`

**Output** : `data/processed/features_engineered.csv`

---

### **2️⃣ Notebook 2 : Model Training & Evaluation**
**Fichier** : `2_model_training_evaluation.ipynb`

**Objectif** : Entraîner et évaluer les modèles ML pour sélectionner le meilleur

**Contenu** :
- **Partie 1** : Chargement & Analyse Rapide
  - Import des features (42,372 × 15)
  - Vérification dataset (shape, NaN, corrélations)
  - Distribution FLAG (déséquilibre confirmé)

- **Partie 2** : Gestion des Valeurs Manquantes
  - Imputation skewness/kurtosis par 0
  - Vérification post-imputation (0 NaN)

- **Partie 3** : Séparation X/y & Split
  - X = 15 features, y = FLAG
  - Train/Test 80/20 (stratifié)
  - Train : 33,897 clients (2,892 fraudeurs)
  - Test : 8,475 clients (723 fraudeurs)

- **Partie 4** : Normalisation
  - StandardScaler (mean=0, std=1)
  - Fit sur train, transform sur test

- **Partie 5** : Gestion du Déséquilibre
  - **Méthode 1** : SMOTE (62,010 clients, 50/50)
  - **Méthode 2** : Random Undersampling (5,784 clients, 50/50) ⭐
  - **Méthode 3** : SMOTE-Tomek (61,274 clients, 50/50)

- **Partie 6** : Entraînement des Modèles
  - 5 algorithmes testés :
    - Logistic Regression
    - Random Forest
    - XGBoost
    - LightGBM ⭐ (GAGNANT)
    - MLP (Neural Network)
  - 3 datasets × 5 modèles = 15 combinaisons
  - **Résultat** : Undersampling + LightGBM (Recall 71.6%)

- **Partie 7** : Analyse Approfondie
  - Matrice de confusion (518/723 fraudeurs détectés)
  - Top 3 features :
    1. max_consecutive_zeros (importance 374)
    2. trend (importance 300)
    3. zero_days (importance 289)
  - Analyse seuils de décision (0.3, 0.5, 0.7)
  - Courbe ROC (AUC = 0.780)

- **Partie 8** : Optimisation (Grid Search)
  - Tuning hyperparamètres LightGBM
  - Résultat : Paramètres par défaut déjà optimaux
  - Pas d'amélioration après Grid Search

- **Partie 9** : Sauvegarde des Modèles
  - fraud_detection_model.pkl (LightGBM)
  - scaler.pkl (StandardScaler)

**Durée estimée** : 2-3 heures

**Dataset utilisé** : `data/processed/features_engineered.csv`

**Output** :
- `backend/app/ml/models/fraud_detection_model.pkl`
- `backend/app/ml/models/scaler.pkl`

---

## 📊 Métriques Finales

### **Modèle Sélectionné : Undersampling + LightGBM**

| Métrique | Valeur |
|----------|--------|
| **Recall** | 71.6% (518/723 fraudeurs détectés) |
| **Precision** | 16.9% |
| **F1-Score** | 0.278 |
| **AUC-ROC** | 0.780 |
| **Accuracy** | 68.3% |

### **Trade-off Business**
- ✅ **518 fraudeurs détectés** (71.6% Recall)
- ❌ **205 fraudeurs manqués** (28.4% Faux Négatifs)
- ⚠️ **2,480 fausses alertes** (Faux Positifs)

→ **Décision** : Privilégier le Recall (détecter un maximum de fraudeurs) au détriment de la Precision

---

## 🔧 Environnement Python

### **Librairies Requises**

```bash
# Installation des dépendances notebooks
pip install jupyter notebook
pip install pandas numpy matplotlib seaborn
pip install scikit-learn lightgbm xgboost
pip install imbalanced-learn  # Pour SMOTE
```

### **Lancer Jupyter**

```bash
# Depuis le dossier notebooks/
jupyter notebook
```

---

## 📁 Données Requises

### **Fichiers nécessaires**

1. **Dataset brut** : `../data/raw/client_data.csv`
   - Format : 42,372 lignes × 1,036 colonnes
   - Colonnes : CONS_NO + 1033 jours de consommation + FLAG

2. **Dataset avec features** : `../data/processed/features_engineered.csv`
   - Format : 42,372 lignes × 17 colonnes
   - Colonnes : CONS_NO + 15 features + FLAG

---

## 🎯 Utilisation

### **Ordre d'exécution**

1. **Notebook 1** : Data Preparation & Feature Engineering
   - Input : `client_data.csv` (dataset brut)
   - Output : `features_engineered.csv` (15 features)

2. **Notebook 2** : Model Training & Evaluation
   - Input : `features_engineered.csv`
   - Output : 
     - `fraud_detection_model.pkl`
     - `scaler.pkl`

### **Exécution Complète**

```bash
# 1. Naviguer vers notebooks
cd notebooks/

# 2. Lancer Jupyter
jupyter notebook

# 3. Ouvrir et exécuter dans l'ordre :
#    → 1_data_preparation_feature_engineering.ipynb
#    → 2_model_training_evaluation.ipynb
```

---

## 📝 Notes Importantes

### **Dataset SGCC**
- **Source** : State Grid Corporation of China
- **Période** : 01/01/2014 → 31/10/2016 (presque 3 ans)
- **Clients** : 42,372 (résidentiels et industriels)
- **Étiquettes** : 
  - 0 = Normal (91.47%)
  - 1 = Fraudeur (8.53%)

### **Logique de Détection**
Les fraudeurs ont typiquement :
- ❌ Beaucoup de jours à 0 kWh (compteur trafiqué)
- ❌ Consommation très erratique (CV élevé)
- ❌ Tendance anormale (baisse suspecte)
- ❌ Longues séquences de zéros (max_consecutive_zeros élevé)

### **Features les Plus Importantes**
1. **max_consecutive_zeros** (374) → Jours consécutifs à 0 kWh
2. **trend** (300) → Tendance de consommation
3. **zero_days** (289) → Nombre total de jours à 0

---

## 🚀 Intégration avec le Projet

Les modèles entraînés dans ces notebooks sont utilisés dans le backend :

```python
# backend/app/ml/predictor.py
import pickle

# Charger les modèles sauvegardés
model = pickle.load(open('models/fraud_detection_model.pkl', 'rb'))
scaler = pickle.load(open('models/scaler.pkl', 'rb'))

# Prédiction
X_scaled = scaler.transform(features)
predictions = model.predict(X_scaled)
probabilities = model.predict_proba(X_scaled)[:, 1]
```

---

## 📚 Références

- **Dataset** : [SGCC Fraud Detection Dataset](https://www.kaggle.com/datasets)
- **LightGBM** : [Documentation](https://lightgbm.readthedocs.io/)
- **SMOTE** : [imbalanced-learn](https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html)
- **Scikit-learn** : [Documentation](https://scikit-learn.org/)

---

## 👤 Auteur

**Hamito (Mohamed Boustar)**
- Programme : 3ème année IDSCC, ENSAO
- Module : Internet of Things (IoT)
- Professeur : K. AZGHIOU
- Date : Novembre 2025

---

## 📄 Licence

Ce projet est développé dans un cadre académique (ENSAO, 2025).