"""
Tests pour l'API ML de prédiction d'obésité
"""
import pytest
import os
import sys
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ajouter le chemin du module principal
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from obesity_api import app

client = TestClient(app)

class TestMLAPI:
    """Tests pour l'API ML"""
    
    def test_read_root(self):
        """Test de la page d'accueil de l'API ML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "ObesiTrack ML API" in response.json()["message"]
    
    def test_health_check(self):
        """Test du health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_model_info(self):
        """Test des informations du modèle"""
        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "model_name" in data
        assert "version" in data
        assert "accuracy" in data

class TestPredictionAPI:
    """Tests pour l'API de prédiction ML"""
    
    def test_predict_without_auth(self):
        """Test de prédiction sans authentification"""
        prediction_data = {
            "Gender": "Male",
            "Age": 25.0,
            "Height": 175.0,
            "Weight": 70.0,
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
        
        response = client.post("/predict", json=prediction_data)
        assert response.status_code == 401  # Non autorisé
    
    @patch('obesity_api.get_current_user')
    @patch('obesity_api.predict_obesity')
    def test_predict_with_auth_success(self, mock_predict, mock_get_user):
        """Test de prédiction avec authentification réussie"""
        # Mock de l'utilisateur authentifié
        mock_get_user.return_value = {"email": "test@example.com", "name": "Test User"}
        
        # Mock de la prédiction
        mock_predict.return_value = {
            "prediction": "Normal_Weight",
            "probabilities": {
                "Insufficient_Weight": 0.05,
                "Normal_Weight": 0.75,
                "Overweight_Level_I": 0.15,
                "Overweight_Level_II": 0.03,
                "Obesity_Type_I": 0.02,
                "Obesity_Type_II": 0.0,
                "Obesity_Type_III": 0.0
            },
            "confidence": 0.75
        }
        
        prediction_data = {
            "Gender": "Male",
            "Age": 25.0,
            "Height": 175.0,
            "Weight": 70.0,
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
        
        response = client.post("/predict", json=prediction_data)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probabilities" in data
        assert "confidence" in data
        assert data["prediction"] == "Normal_Weight"
    
    @patch('obesity_api.get_current_user')
    def test_predict_invalid_data(self, mock_get_user):
        """Test de prédiction avec des données invalides"""
        mock_get_user.return_value = {"email": "test@example.com", "name": "Test User"}
        
        invalid_data = {
            "Gender": "Invalid",  # Valeur invalide
            "Age": -5,  # Âge négatif
            "Height": 0,  # Taille nulle
            "Weight": -10  # Poids négatif
        }
        
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422  # Erreur de validation
    
    @patch('obesity_api.get_current_user')
    def test_predict_missing_fields(self, mock_get_user):
        """Test de prédiction avec des champs manquants"""
        mock_get_user.return_value = {"email": "test@example.com", "name": "Test User"}
        
        incomplete_data = {
            "Gender": "Male",
            "Age": 25.0
            # Champs manquants
        }
        
        response = client.post("/predict", json=incomplete_data)
        assert response.status_code == 422  # Erreur de validation

class TestModelLoading:
    """Tests pour le chargement du modèle"""
    
    @patch('obesity_api.load_model')
    def test_model_loading_success(self, mock_load_model):
        """Test de chargement réussi du modèle"""
        mock_load_model.return_value = {
            "model": MagicMock(),
            "scaler": MagicMock(),
            "feature_columns": ["feature1", "feature2"],
            "label_encoders": {"feature1": MagicMock()},
            "target_encoder": MagicMock(),
            "model_info": {"accuracy": 0.85, "version": "1.0"}
        }
        
        response = client.get("/model/info")
        assert response.status_code == 200
    
    @patch('obesity_api.load_model')
    def test_model_loading_failure(self, mock_load_model):
        """Test d'échec de chargement du modèle"""
        mock_load_model.side_effect = Exception("Modèle non trouvé")
        
        response = client.get("/model/info")
        assert response.status_code == 500

class TestDataPreprocessing:
    """Tests pour le prétraitement des données"""
    
    def test_data_validation(self):
        """Test de validation des données"""
        valid_data = {
            "Gender": "Male",
            "Age": 25.0,
            "Height": 175.0,
            "Weight": 70.0,
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
        
        # Test avec des données valides
        response = client.post("/predict", json=valid_data)
        # Le test peut échouer à cause de l'authentification, mais pas à cause de la validation
        assert response.status_code in [200, 401]
    
    def test_data_types_validation(self):
        """Test de validation des types de données"""
        invalid_types_data = {
            "Gender": 123,  # Devrait être une chaîne
            "Age": "twenty-five",  # Devrait être un nombre
            "Height": "tall",  # Devrait être un nombre
            "Weight": [70]  # Devrait être un nombre
        }
        
        response = client.post("/predict", json=invalid_types_data)
        assert response.status_code == 422  # Erreur de validation

class TestPerformance:
    """Tests de performance"""
    
    @patch('obesity_api.get_current_user')
    @patch('obesity_api.predict_obesity')
    def test_prediction_speed(self, mock_predict, mock_get_user):
        """Test de vitesse de prédiction"""
        import time
        
        mock_get_user.return_value = {"email": "test@example.com", "name": "Test User"}
        mock_predict.return_value = {
            "prediction": "Normal_Weight",
            "probabilities": {"Normal_Weight": 0.8},
            "confidence": 0.8
        }
        
        prediction_data = {
            "Gender": "Male",
            "Age": 25.0,
            "Height": 175.0,
            "Weight": 70.0,
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
        
        start_time = time.time()
        response = client.post("/predict", json=prediction_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Prédiction en moins de 5 secondes
