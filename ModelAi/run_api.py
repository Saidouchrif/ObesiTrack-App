#!/usr/bin/env python3
"""
Script simple pour démarrer l'API ObesiTrack
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Démarrage de l'API ObesiTrack - Prédiction d'Obésité")
    print("📊 Port: 8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔍 Redoc: http://localhost:8000/redoc")
    print("=" * 60)
    print("ℹ️  Le modèle sera entraîné automatiquement au premier démarrage")
    print("=" * 60)
    
    try:
        # Configuration sécurisée pour Docker
        host = os.getenv("HOST", "127.0.0.1")  # Par défaut localhost, 0.0.0.0 pour Docker
        if os.getenv("DOCKER_ENV") == "true":
            host = "0.0.0.0"  # Nécessaire pour Docker
        
        uvicorn.run(
            "obesity_api:app",
            host=host,  # nosec B104
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'API")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Assurez-vous que le fichier Data.csv est présent dans ce dossier")
