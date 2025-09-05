from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Ajout du chemin parent pour accéder aux modèles
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from models.ObesityPredictor import ObesityPredictor
from models.ObesityModels import (
    ObesityPredictionRequest, 
    ObesityPredictionResponse, 
    FeatureInfoResponse,
    HealthRecommendation
)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="ObesiTrack API - Prédiction d'Obésité",
    description="API pour la prédiction des catégories d'obésité basée sur des modèles de Machine Learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale du prédicteur
predictor = None

def get_predictor():
    """Dependency pour obtenir l'instance du prédicteur"""
    global predictor
    if predictor is None:
        try:
            predictor = ObesityPredictor()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'initialisation du prédicteur: {str(e)}"
            )
    return predictor

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    try:
        global predictor
        predictor = ObesityPredictor()
        print("✅ Prédicteur d'obésité initialisé avec succès")
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
            "prediction": "/predict",
            "feature_info": "/features",
            "health_check": "/health",
            "documentation": "/docs"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        predictor_instance = get_predictor()
        return {
            "status": "healthy",
            "message": "API fonctionnelle",
            "predictor_loaded": predictor_instance is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Erreur: {str(e)}",
            "predictor_loaded": False
        }

@app.get("/features", response_model=FeatureInfoResponse, tags=["Information"])
async def get_feature_info(predictor_instance: ObesityPredictor = Depends(get_predictor)):
    """Obtenir les informations sur les features requises pour la prédiction"""
    try:
        feature_info = predictor_instance.get_feature_info()
        
        # Catégories d'obésité possibles
        categories = [
            "Insufficient_Weight",
            "Normal_Weight", 
            "Overweight_Level_I",
            "Overweight_Level_II",
            "Obesity_Type_I",
            "Obesity_Type_II",
            "Obesity_Type_III"
        ]
        
        # Mapping des niveaux de risque
        risk_levels = {
            'Insufficient_Weight': 'Faible',
            'Normal_Weight': 'Très faible',
            'Overweight_Level_I': 'Modéré',
            'Overweight_Level_II': 'Élevé',
            'Obesity_Type_I': 'Très élevé',
            'Obesity_Type_II': 'Critique',
            'Obesity_Type_III': 'Critique'
        }
        
        return FeatureInfoResponse(
            features=feature_info,
            categories=categories,
            risk_levels=risk_levels
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des informations: {str(e)}"
        )

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

@app.post("/predict", response_model=ObesityPredictionResponse, tags=["Prediction"])
async def predict_obesity(
    request: ObesityPredictionRequest,
    predictor_instance: ObesityPredictor = Depends(get_predictor)
):
    """
    Prédit la catégorie d'obésité basée sur les caractéristiques fournies
    
    Cette endpoint utilise un modèle de machine learning entraîné pour prédire
    la catégorie d'obésité d'une personne basée sur ses caractéristiques
    physiques, habitudes alimentaires et mode de vie.
    """
    try:
        # Conversion de la requête en dictionnaire
        features_dict = request.dict()
        
        # Prédiction
        prediction_result = predictor_instance.predict(features_dict)
        
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
async def predict_sample(predictor_instance: ObesityPredictor = Depends(get_predictor)):
    """
    Exemple de prédiction avec des données d'exemple
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
    
    return await predict_obesity(sample_data, predictor_instance)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
