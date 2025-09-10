#!/usr/bin/env python3
"""
Script de test pour vérifier l'endpoint /results
"""
import requests
import json

def test_results_endpoint():
    base_url = "http://localhost:7777"
    
    # Test de connexion
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Serveur accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Serveur non accessible: {e}")
        return
    
    # Test de l'endpoint /results sans authentification (devrait échouer)
    try:
        response = requests.get(f"{base_url}/results")
        print(f"📊 Endpoint /results sans auth: {response.status_code}")
        if response.status_code == 401:
            print("✅ Authentification requise (comportement attendu)")
        else:
            print(f"⚠️  Réponse inattendue: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors du test /results: {e}")

if __name__ == "__main__":
    test_results_endpoint()
