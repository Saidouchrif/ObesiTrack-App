from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from enum import Enum

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

class ObesityPredictionResponse(BaseModel):
    """Modèle pour la réponse de prédiction d'obésité"""
    
    prediction: str = Field(..., description="Catégorie d'obésité prédite")
    confidence: float = Field(..., ge=0, le=1, description="Niveau de confiance de la prédiction")
    risk_level: str = Field(..., description="Niveau de risque associé")
    probabilities: dict = Field(..., description="Probabilités pour toutes les catégories")
    bmi: float = Field(..., description="Indice de masse corporelle calculé")
    recommendations: list = Field(..., description="Recommandations basées sur la prédiction")

class FeatureInfoResponse(BaseModel):
    """Modèle pour les informations sur les features"""
    
    features: dict = Field(..., description="Informations sur toutes les features")
    categories: list = Field(..., description="Liste des catégories d'obésité possibles")
    risk_levels: dict = Field(..., description="Mapping des catégories vers les niveaux de risque")

class HealthRecommendation(BaseModel):
    """Modèle pour une recommandation de santé"""
    
    category: str = Field(..., description="Catégorie de la recommandation")
    recommendation: str = Field(..., description="Texte de la recommandation")
    priority: str = Field(..., description="Priorité (High, Medium, Low)")
