#!/bin/bash

# Script de démarrage pour ObesiTrack
echo "🚀 Démarrage de ObesiTrack Application"
echo "======================================"

# Fonction pour gérer l'arrêt propre
cleanup() {
    echo "🛑 Arrêt des services..."
    kill $BACKEND_PID $ML_PID 2>/dev/null
    exit 0
}

# Capturer les signaux d'arrêt
trap cleanup SIGTERM SIGINT

# Démarrer l'API ML en arrière-plan
echo "📊 Démarrage de l'API ML (port 8000)..."
cd /app/ModelAi
python run_api.py &
ML_PID=$!

# Attendre que l'API ML soit prête
echo "⏳ Attente du démarrage de l'API ML..."
sleep 10

# Démarrer l'API principale en arrière-plan
echo "🏥 Démarrage de l'API principale (port 7777)..."
cd /app/App/Back-end
uvicorn main:app --host 0.0.0.0 --port 7777 --reload &
BACKEND_PID=$!

# Attendre que les deux services soient prêts
echo "✅ Services démarrés:"
echo "   - API Principale: http://localhost:7777"
echo "   - API ML: http://localhost:8000"
echo "   - Documentation: http://localhost:7777/docs"
echo "   - MongoDB Express: http://localhost:8081"
echo "======================================"

# Attendre que les processus se terminent
wait $BACKEND_PID $ML_PID
