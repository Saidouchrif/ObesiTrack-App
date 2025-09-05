#!/usr/bin/env python3
"""
Script de démarrage pour l'API de prédiction d'obésité
"""

import uvicorn
import sys
import os

# Ajout du chemin pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Démarrage de l'API ObesiTrack - Prédiction d'Obésité")
    print("📊 Port: 8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔍 Redoc: http://localhost:8000/redoc")
    print("=" * 50)
    
    uvicorn.run(
        "obesity_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
