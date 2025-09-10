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
from models.Result import save_prediction_result, get_user_results, get_result_by_predict_id, get_all_results_for_admin, delete_result

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

@app.get("/admin")
def admin_page(request: Request):
    return templates.TemplateResponse("AdminDashboard.html", {"request": request})

@app.get("/admin/users/add")
def add_user_page(request: Request):
    return templates.TemplateResponse("User/AjouterUser.html", {"request": request})

@app.get("/admin/users/edit/{user_email}")
def edit_user_page(request: Request, user_email: str):
    return templates.TemplateResponse("User/ModifierUser.html", {"request": request, "user_email": user_email})


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
                
                # Sauvegarder le résultat de la prédiction
                prediction = ml_result.get("prediction", "Unknown")
                probabilities = ml_result.get("probabilities", {})
                
                save_result = save_prediction_result(
                    user_id=current_user['email'],
                    predict_id=result["predict_id"],
                    prediction=prediction,
                    probabilities=probabilities,
                    prediction_data=predict_dict,
                    ml_status="success"
                )
                
                return {
                    "message": "Prédiction créée avec succès",
                    "predict_id": result["predict_id"],
                    "result_id": save_result["result_id"],
                    "prediction": prediction,
                    "probabilities": probabilities,
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
            
            # Sauvegarder le résultat de la prédiction fallback
            save_result = save_prediction_result(
                user_id=current_user['email'],
                predict_id=result["predict_id"],
                prediction=prediction,
                probabilities=probabilities,
                prediction_data=predict_dict,
                ml_status="fallback"
            )
            
            return {
                "message": "Prédiction créée avec succès (mode fallback - API ML indisponible)",
                "predict_id": result["predict_id"],
                "result_id": save_result["result_id"],
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

@app.get("/results")
def get_results(current_user: dict = Depends(get_current_user), limit: int = 10):
    """Récupérer les résultats de prédiction de l'utilisateur authentifié"""
    try:
        results = get_user_results(current_user['email'], limit)
        return {
            "results": results,
            "count": len(results),
            "user_id": current_user['email']
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération des résultats: {str(e)}"}

@app.get("/results/{predict_id}")
def get_result(predict_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un résultat de prédiction spécifique de l'utilisateur authentifié"""
    try:
        result = get_result_by_predict_id(predict_id, current_user['email'])
        if result:
            return {
                "result": result,
                "user_id": current_user['email']
            }
        else:
            return {"error": "Résultat non trouvé ou non autorisé"}
    except Exception as e:
        return {"error": f"Erreur lors de la récupération du résultat: {str(e)}"}

@app.delete("/results/{result_id}")
def delete_result_endpoint(result_id: str, current_user: dict = Depends(get_current_user)):
    """Supprimer un résultat de prédiction de l'utilisateur authentifié"""
    try:
        result = delete_result(result_id, current_user['email'])
        return result
    except Exception as e:
        return {"error": f"Erreur lors de la suppression du résultat: {str(e)}"}

@app.get("/admin/results")
def get_all_results_admin(current_user: dict = Depends(get_current_user), limit: int = 50):
    """Récupérer tous les résultats pour l'admin"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection
        user = collection.find_one({"email": current_user['email']})
        if not user or user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        results = get_all_results_for_admin(limit)
        return {
            "results": results,
            "count": len(results),
            "admin_user": current_user['email']
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération des résultats admin: {str(e)}"}

@app.get("/admin/users")
def get_all_users_admin(current_user: dict = Depends(get_current_user)):
    """Récupérer tous les utilisateurs pour l'admin"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection
        user = collection.find_one({"email": current_user['email']})
        if not user or user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        # Récupérer tous les utilisateurs (sans les mots de passe)
        users = list(collection.find({}, {"password": 0}))
        
        # Convertir ObjectId en string
        for user in users:
            user["_id"] = str(user["_id"])
        
        return {
            "users": users,
            "count": len(users),
            "admin_user": current_user['email']
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération des utilisateurs: {str(e)}"}

@app.get("/admin/user/{user_email}/results")
def get_user_results_admin(user_email: str, current_user: dict = Depends(get_current_user)):
    """Récupérer les résultats d'un utilisateur spécifique pour l'admin"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection
        user = collection.find_one({"email": current_user['email']})
        if not user or user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        # Récupérer les résultats de l'utilisateur spécifique
        results = get_user_results(user_email, limit=100)
        
        return {
            "results": results,
            "count": len(results),
            "user_email": user_email,
            "admin_user": current_user['email']
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération des résultats de l'utilisateur: {str(e)}"}

@app.get("/admin/statistics")
def get_admin_statistics(current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques globales pour l'admin"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection
        user = collection.find_one({"email": current_user['email']})
        if not user or user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        # Statistiques des utilisateurs
        total_users = collection.count_documents({})
        admin_users = collection.count_documents({"Role": "admin"})
        regular_users = collection.count_documents({"Role": "user"})
        
        # Statistiques des prédictions
        from models.Connection import collection_result
        total_predictions = collection_result.count_documents({})
        
        # Distribution des catégories
        pipeline = [
            {"$group": {"_id": "$prediction", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_distribution = list(collection_result.aggregate(pipeline))
        
        # Utilisateurs les plus actifs
        user_activity_pipeline = [
            {"$group": {"_id": "$user_id", "prediction_count": {"$sum": 1}}},
            {"$sort": {"prediction_count": -1}},
            {"$limit": 10}
        ]
        most_active_users = list(collection_result.aggregate(user_activity_pipeline))
        
        return {
            "user_stats": {
                "total_users": total_users,
                "admin_users": admin_users,
                "regular_users": regular_users
            },
            "prediction_stats": {
                "total_predictions": total_predictions,
                "category_distribution": category_distribution,
                "most_active_users": most_active_users
            },
            "admin_user": current_user['email']
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération des statistiques: {str(e)}"}

@app.post("/admin/users")
def create_user_admin(user_data: dict, current_user: dict = Depends(get_current_user)):
    """Créer un nouvel utilisateur (admin seulement)"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection
        user = collection.find_one({"email": current_user['email']})
        if not user or user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        # Extraire les données
        email = user_data.get("email")
        name = user_data.get("name")
        password = user_data.get("password")
        role = user_data.get("role", "user")
        
        if not email or not name or not password:
            return {"error": "Email, nom et mot de passe requis"}
        
        # Vérifier si l'utilisateur existe déjà
        if collection.find_one({"email": email}):
            return {"error": "Un utilisateur avec cet email existe déjà"}
        
        # Créer l'utilisateur
        result = create_user(email, name, password, role)
        
        return {
            "message": "Utilisateur créé avec succès",
            "user": {
                "email": email,
                "name": name,
                "role": role
            }
        }
    except Exception as e:
        return {"error": f"Erreur lors de la création de l'utilisateur: {str(e)}"}

@app.put("/admin/users/{user_email}")
def update_user_admin(user_email: str, user_data: dict, current_user: dict = Depends(get_current_user)):
    """Modifier un utilisateur (admin seulement)"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection
        admin_user = collection.find_one({"email": current_user['email']})
        if not admin_user or admin_user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        # Vérifier si l'utilisateur à modifier existe
        user_to_update = collection.find_one({"email": user_email})
        if not user_to_update:
            return {"error": "Utilisateur non trouvé"}
        
        # Préparer les données de mise à jour
        update_data = {}
        
        if "name" in user_data:
            update_data["name"] = user_data["name"]
        
        if "role" in user_data:
            update_data["Role"] = user_data["role"]
        
        if "password" in user_data and user_data["password"]:
            import bcrypt
            hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
            update_data["password"] = hashed_password
        
        # Mettre à jour l'utilisateur
        collection.update_one(
            {"email": user_email},
            {"$set": update_data}
        )
        
        # Récupérer l'utilisateur mis à jour
        updated_user = collection.find_one({"email": user_email}, {"password": 0})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "message": "Utilisateur mis à jour avec succès",
            "user": updated_user
        }
    except Exception as e:
        return {"error": f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"}

@app.delete("/admin/users/{user_email}")
def delete_user_admin(user_email: str, current_user: dict = Depends(get_current_user)):
    """Supprimer un utilisateur (admin seulement)"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection, collection_result, collection_predict
        admin_user = collection.find_one({"email": current_user['email']})
        if not admin_user or admin_user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        # Vérifier si l'utilisateur à supprimer existe
        user_to_delete = collection.find_one({"email": user_email})
        if not user_to_delete:
            return {"error": "Utilisateur non trouvé"}
        
        # Empêcher la suppression de l'admin actuel
        if user_email == current_user['email']:
            return {"error": "Vous ne pouvez pas supprimer votre propre compte"}
        
        # Supprimer l'utilisateur et toutes ses données associées
        # 1. Supprimer les prédictions
        collection_predict.delete_many({"user_id": user_email})
        
        # 2. Supprimer les résultats
        collection_result.delete_many({"user_id": user_email})
        
        # 3. Supprimer l'utilisateur
        result = collection.delete_one({"email": user_email})
        
        if result.deleted_count > 0:
            return {"message": "Utilisateur et toutes ses données supprimés avec succès"}
        else:
            return {"error": "Erreur lors de la suppression de l'utilisateur"}
    except Exception as e:
        return {"error": f"Erreur lors de la suppression de l'utilisateur: {str(e)}"}

@app.get("/admin/users/{user_email}")
def get_user_admin(user_email: str, current_user: dict = Depends(get_current_user)):
    """Récupérer les détails d'un utilisateur (admin seulement)"""
    try:
        # Vérifier si l'utilisateur est admin
        from models.Connection import collection
        admin_user = collection.find_one({"email": current_user['email']})
        if not admin_user or admin_user.get("Role") != "admin":
            return {"error": "Accès non autorisé - Admin requis"}
        
        # Récupérer l'utilisateur (sans le mot de passe)
        user = collection.find_one({"email": user_email}, {"password": 0})
        
        if not user:
            return {"error": "Utilisateur non trouvé"}
        
        user["_id"] = str(user["_id"])
        
        return {
            "user": user,
            "admin_user": current_user['email']
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération de l'utilisateur: {str(e)}"}