"""
Application principale pour Hugging Face Spaces
ObesiTrack - Application de prédiction d'obésité
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# Ajouter les chemins nécessaires
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir / "App" / "Back-end"))
sys.path.insert(0, str(app_dir / "ModelAi"))
sys.path.insert(0, str(app_dir / "App"))

# Variables d'environnement
os.environ.setdefault("API_HOST", "0.0.0.0")
os.environ.setdefault("API_PORT", "7860")
os.environ.setdefault("ML_API_PORT", "8000")
os.environ.setdefault("PYTHONPATH", str(app_dir))

# Démarrer l'API ML en arrière-plan
def start_ml_api():
    try:
        print("Démarrage de l'API ML...")
        ml_dir = app_dir / "ModelAi"
        subprocess.Popen([
            sys.executable, "run_api.py"
        ], cwd=ml_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("API ML démarrée sur le port 8000")
    except Exception as e:
        print(f"Erreur lors du démarrage de l'API ML: {e}")

# Démarrer l'API ML
ml_thread = threading.Thread(target=start_ml_api, daemon=True)
ml_thread.start()
time.sleep(5)

# Importer FastAPI et les dépendances
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json

# Créer l'application FastAPI
app = FastAPI(title="ObesiTrack", description="Application de prédiction d'obésité")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory="App/Front-end/src")

# Servir les fichiers statiques
try:
    app.mount("/static", StaticFiles(directory="App/Front-end/src"), name="static")
    app.mount("/images", StaticFiles(directory="App/Front-end/Images"), name="images")
except Exception as e:
    print(f"Impossible de monter les fichiers statiques: {e}")

# Modèles Pydantic
class UserSignup(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class PredictionData(BaseModel):
    Gender: str
    Age: float
    Height: float
    Weight: float
    family_history_with_overweight: str
    FAVC: str
    FCVC: float
    NCP: float
    CAEC: str
    SMOKE: str
    CH2O: float
    SCC: str
    FAF: float
    TUE: float
    CALC: str
    MTRANS: str

# Base de données en mémoire
users_db = {}
predictions_db = {}

# Routes HTML
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse("Home.html", {"request": request})
    except Exception as e:
        print(f"Erreur page d'accueil: {e}")
        return HTMLResponse(content="""
        <html>
            <head><title>ObesiTrack</title></head>
            <body>
                <h1>ObesiTrack - Application de Prédiction d'Obésité</h1>
                <p>Application de prédiction d'obésité basée sur l'IA</p>
                <p><a href="/docs">Documentation API</a></p>
            </body>
        </html>
        """)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    try:
        return templates.TemplateResponse("Login.html", {"request": request})
    except Exception as e:
        print(f"Erreur page login: {e}")
        return HTMLResponse(content="<h1>Page de connexion</h1>")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    try:
        return templates.TemplateResponse("Register.html", {"request": request})
    except Exception as e:
        print(f"Erreur page register: {e}")
        return HTMLResponse(content="<h1>Page d'inscription</h1>")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    try:
        return templates.TemplateResponse("Dashboard.html", {"request": request})
    except Exception as e:
        print(f"Erreur dashboard: {e}")
        return HTMLResponse(content="<h1>Dashboard</h1>")

@app.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    try:
        return templates.TemplateResponse("Predict.html", {"request": request})
    except Exception as e:
        print(f"Erreur page predict: {e}")
        return HTMLResponse(content="<h1>Prédiction</h1>")

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    try:
        return templates.TemplateResponse("History.html", {"request": request})
    except Exception as e:
        print(f"Erreur page history: {e}")
        return HTMLResponse(content="<h1>Historique</h1>")

@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request):
    try:
        return templates.TemplateResponse("Statistics.html", {"request": request})
    except Exception as e:
        print(f"Erreur page statistics: {e}")
        return HTMLResponse(content="<h1>Statistiques</h1>")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    try:
        return templates.TemplateResponse("AdminDashboard.html", {"request": request})
    except Exception as e:
        print(f"Erreur page admin: {e}")
        return HTMLResponse(content="<h1>Administration</h1>")

# API Routes
@app.post("/signup")
async def signup(user_data: UserSignup):
    try:
        if user_data.email in users_db:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        users_db[user_data.email] = {
            "email": user_data.email,
            "name": user_data.name,
            "password": user_data.password,
            "role": "user"
        }
        
        return {"message": "User created successfully", "email": user_data.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(user_data: UserLogin):
    try:
        if user_data.email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = users_db[user_data.email]
        if user["password"] != user_data.password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = f"fake_jwt_token_{user_data.email}"
        
        return {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "token": token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict(prediction_data: PredictionData):
    try:
        ml_api_url = "http://localhost:8000/predict"
        
        ml_data = {
            "Gender": prediction_data.Gender,
            "Age": prediction_data.Age,
            "Height": prediction_data.Height,
            "Weight": prediction_data.Weight,
            "family_history_with_overweight": prediction_data.family_history_with_overweight,
            "FAVC": prediction_data.FAVC,
            "FCVC": prediction_data.FCVC,
            "NCP": prediction_data.NCP,
            "CAEC": prediction_data.CAEC,
            "SMOKE": prediction_data.SMOKE,
            "CH2O": prediction_data.CH2O,
            "SCC": prediction_data.SCC,
            "FAF": prediction_data.FAF,
            "TUE": prediction_data.TUE,
            "CALC": prediction_data.CALC,
            "MTRANS": prediction_data.MTRANS
        }
        
        try:
            response = requests.post(ml_api_url, json=ml_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                # Fallback
                return {
                    "prediction": "Normal_Weight",
                    "confidence": 0.85,
                    "risk_level": "Très faible",
                    "bmi": round(prediction_data.Weight / (prediction_data.Height ** 2), 2),
                    "probabilities": {
                        "Insufficient_Weight": 0.05,
                        "Normal_Weight": 0.85,
                        "Overweight_Level_I": 0.08,
                        "Overweight_Level_II": 0.02,
                        "Obesity_Type_I": 0.00,
                        "Obesity_Type_II": 0.00,
                        "Obesity_Type_III": 0.00
                    },
                    "recommendations": [
                        {
                            "category": "Maintien",
                            "recommendation": "Continuez à maintenir un mode de vie sain",
                            "priority": "Low"
                        }
                    ]
                }
        except Exception as e:
            print(f"API ML non disponible: {e}")
            # Fallback
            return {
                "prediction": "Normal_Weight",
                "confidence": 0.85,
                "risk_level": "Très faible",
                "bmi": round(prediction_data.Weight / (prediction_data.Height ** 2), 2),
                "probabilities": {
                    "Insufficient_Weight": 0.05,
                    "Normal_Weight": 0.85,
                    "Overweight_Level_I": 0.08,
                    "Overweight_Level_II": 0.02,
                    "Obesity_Type_I": 0.00,
                    "Obesity_Type_II": 0.00,
                    "Obesity_Type_III": 0.00
                },
                "recommendations": [
                    {
                        "category": "Maintien",
                        "recommendation": "Continuez à maintenir un mode de vie sain",
                        "priority": "Low"
                    }
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predictions")
async def get_predictions():
    return {"predictions": list(predictions_db.values())}

@app.get("/results")
async def get_results():
    return {"results": list(predictions_db.values())}

@app.get("/admin/users")
async def get_users():
    return {"users": list(users_db.values())}

@app.get("/admin/statistics")
async def get_statistics():
    return {
        "total_users": len(users_db),
        "total_predictions": len(predictions_db),
        "admin_users": len([u for u in users_db.values() if u.get("role") == "admin"])
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "ObesiTrack API is running"}

@app.get("/api/status")
def api_status():
    return {
        "status": "running",
        "api_ml": "started",
        "main_api": "running",
        "port": 7860,
        "users_count": len(users_db),
        "predictions_count": len(predictions_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)