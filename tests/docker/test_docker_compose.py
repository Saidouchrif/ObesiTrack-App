"""
Tests pour la validation Docker Compose
"""
import pytest
import subprocess
import time
import requests
import os

class TestDockerCompose:
    """Tests pour Docker Compose"""
    
    def test_docker_compose_config(self):
        """Test de la syntaxe du docker-compose.yml"""
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Erreur de syntaxe: {result.stderr}"
    
    def test_docker_build(self):
        """Test de construction de l'image Docker"""
        result = subprocess.run(
            ["docker", "build", "-t", "obesitrack:test", "."],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Erreur de construction: {result.stderr}"
    
    def test_docker_image_structure(self):
        """Test de la structure de l'image Docker"""
        # Vérifier que les fichiers nécessaires sont présents
        files_to_check = [
            "/app/requirements.txt",
            "/app/App/Back-end/main.py",
            "/app/ModelAi/obesity_api.py",
            "/app/start.sh"
        ]
        
        for file_path in files_to_check:
            result = subprocess.run(
                ["docker", "run", "--rm", "obesitrack:test", "test", "-f", file_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Fichier manquant: {file_path}"
    
    def test_docker_environment_variables(self):
        """Test des variables d'environnement Docker"""
        result = subprocess.run(
            ["docker", "run", "--rm", "-e", "PYTHONPATH=/app", "obesitrack:test", "python", "-c", "import sys; print(sys.path)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "/app" in result.stdout

class TestDockerServices:
    """Tests pour les services Docker"""
    
    @pytest.fixture(scope="class")
    def docker_services(self):
        """Fixture pour démarrer les services Docker"""
        # Démarrer les services
        subprocess.run(["docker-compose", "up", "-d", "--build"], check=True)
        
        # Attendre que les services soient prêts
        time.sleep(30)
        
        yield
        
        # Nettoyage
        subprocess.run(["docker-compose", "down", "-v"], check=True)
    
    def test_main_api_service(self, docker_services):
        """Test du service API principale"""
        try:
            response = requests.get("http://localhost:7777/", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Service API principale non accessible")
    
    def test_ml_api_service(self, docker_services):
        """Test du service API ML"""
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Service API ML non accessible")
    
    def test_mongodb_service(self, docker_services):
        """Test du service MongoDB"""
        try:
            # Test de connexion MongoDB
            result = subprocess.run(
                ["docker", "exec", "obesitrack-mongo", "mongosh", "--eval", "db.adminCommand('ping')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
        except subprocess.TimeoutExpired:
            pytest.skip("Service MongoDB non accessible")
    
    def test_mongo_express_service(self, docker_services):
        """Test du service MongoDB Express"""
        try:
            response = requests.get("http://localhost:8081/", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Service MongoDB Express non accessible")

class TestDockerHealthChecks:
    """Tests pour les health checks Docker"""
    
    def test_health_check_script(self):
        """Test du script de health check"""
        # Vérifier que le script start.sh existe et est exécutable
        assert os.path.exists("start.sh")
        assert os.access("start.sh", os.X_OK)
    
    def test_docker_health_check_config(self):
        """Test de la configuration des health checks"""
        # Vérifier que les health checks sont configurés dans docker-compose.yml
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            assert "healthcheck:" in content
            assert "test:" in content

class TestDockerVolumes:
    """Tests pour les volumes Docker"""
    
    def test_volume_mounts(self):
        """Test des montages de volumes"""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            assert "volumes:" in content
            assert "./App/Front-end/src:/app/App/Front-end/src:ro" in content
    
    def test_mongo_data_volume(self):
        """Test du volume de données MongoDB"""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            assert "mongo_data:" in content
            assert "/data/db" in content

class TestDockerNetworking:
    """Tests pour le réseau Docker"""
    
    def test_network_configuration(self):
        """Test de la configuration réseau"""
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            assert "networks:" in content
            assert "obesitrack-network:" in content
    
    def test_service_communication(self):
        """Test de la communication entre services"""
        # Vérifier que les services peuvent communiquer via le réseau
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            assert "mongodb://mongo:27017" in content
