import joblib
import pandas as pd
import numpy as np
from fastapi import HTTPException
import os

class ObesityPredictor:
    """
    Classe pour prédire les catégories d'obésité en utilisant le modèle ML entraîné
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.target_encoder = None
        self.feature_columns = None
        self.load_models()
    
    def load_models(self):
        """Charge les modèles et préprocesseurs sauvegardés"""
        try:
            # Chemin vers les modèles (relatif au dossier ModelAi)
            models_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ModelAi', 'models')
            
            self.model = joblib.load(os.path.join(models_path, 'best_obesity_model.pkl'))
            self.scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))
            self.label_encoders = joblib.load(os.path.join(models_path, 'label_encoders.pkl'))
            self.target_encoder = joblib.load(os.path.join(models_path, 'target_encoder.pkl'))
            self.feature_columns = joblib.load(os.path.join(models_path, 'feature_columns.pkl'))
            
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Modèles ML non trouvés. Veuillez d'abord entraîner le modèle. Erreur: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Erreur lors du chargement des modèles: {str(e)}"
            )
    
    def predict(self, features_dict):
        """
        Prédit la catégorie d'obésité basée sur les features fournies
        
        Args:
            features_dict (dict): Dictionnaire contenant les features
        
        Returns:
            dict: Prédiction et probabilités
        """
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
                    # Vérification que la valeur existe dans l'encodeur
                    if features_dict[feature] not in encoder.classes_:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Valeur invalide pour {feature}: {features_dict[feature]}. Valeurs acceptées: {list(encoder.classes_)}"
                        )
                    df_input[feature] = encoder.transform([features_dict[feature]])[0]
            
            # Réorganisation des colonnes selon l'ordre d'entraînement
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
    
    def get_feature_info(self):
        """Retourne les informations sur les features requises"""
        feature_info = {}
        
        for feature in self.feature_columns:
            if feature in self.label_encoders:
                feature_info[feature] = {
                    'type': 'categorical',
                    'values': list(self.label_encoders[feature].classes_)
                }
            else:
                feature_info[feature] = {
                    'type': 'numerical',
                    'description': self._get_feature_description(feature)
                }
        
        return feature_info
    
    def _get_feature_description(self, feature):
        """Retourne la description d'une feature"""
        descriptions = {
            'Age': 'Âge en années',
            'Height': 'Taille en mètres',
            'Weight': 'Poids en kilogrammes',
            'FCVC': 'Fréquence de consommation de légumes (1-3)',
            'NCP': 'Nombre de repas principaux par jour (1-4)',
            'CH2O': 'Consommation d\'eau par jour (1-3)',
            'FAF': 'Fréquence d\'activité physique (0-3)',
            'TUE': 'Temps d\'utilisation d\'appareils électroniques (0-2)'
        }
        return descriptions.get(feature, 'Feature numérique')
