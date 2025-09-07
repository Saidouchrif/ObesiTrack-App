from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
# Add the parent directory to the path to access the models directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from models.User import create_user, authenticate_user
from models.Auth import get_current_user
from models.Predict import create_predict, get_user_predictions, get_prediction_by_id, delete_prediction

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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

templates = Jinja2Templates(directory='../Front-end/src')

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("Home.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("Login.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("Register.html", {"request": request})

@app.get("/predict")
def predict_page(request: Request):
    return templates.TemplateResponse("Predict.html", {"request": request})

@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("Dashboard.html", {"request": request})

@app.get("/statistics")
def statistics_page(request: Request):
    return templates.TemplateResponse("Statistics.html", {"request": request})

@app.get("/history")
def history_page(request: Request):
    return templates.TemplateResponse("History.html", {"request": request})


@app.post("/signup")
def signup(user: UserSignup):
    return create_user(user.email, user.name, user.password)

@app.post('/login')
def login(user: UserLogin):
    return authenticate_user(user.email, user.password)

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    """Route protégée accessible uniquement avec un token JWT valide"""
    return {
        "message": f"Accès autorisé pour {current_user['email']}",
        "user": current_user
    }

@app.post("/predict")
def create_prediction(prediction_data: PredictionData, current_user: dict = Depends(get_current_user)):
    """Créer une nouvelle prédiction pour l'utilisateur authentifié"""
    try:
        # Convertir les données en dictionnaire
        predict_dict = prediction_data.dict()
        
        # Créer la prédiction avec l'ID de l'utilisateur
        result = create_predict(current_user['email'], predict_dict)
        
        # Appel au modèle ML réel via l'API externe
        try:
            import requests
            from models.Auth import create_access_token
            
            # Appeler l'API du modèle ML sur le port 8000
            ml_api_url = "http://localhost:8000/predict"
            
            # Créer un token JWT pour l'API ML
            ml_token = create_access_token(data={"sub": current_user['email']})
            
            # Préparer les données pour l'API ML
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
            
            # Headers avec authentification JWT
            headers = {
                "Authorization": f"Bearer {ml_token}",
                "Content-Type": "application/json"
            }
            
            # Faire l'appel à l'API ML
            ml_response = requests.post(ml_api_url, json=ml_data, headers=headers, timeout=10)
            
            if ml_response.status_code == 200:
                ml_result = ml_response.json()
                
                return {
                    "message": "Prédiction créée avec succès",
                    "predict_id": result["predict_id"],
                    "prediction": ml_result.get("prediction", "Unknown"),
                    "probabilities": ml_result.get("probabilities", {}),
                    "user_id": current_user['email'],
                    "ml_status": "success"
                }
            else:
                raise Exception(f"API ML returned status {ml_response.status_code}: {ml_response.text}")
            
        except Exception as ml_error:
            # En cas d'erreur avec l'API ML, utiliser une prédiction de fallback
            print(f"Erreur API ML: {ml_error}")
            import random
            categories = [
                'Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I', 
                'Overweight_Level_II', 'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III'
            ]
            
            prediction = random.choice(categories)
            probabilities = {cat: random.random() for cat in categories}
            
            return {
                "message": "Prédiction créée avec succès (mode fallback - API ML indisponible)",
                "predict_id": result["predict_id"],
                "prediction": prediction,
                "probabilities": probabilities,
                "user_id": current_user['email'],
                "ml_status": "fallback",
                "ml_error": str(ml_error)
            }
        
    except Exception as e:
        return {"error": f"Erreur lors de la création de la prédiction: {str(e)}"}

@app.get("/predictions")
def get_predictions(current_user: dict = Depends(get_current_user), limit: int = 10):
    """Récupérer les prédictions de l'utilisateur authentifié"""
    try:
        predictions = get_user_predictions(current_user['email'], limit)
        return {
            "predictions": predictions,
            "count": len(predictions),
            "user_id": current_user['email']
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération des prédictions: {str(e)}"}

@app.get("/predictions/{predict_id}")
def get_prediction(predict_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer une prédiction spécifique de l'utilisateur authentifié"""
    try:
        prediction = get_prediction_by_id(predict_id, current_user['email'])
        if prediction:
            return {
                "prediction": prediction,
                "user_id": current_user['email']
            }
        else:
            return {"error": "Prédiction non trouvée ou non autorisée"}
    except Exception as e:
        return {"error": f"Erreur lors de la récupération de la prédiction: {str(e)}"}

@app.delete("/predictions/{predict_id}")
def delete_prediction_endpoint(predict_id: str, current_user: dict = Depends(get_current_user)):
    """Supprimer une prédiction de l'utilisateur authentifié"""
    try:
        result = delete_prediction(predict_id, current_user['email'])
        return result
    except Exception as e:
        return {"error": f"Erreur lors de la suppression de la prédiction: {str(e)}"}