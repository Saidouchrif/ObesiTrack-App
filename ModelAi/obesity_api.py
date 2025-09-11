from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import warnings
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Chargement des variables d'environnement
load_dotenv()

# Configuration JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Schéma de sécurité
security = HTTPBearer()

# ==================== FONCTIONS D'AUTHENTIFICATION JWT ====================

def verify_token(token: str):
    """Vérifie et décode un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dépendance pour obtenir l'utilisateur actuel à partir du token JWT"""
    token = credentials.credentials
    email = verify_token(token)
    return {"email": email}

# ==================== MODÈLES PYDANTIC ====================

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class FamilyHistoryEnum(str, Enum):
    YES = "yes"
    NO = "no"

class FAVCEnum(str, Enum):
    YES = "yes"
    NO = "no"

class CAECEnum(str, Enum):
    NO = "no"
    SOMETIMES = "Sometimes"
    FREQUENTLY = "Frequently"
    ALWAYS = "Always"

class SmokeEnum(str, Enum):
    YES = "yes"
    NO = "no"

class SCCEnum(str, Enum):
    YES = "yes"
    NO = "no"

class CALCEnum(str, Enum):
    NO = "no"
    SOMETIMES = "Sometimes"
    FREQUENTLY = "Frequently"
    ALWAYS = "Always"

class MTRANSEnum(str, Enum):
    AUTOMOBILE = "Automobile"
    BIKE = "Bike"
    MOTORBIKE = "Motorbike"
    PUBLIC_TRANSPORTATION = "Public_Transportation"
    WALKING = "Walking"

class ObesityPredictionRequest(BaseModel):
    """Modèle pour la requête de prédiction d'obésité"""
    
    Gender: GenderEnum = Field(..., description="Genre de la personne")
    Age: int = Field(..., ge=1, le=120, description="Âge en années")
    Height: float = Field(..., gt=0, le=3.0, description="Taille en mètres")
    Weight: float = Field(..., gt=0, le=300, description="Poids en kilogrammes")
    family_history_with_overweight: FamilyHistoryEnum = Field(..., description="Antécédents familiaux d'obésité")
    FAVC: FAVCEnum = Field(..., description="Consommation fréquente d'aliments riches en calories")
    FCVC: float = Field(..., ge=1, le=3, description="Fréquence de consommation de légumes (1-3)")
    NCP: float = Field(..., ge=1, le=4, description="Nombre de repas principaux par jour (1-4)")
    CAEC: CAECEnum = Field(..., description="Consommation d'aliments entre les repas")
    SMOKE: SmokeEnum = Field(..., description="Fumeur")
    CH2O: float = Field(..., ge=1, le=3, description="Consommation d'eau par jour (1-3)")
    SCC: SCCEnum = Field(..., description="Surveillance des calories consommées")
    FAF: float = Field(..., ge=0, le=3, description="Fréquence d'activité physique (0-3)")
    TUE: float = Field(..., ge=0, le=2, description="Temps d'utilisation d'appareils électroniques (0-2)")
    CALC: CALCEnum = Field(..., description="Consommation d'alcool")
    MTRANS: MTRANSEnum = Field(..., description="Moyen de transport principal")

    @validator('Height')
    def validate_height(cls, v):
        if v < 0.5 or v > 2.5:
            raise ValueError('La taille doit être entre 0.5 et 2.5 mètres')
        return v

    @validator('Weight')
    def validate_weight(cls, v):
        if v < 10 or v > 300:
            raise ValueError('Le poids doit être entre 10 et 300 kg')
        return v

    @validator('Age')
    def validate_age(cls, v):
        if v < 1 or v > 120:
            raise ValueError('L\'âge doit être entre 1 et 120 ans')
        return v

class HealthRecommendation(BaseModel):
    """Modèle pour une recommandation de santé"""
    
    category: str = Field(..., description="Catégorie de la recommandation")
    recommendation: str = Field(..., description="Texte de la recommandation")
    priority: str = Field(..., description="Priorité (High, Medium, Low)")

class ObesityPredictionResponse(BaseModel):
    """Modèle pour la réponse de prédiction d'obésité"""
    
    prediction: str = Field(..., description="Catégorie d'obésité prédite")
    confidence: float = Field(..., ge=0, le=1, description="Niveau de confiance de la prédiction")
    risk_level: str = Field(..., description="Niveau de risque associé")
    probabilities: dict = Field(..., description="Probabilités pour toutes les catégories")
    bmi: float = Field(..., description="Indice de masse corporelle calculé")
    recommendations: list = Field(..., description="Recommandations basées sur la prédiction")

class ModelStatusResponse(BaseModel):
    """Modèle pour le statut du modèle"""
    
    status: str = Field(..., description="Statut du modèle")
    accuracy: float = Field(..., description="Précision du modèle")
    model_type: str = Field(..., description="Type de modèle utilisé")
    features_count: int = Field(..., description="Nombre de features")
    categories: list = Field(..., description="Catégories d'obésité")

# ==================== CLASSE PRÉDICTEUR ====================

class ObesityPredictor:
    """Classe pour prédire les catégories d'obésité en utilisant le modèle ML entraîné"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.target_encoder = None
        self.feature_columns = None
        self.model_info = {}
        self.load_models()
    
    def load_models(self):
        """Charge les modèles et préprocesseurs sauvegardés"""
        try:
            models_path = 'models'
            
            if not os.path.exists(models_path):
                print("⚠️ Dossier models non trouvé. Entraînement du modèle...")
                self.train_and_save_model()
                return
            
            self.model = joblib.load(os.path.join(models_path, 'best_obesity_model.pkl'))
            self.scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))
            self.label_encoders = joblib.load(os.path.join(models_path, 'label_encoders.pkl'))
            self.target_encoder = joblib.load(os.path.join(models_path, 'target_encoder.pkl'))
            self.feature_columns = joblib.load(os.path.join(models_path, 'feature_columns.pkl'))
            self.model_info = joblib.load(os.path.join(models_path, 'model_info.pkl'))
            
            print("✅ Modèles chargés avec succès")
            
        except FileNotFoundError as e:
            print(f"⚠️ Modèles non trouvés: {e}. Entraînement du modèle...")
            self.train_and_save_model()
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}. Entraînement du modèle...")
            self.train_and_save_model()
    
    def train_and_save_model(self):
        """Entraîne et sauvegarde le modèle"""
        print("=== ENTRAÎNEMENT DU MODÈLE ===")
        
        # Chargement des données
        if not os.path.exists('Data.csv'):
            raise HTTPException(
                status_code=500,
                detail="Fichier Data.csv non trouvé. Veuillez placer le fichier de données dans le même dossier."
            )
        
        df = pd.read_csv('Data.csv')
        print(f"Dataset chargé: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Préprocessing
        df_processed = df.copy()
        
        # Encodage des variables catégorielles
        self.label_encoders = {}
        categorical_features = ['Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 'SMOKE', 'SCC', 'CALC', 'MTRANS']
        
        for feature in categorical_features:
            le = LabelEncoder()
            df_processed[feature] = le.fit_transform(df_processed[feature])
            self.label_encoders[feature] = le
        
        # Encodage de la variable cible
        self.target_encoder = LabelEncoder()
        df_processed['NObeyesdad_encoded'] = self.target_encoder.fit_transform(df_processed['NObeyesdad'])
        
        # Préparation des features
        self.feature_columns = [col for col in df_processed.columns if col not in ['NObeyesdad', 'NObeyesdad_encoded']]
        X = df_processed[self.feature_columns]
        y = df_processed['NObeyesdad_encoded']
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Normalisation
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entraînement des modèles
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'SVM': SVC(random_state=42, probability=True)
        }
        
        best_model = None
        best_score = 0
        best_name = ""
        
        for name, model in models.items():
            if name in ['Logistic Regression', 'SVM']:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            if accuracy > best_score:
                best_score = accuracy
                best_model = model
                best_name = name
        
        self.model = best_model
        self.model_info = {
            'model_type': best_name,
            'accuracy': best_score,
            'features_count': len(self.feature_columns),
            'categories': list(self.target_encoder.classes_)
        }
        
        print(f"✅ Meilleur modèle: {best_name} (Accuracy: {best_score:.4f})")
        
        # Sauvegarde
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/best_obesity_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        joblib.dump(self.label_encoders, 'models/label_encoders.pkl')
        joblib.dump(self.target_encoder, 'models/target_encoder.pkl')
        joblib.dump(self.feature_columns, 'models/feature_columns.pkl')
        joblib.dump(self.model_info, 'models/model_info.pkl')
        
        print("✅ Modèles sauvegardés")
    
    def predict(self, features_dict):
        """Prédit la catégorie d'obésité"""
        try:
            # Validation des features requises
            required_features = set(self.feature_columns)
            provided_features = set(features_dict.keys())
            
            if not required_features.issubset(provided_features):
                missing_features = required_features - provided_features
                raise HTTPException(
                    status_code=400,
                    detail=f"Features manquantes: {list(missing_features)}"
                )
            
            # Création d'un DataFrame avec les features
            df_input = pd.DataFrame([features_dict])
            
            # Encodage des variables catégorielles
            for feature, encoder in self.label_encoders.items():
                if feature in df_input.columns:
                    # Récupération de la valeur brute (pas l'enum)
                    feature_value = features_dict[feature]
                    if feature_value not in encoder.classes_:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Valeur invalide pour {feature}: {feature_value}. Valeurs acceptées: {list(encoder.classes_)}"
                        )
                    df_input[feature] = encoder.transform([feature_value])[0]
            
            # Réorganisation des colonnes
            df_input = df_input[self.feature_columns]
            
            # Normalisation
            df_input_scaled = self.scaler.transform(df_input)
            
            # Prédiction
            prediction_encoded = self.model.predict(df_input_scaled)[0]
            probabilities = self.model.predict_proba(df_input_scaled)[0]
            
            # Décodage de la prédiction
            prediction = self.target_encoder.inverse_transform([prediction_encoded])[0]
            
            # Création du résultat
            result = {
                'prediction': prediction,
                'confidence': float(max(probabilities)),
                'probabilities': {
                    self.target_encoder.inverse_transform([i])[0]: float(prob) 
                    for i, prob in enumerate(probabilities)
                },
                'risk_level': self._get_risk_level(prediction)
            }
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la prédiction: {str(e)}"
            )
    
    def _get_risk_level(self, prediction):
        """Détermine le niveau de risque basé sur la prédiction"""
        risk_mapping = {
            'Insufficient_Weight': 'Faible',
            'Normal_Weight': 'Très faible',
            'Overweight_Level_I': 'Modéré',
            'Overweight_Level_II': 'Élevé',
            'Obesity_Type_I': 'Très élevé',
            'Obesity_Type_II': 'Critique',
            'Obesity_Type_III': 'Critique'
        }
        return risk_mapping.get(prediction, 'Inconnu')
    
    def get_model_status(self):
        """Retourne le statut du modèle"""
        return self.model_info

# ==================== FONCTIONS UTILITAIRES ====================

def calculate_bmi(weight: float, height: float) -> float:
    """Calcule l'IMC (Indice de Masse Corporelle)"""
    return round(weight / (height ** 2), 2)

def get_health_recommendations(prediction: str, bmi: float) -> list:
    """Génère des recommandations de santé basées sur la prédiction"""
    recommendations = []
    
    if prediction in ["Insufficient_Weight"]:
        recommendations = [
            HealthRecommendation(
                category="Nutrition",
                recommendation="Consultez un nutritionniste pour un plan alimentaire équilibré et riche en calories",
                priority="High"
            ),
            HealthRecommendation(
                category="Exercice",
                recommendation="Pratiquez des exercices de musculation pour développer la masse musculaire",
                priority="Medium"
            )
        ]
    elif prediction == "Normal_Weight":
        recommendations = [
            HealthRecommendation(
                category="Maintien",
                recommendation="Continuez à maintenir un mode de vie sain avec une alimentation équilibrée",
                priority="Low"
            ),
            HealthRecommendation(
                category="Exercice",
                recommendation="Maintenez une activité physique régulière (150 min/semaine)",
                priority="Low"
            )
        ]
    elif prediction in ["Overweight_Level_I", "Overweight_Level_II"]:
        recommendations = [
            HealthRecommendation(
                category="Nutrition",
                recommendation="Réduisez l'apport calorique et augmentez la consommation de fruits et légumes",
                priority="High"
            ),
            HealthRecommendation(
                category="Exercice",
                recommendation="Augmentez l'activité physique à au moins 30 minutes par jour",
                priority="High"
            ),
            HealthRecommendation(
                category="Suivi",
                recommendation="Consultez un professionnel de santé pour un suivi personnalisé",
                priority="Medium"
            )
        ]
    else:  # Obesity_Type_I, II, III
        recommendations = [
            HealthRecommendation(
                category="Urgent",
                recommendation="Consultez immédiatement un médecin ou un spécialiste de l'obésité",
                priority="High"
            ),
            HealthRecommendation(
                category="Nutrition",
                recommendation="Suivez un programme nutritionnel supervisé par un professionnel",
                priority="High"
            ),
            HealthRecommendation(
                category="Exercice",
                recommendation="Commencez par des exercices doux et progressifs sous supervision médicale",
                priority="High"
            ),
            HealthRecommendation(
                category="Suivi",
                recommendation="Surveillance médicale régulière et tests de santé complets",
                priority="High"
            )
        ]
    
    return [rec.dict() for rec in recommendations]

# ==================== APPLICATION FASTAPI ====================

# Initialisation de l'application FastAPI
app = FastAPI(
    title="ObesiTrack API - Prédiction d'Obésité",
    description="API complète pour la prédiction des catégories d'obésité basée sur des modèles de Machine Learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale du prédicteur
predictor = None

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    global predictor
    try:
        predictor = ObesityPredictor()
        print("✅ API ObesiTrack initialisée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {str(e)}")

@app.get("/", tags=["Health"])
async def root():
    """Endpoint de base pour vérifier que l'API fonctionne"""
    return {
        "message": "Bienvenue sur l'API ObesiTrack - Prédiction d'Obésité",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "prediction": "/predict (🔒 JWT Required)",
            "model_status": "/model/status (🔒 JWT Required)",
            "sample_prediction": "/predict/sample (🔒 JWT Required)",
            "user_info": "/user/info (🔒 JWT Required)",
            "health_check": "/health (Public)",
            "documentation": "/docs (Public)"
        },
        "authentication": {
            "type": "JWT Bearer Token",
            "header": "Authorization: Bearer <token>",
            "login_endpoint": "http://localhost:7777/login"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        global predictor
        if predictor is None:
            return {
                "status": "unhealthy",
                "message": "Prédicteur non initialisé",
                "predictor_loaded": False
            }
        
        return {
            "status": "healthy",
            "message": "API fonctionnelle",
            "predictor_loaded": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Erreur: {str(e)}",
            "predictor_loaded": False
        }

@app.get("/user/info", tags=["User"])
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Obtenir les informations de l'utilisateur connecté (Protégé par JWT)"""
    return {
        "message": "Utilisateur authentifié",
        "user": current_user,
        "authenticated": True
    }

@app.get("/model/status", response_model=ModelStatusResponse, tags=["Model"])
async def get_model_status(current_user: dict = Depends(get_current_user)):
    """Obtenir le statut et les informations du modèle ML (Protégé par JWT)"""
    try:
        global predictor
        if predictor is None:
            raise HTTPException(
                status_code=500,
                detail="Prédicteur non initialisé"
            )
        
        model_info = predictor.get_model_status()
        
        return ModelStatusResponse(
            status="trained",
            accuracy=model_info['accuracy'],
            model_type=model_info['model_type'],
            features_count=model_info['features_count'],
            categories=model_info['categories']
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )

@app.post("/predict", response_model=ObesityPredictionResponse, tags=["Prediction"])
async def predict_obesity(request: ObesityPredictionRequest, current_user: dict = Depends(get_current_user)):
    """
    Prédit la catégorie d'obésité basée sur les caractéristiques fournies (Protégé par JWT)
    
    Cette endpoint utilise un modèle de machine learning entraîné pour prédire
    la catégorie d'obésité d'une personne basée sur ses caractéristiques
    physiques, habitudes alimentaires et mode de vie.
    """
    try:
        global predictor
        if predictor is None:
            raise HTTPException(
                status_code=500,
                detail="Prédicteur non initialisé"
            )
        
        # Conversion de la requête en dictionnaire avec les valeurs brutes
        features_dict = request.dict()
        
        # Conversion des enums en valeurs string pour l'encodage
        for key, value in features_dict.items():
            if hasattr(value, 'value'):  # Si c'est un enum
                features_dict[key] = value.value
        
        # Prédiction
        prediction_result = predictor.predict(features_dict)
        
        # Calcul de l'IMC
        bmi = calculate_bmi(request.Weight, request.Height)
        
        # Génération des recommandations
        recommendations = get_health_recommendations(
            prediction_result['prediction'], 
            bmi
        )
        
        # Construction de la réponse
        response = ObesityPredictionResponse(
            prediction=prediction_result['prediction'],
            confidence=prediction_result['confidence'],
            risk_level=prediction_result['risk_level'],
            probabilities=prediction_result['probabilities'],
            bmi=bmi,
            recommendations=recommendations
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )

@app.get("/predict/sample", response_model=ObesityPredictionResponse, tags=["Prediction"])
async def predict_sample(current_user: dict = Depends(get_current_user)):
    """
    Exemple de prédiction avec des données d'exemple (Protégé par JWT)
    """
    sample_data = ObesityPredictionRequest(
        Gender="Male",
        Age=25,
        Height=1.75,
        Weight=80.0,
        family_history_with_overweight="yes",
        FAVC="no",
        FCVC=2.0,
        NCP=3.0,
        CAEC="Sometimes",
        SMOKE="no",
        CH2O=2.0,
        SCC="no",
        FAF=1.0,
        TUE=0.0,
        CALC="Sometimes",
        MTRANS="Public_Transportation"
    )
    
    return await predict_obesity(sample_data)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API ObesiTrack - Prédiction d'Obésité")
    print("📊 Port: 8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("=" * 50)

    # Configuration sécurisée pour Docker
    host = os.getenv("HOST", "127.0.0.1")  # Par défaut localhost, 0.0.0.0 pour Docker
    if os.getenv("DOCKER_ENV") == "true":
        host = "0.0.0.0"  # Nécessaire pour Docker
    
    uvicorn.run("obesity_api:app", host=host, port=8000, reload=True)  # nosec B104