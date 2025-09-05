# 🔒 API ObesiTrack - Protégée par JWT

L'API de prédiction d'obésité est maintenant protégée par authentification JWT. Seuls les utilisateurs authentifiés peuvent accéder aux fonctionnalités de prédiction.

## 🚀 Démarrage

### 1. Démarrer l'API d'authentification (port 7777)
```bash
cd App/Back-end
uvicorn main:app --reload --port 7777
```

### 2. Démarrer l'API ML protégée (port 8000)
```bash
cd ModelAi
python run_api.py
```

## 🔐 Authentification

### 1. Connexion pour obtenir un token
```bash
curl -X POST "http://localhost:7777/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password123"
     }'
```

**Réponse :**
```json
{
  "name": "John User",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Utilisation du token
Ajoutez le token dans l'header `Authorization` :
```bash
curl -X GET "http://localhost:8000/model/status" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## 📋 Endpoints Protégés

### 🔒 Endpoints nécessitant une authentification JWT :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/predict` | POST | Prédiction d'obésité personnalisée |
| `/predict/sample` | GET | Prédiction d'exemple |
| `/model/status` | GET | Statut et informations du modèle ML |
| `/user/info` | GET | Informations de l'utilisateur connecté |

### 🌐 Endpoints publics :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil avec documentation |
| `/health` | GET | Vérification de santé de l'API |
| `/docs` | GET | Documentation Swagger UI |

## 🧪 Test de l'API

### Script de test automatique
```bash
cd ModelAi
python test_protected_api.py
```

### Test manuel étape par étape

#### 1. Connexion
```bash
curl -X POST "http://localhost:7777/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password123"
     }'
```

#### 2. Test d'accès protégé
```bash
# Remplacez YOUR_TOKEN par le token reçu
curl -X GET "http://localhost:8000/user/info" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. Prédiction d'obésité
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
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
     }'
```

## ⚠️ Gestion des erreurs

### Token invalide ou expiré
```json
{
  "detail": "Token invalide"
}
```

### Accès sans token
```json
{
  "detail": "Not authenticated"
}
```

### Token manquant
```json
{
  "detail": "Not authenticated"
}
```

## 🔧 Configuration

### Variables d'environnement
L'API utilise les mêmes variables d'environnement que l'API d'authentification :
- `SECRET_KEY` : Clé secrète pour signer les tokens JWT
- `MONGO_URI` : URI de connexion MongoDB
- `DB_NAME` : Nom de la base de données

### Expiration des tokens
- **Durée** : 30 minutes
- **Renouvellement** : Nouvelle connexion requise

## 🛡️ Sécurité

- ✅ **Authentification JWT** obligatoire pour les endpoints sensibles
- ✅ **Validation des tokens** à chaque requête
- ✅ **Expiration automatique** des tokens
- ✅ **Headers sécurisés** (Authorization: Bearer)
- ✅ **Gestion d'erreurs** appropriée

## 📖 Documentation Interactive

- **API ML** : http://localhost:8000/docs
- **API Auth** : http://localhost:7777/docs

## 🚨 Dépannage

### Erreur "Token invalide"
- Vérifiez que le token est correct
- Vérifiez que le token n'a pas expiré (30 minutes)
- Vérifiez le format : `Authorization: Bearer <token>`

### Erreur de connexion
- Vérifiez que l'API d'authentification est démarrée (port 7777)
- Vérifiez que l'API ML est démarrée (port 8000)
- Vérifiez les URLs dans les requêtes

### Erreur "Not authenticated"
- Ajoutez le header `Authorization: Bearer <token>`
- Vérifiez que le token est valide
