"""
Tests pour l'API principale ObesiTrack
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ajouter le chemin du module principal
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)

class TestMainAPI:
    """Tests pour les endpoints principaux"""
    
    def test_read_root(self):
        """Test de la page d'accueil"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Home.html" in response.text
    
    def test_login_page(self):
        """Test de la page de connexion"""
        response = client.get("/login")
        assert response.status_code == 200
        assert "Login.html" in response.text
    
    def test_register_page(self):
        """Test de la page d'inscription"""
        response = client.get("/register")
        assert response.status_code == 200
        assert "Register.html" in response.text
    
    def test_predict_page(self):
        """Test de la page de prédiction"""
        response = client.get("/predict")
        assert response.status_code == 200
        assert "Predict.html" in response.text
    
    def test_dashboard_page(self):
        """Test de la page dashboard"""
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "Dashboard.html" in response.text
    
    def test_statistics_page(self):
        """Test de la page statistiques"""
        response = client.get("/statistics")
        assert response.status_code == 200
        assert "Statistics.html" in response.text
    
    def test_history_page(self):
        """Test de la page historique"""
        response = client.get("/history")
        assert response.status_code == 200
        assert "History.html" in response.text
    
    def test_admin_page(self):
        """Test de la page admin"""
        response = client.get("/admin")
        assert response.status_code == 200
        assert "AdminDashboard.html" in response.text

class TestUserAuthentication:
    """Tests pour l'authentification utilisateur"""
    
    @patch('models.User.create_user')
    def test_signup_success(self, mock_create_user):
        """Test d'inscription réussie"""
        mock_create_user.return_value = {
            "message": "Utilisateur créé avec succès",
            "user_id": "test@example.com"
        }
        
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123"
        }
        
        response = client.post("/signup", json=user_data)
        assert response.status_code == 200
        assert "Utilisateur créé avec succès" in response.json()["message"]
    
    @patch('models.User.authenticate_user')
    def test_login_success(self, mock_authenticate):
        """Test de connexion réussie"""
        mock_authenticate.return_value = {
            "access_token": "fake_token",
            "token_type": "bearer",
            "user": {"email": "test@example.com", "name": "Test User"}
        }
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self):
        """Test de connexion avec des identifiants invalides"""
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 401

class TestPredictionAPI:
    """Tests pour l'API de prédiction"""
    
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
    
    @patch('models.Auth.get_current_user')
    @patch('models.Predict.create_predict')
    @patch('requests.post')
    def test_predict_with_auth_success(self, mock_requests, mock_create_predict, mock_get_user):
        """Test de prédiction avec authentification réussie"""
        # Mock de l'utilisateur authentifié
        mock_get_user.return_value = {"email": "test@example.com", "name": "Test User"}
        
        # Mock de la création de prédiction
        mock_create_predict.return_value = {"predict_id": "test_predict_id"}
        
        # Mock de l'API ML
        mock_ml_response = MagicMock()
        mock_ml_response.status_code = 200
        mock_ml_response.json.return_value = {
            "prediction": "Normal_Weight",
            "probabilities": {"Normal_Weight": 0.8, "Overweight_Level_I": 0.2}
        }
        mock_requests.return_value = mock_ml_response
        
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
        assert "prediction" in response.json()

class TestAdminAPI:
    """Tests pour l'API admin"""
    
    def test_admin_endpoints_without_auth(self):
        """Test des endpoints admin sans authentification"""
        response = client.get("/admin/users")
        assert response.status_code == 401
        
        response = client.get("/admin/results")
        assert response.status_code == 401
    
    @patch('models.Auth.get_current_user')
    def test_admin_endpoints_with_user_auth(self, mock_get_user):
        """Test des endpoints admin avec authentification utilisateur normal"""
        mock_get_user.return_value = {"email": "user@example.com", "name": "Normal User"}
        
        response = client.get("/admin/users")
        assert response.status_code == 403  # Accès refusé (pas admin)

class TestDataValidation:
    """Tests de validation des données"""
    
    def test_invalid_prediction_data(self):
        """Test avec des données de prédiction invalides"""
        invalid_data = {
            "Gender": "Invalid",  # Valeur invalide
            "Age": -5,  # Âge négatif
            "Height": 0,  # Taille nulle
            "Weight": -10  # Poids négatif
        }
        
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422  # Erreur de validation
    
    def test_missing_required_fields(self):
        """Test avec des champs requis manquants"""
        incomplete_data = {
            "Gender": "Male",
            "Age": 25.0
            # Champs manquants
        }
        
        response = client.post("/predict", json=incomplete_data)
        assert response.status_code == 422  # Erreur de validation
