# 🏥 API ObesiTrack - Prédiction d'Obésité

API complète en un seul fichier pour la prédiction des catégories d'obésité basée sur des modèles de Machine Learning.

## 🚀 Démarrage Rapide

### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2. Démarrage de l'API
```bash
python start_obesity_api.py
```

L'API sera disponible sur : **http://localhost:8000**

## 📖 Documentation

- **Documentation interactive** : http://localhost:8000/docs
- **Documentation alternative** : http://localhost:8000/redoc

## 🔗 Endpoints Principaux

### 1. Vérification de santé
```
GET /health
```

### 2. Statut du modèle ML
```
GET /model/status
```

### 3. Prédiction d'obésité
```
POST /predict
```

### 4. Exemple de prédiction
```
GET /predict/sample
```

## 📊 Exemple d'utilisation

### Requête de prédiction

```json
POST /predict
{
  "Gender": "Male",
  "Age": 25,
  "Height": 1.75,
  "Weight": 80.0,
  "family_history_with_overweight": "yes",
  "FAVC": "no",
  "FCVC": 2.0,
  "NCP": 3.0,
  "CAEC": "Sometimes",
  "SMOKE": "no",
  "CH2O": 2.0,
  "SCC": "no",
  "FAF": 1.0,
  "TUE": 0.0,
  "CALC": "Sometimes",
  "MTRANS": "Public_Transportation"
}
```

### Réponse

```json
{
  "prediction": "Normal_Weight",
  "confidence": 0.95,
  "risk_level": "Très faible",
  "bmi": 26.12,
  "probabilities": {
    "Insufficient_Weight": 0.01,
    "Normal_Weight": 0.95,
    "Overweight_Level_I": 0.03,
    "Overweight_Level_II": 0.01,
    "Obesity_Type_I": 0.00,
    "Obesity_Type_II": 0.00,
    "Obesity_Type_III": 0.00
  },
  "recommendations": [
    {
      "category": "Maintien",
      "recommendation": "Continuez à maintenir un mode de vie sain avec une alimentation équilibrée",
      "priority": "Low"
    }
  ]
}
```

## 🏷️ Catégories d'Obésité

1. **Insufficient_Weight** - Poids insuffisant
2. **Normal_Weight** - Poids normal
3. **Overweight_Level_I** - Surpoids niveau I
4. **Overweight_Level_II** - Surpoids niveau II
5. **Obesity_Type_I** - Obésité type I
6. **Obesity_Type_II** - Obésité type II
7. **Obesity_Type_III** - Obésité type III

## 📋 Features Requises

### Variables Catégorielles
- **Gender**: Male, Female
- **family_history_with_overweight**: yes, no
- **FAVC**: yes, no (Frequent consumption of high caloric food)
- **CAEC**: no, Sometimes, Frequently, Always (Consumption of food between meals)
- **SMOKE**: yes, no
- **SCC**: yes, no (Calories consumption monitoring)
- **CALC**: no, Sometimes, Frequently, Always (Alcohol consumption)
- **MTRANS**: Automobile, Bike, Motorbike, Public_Transportation, Walking

### Variables Numériques
- **Age**: Âge en années (1-120)
- **Height**: Taille en mètres (0.5-2.5)
- **Weight**: Poids en kilogrammes (10-300)
- **FCVC**: Fréquence de consommation de légumes (1-3)
- **NCP**: Nombre de repas principaux par jour (1-4)
- **CH2O**: Consommation d'eau par jour (1-3)
- **FAF**: Fréquence d'activité physique (0-3)
- **TUE**: Temps d'utilisation d'appareils électroniques (0-2)

## ✨ Fonctionnalités

- ✅ **Entraînement automatique** du modèle au premier démarrage
- ✅ **Prédiction multiclasse** de 7 catégories d'obésité
- ✅ **Validation stricte** des données d'entrée
- ✅ **Recommandations de santé** personnalisées
- ✅ **Calcul automatique de l'IMC**
- ✅ **Niveaux de confiance** et probabilités
- ✅ **API RESTful** avec documentation interactive
- ✅ **Gestion d'erreurs** robuste
- ✅ **Tout en un seul fichier** - Facile à déployer

## 🏥 Utilisation Médicale

⚠️ **Important** : Cette API est destinée à des fins éducatives et de recherche. Pour toute utilisation médicale réelle, consultez toujours un professionnel de santé qualifié.

## 🐛 Dépannage

### Erreur "Data.csv non trouvé"
- Assurez-vous que le fichier `Data.csv` est présent dans le dossier `ModelAi/`

### Erreur de port déjà utilisé
- Changez le port dans le script de démarrage
- Ou arrêtez le processus utilisant le port 8000

### Erreur d'importation
- Vérifiez que toutes les dépendances sont installées : `pip install -r requirements.txt`
