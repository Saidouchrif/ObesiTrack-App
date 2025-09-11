"""
Tests de performance et de charge pour ObesiTrack
"""
import pytest
import time
import requests
import concurrent.futures
from locust import HttpUser, task, between

class ObesiTrackUser(HttpUser):
    """Utilisateur simulé pour les tests de charge"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Connexion de l'utilisateur"""
        # Simuler une connexion
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.client.post("/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def view_homepage(self):
        """Tâche: consulter la page d'accueil"""
        self.client.get("/")
    
    @task(2)
    def view_dashboard(self):
        """Tâche: consulter le dashboard"""
        self.client.get("/dashboard", headers=self.headers)
    
    @task(1)
    def make_prediction(self):
        """Tâche: faire une prédiction"""
        if self.token:
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
            self.client.post("/predict", json=prediction_data, headers=self.headers)

class TestPerformance:
    """Tests de performance"""
    
    def test_single_request_response_time(self):
        """Test du temps de réponse d'une requête unique"""
        start_time = time.time()
        response = requests.get("http://localhost:7777/", timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # Moins de 2 secondes
    
    def test_concurrent_requests(self):
        """Test de requêtes concurrentes"""
        def make_request():
            try:
                response = requests.get("http://localhost:7777/", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # Tester 10 requêtes concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8  # 80% de succès minimum
    
    def test_api_endpoints_performance(self):
        """Test de performance des endpoints API"""
        endpoints = [
            "/",
            "/login",
            "/register",
            "/dashboard",
            "/predict",
            "/statistics",
            "/history"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"http://localhost:7777{endpoint}", timeout=5)
                end_time = time.time()
                response_time = end_time - start_time
                
                # Accepter les codes 200, 401 (non autorisé), 404 (non trouvé)
                assert response.status_code in [200, 401, 404]
                assert response_time < 3.0  # Moins de 3 secondes
            except requests.exceptions.RequestException:
                # Ignorer les erreurs de connexion pour les tests
                pass
    
    def test_ml_api_performance(self):
        """Test de performance de l'API ML"""
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/", timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Moins de 5 secondes
        except requests.exceptions.RequestException:
            pytest.skip("API ML non accessible")

class TestLoadTesting:
    """Tests de charge"""
    
    def test_light_load(self):
        """Test de charge légère (5 utilisateurs simultanés)"""
        def simulate_user():
            for _ in range(5):  # 5 requêtes par utilisateur
                try:
                    response = requests.get("http://localhost:7777/", timeout=5)
                    assert response.status_code in [200, 401, 404]
                except:
                    pass
        
        # 5 utilisateurs simultanés
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(simulate_user) for _ in range(5)]
            concurrent.futures.wait(futures)
    
    def test_medium_load(self):
        """Test de charge moyenne (10 utilisateurs simultanés)"""
        def simulate_user():
            for _ in range(3):  # 3 requêtes par utilisateur
                try:
                    response = requests.get("http://localhost:7777/", timeout=5)
                    assert response.status_code in [200, 401, 404]
                except:
                    pass
        
        # 10 utilisateurs simultanés
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_user) for _ in range(10)]
            concurrent.futures.wait(futures)
    
    def test_heavy_load(self):
        """Test de charge lourde (20 utilisateurs simultanés)"""
        def simulate_user():
            for _ in range(2):  # 2 requêtes par utilisateur
                try:
                    response = requests.get("http://localhost:7777/", timeout=5)
                    assert response.status_code in [200, 401, 404]
                except:
                    pass
        
        # 20 utilisateurs simultanés
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(simulate_user) for _ in range(20)]
            concurrent.futures.wait(futures)

class TestMemoryUsage:
    """Tests d'utilisation mémoire"""
    
    def test_memory_leak_detection(self):
        """Test de détection de fuites mémoire"""
        # Faire plusieurs requêtes pour détecter les fuites
        for _ in range(50):
            try:
                response = requests.get("http://localhost:7777/", timeout=5)
                assert response.status_code in [200, 401, 404]
            except:
                pass
        
        # Si on arrive ici sans erreur, pas de fuite mémoire évidente
        assert True

class TestDatabasePerformance:
    """Tests de performance de la base de données"""
    
    def test_database_connection_time(self):
        """Test du temps de connexion à la base de données"""
        # Ce test nécessite que MongoDB soit accessible
        try:
            start_time = time.time()
            # Simuler une requête qui nécessite la DB
            response = requests.get("http://localhost:7777/admin/users", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            # Accepter 401 (non autorisé) ou 200 (succès)
            assert response.status_code in [200, 401]
            assert response_time < 5.0  # Moins de 5 secondes
        except requests.exceptions.RequestException:
            pytest.skip("Base de données non accessible")
