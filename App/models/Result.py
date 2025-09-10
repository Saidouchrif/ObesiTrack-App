from .Connection import collection_result
from datetime import datetime
from bson import ObjectId

def save_prediction_result(user_id: str, predict_id: str, prediction: str, probabilities: dict, prediction_data: dict = None, ml_status: str = "success"):
    """
    Sauvegarder le résultat d'une prédiction avec l'ID utilisateur
    """
    result_record = {
        "user_id": user_id,
        "predict_id": predict_id,
        "prediction": prediction,
        "probabilities": probabilities,
        "prediction_data": prediction_data,  # Ajouter les données originales
        "ml_status": ml_status,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection_result.insert_one(result_record)
    return {
        "message": "Résultat de prédiction sauvegardé avec succès",
        "result_id": str(result.inserted_id)
    }

def get_user_results(user_id: str, limit: int = 10):
    """
    Récupérer les résultats de prédiction d'un utilisateur
    """
    results = list(collection_result.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit))
    
    # Convertir ObjectId en string pour la sérialisation JSON
    for result in results:
        result["_id"] = str(result["_id"])
        result["created_at"] = result["created_at"].isoformat()
        result["updated_at"] = result["updated_at"].isoformat()
    
    return results

def get_result_by_predict_id(predict_id: str, user_id: str):
    """
    Récupérer un résultat de prédiction par ID de prédiction
    """
    try:
        result = collection_result.find_one({
            "predict_id": predict_id,
            "user_id": user_id
        })
        
        if result:
            result["_id"] = str(result["_id"])
            result["created_at"] = result["created_at"].isoformat()
            result["updated_at"] = result["updated_at"].isoformat()
        
        return result
    except Exception as e:
        return None

def get_all_results_for_admin(limit: int = 50):
    """
    Récupérer tous les résultats pour l'admin (sans filtre utilisateur)
    """
    results = list(collection_result.find().sort("created_at", -1).limit(limit))
    
    # Convertir ObjectId en string pour la sérialisation JSON
    for result in results:
        result["_id"] = str(result["_id"])
        result["created_at"] = result["created_at"].isoformat()
        result["updated_at"] = result["updated_at"].isoformat()
    
    return results

def delete_result(result_id: str, user_id: str):
    """
    Supprimer un résultat de prédiction
    """
    try:
        result = collection_result.delete_one({
            "_id": ObjectId(result_id),
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            return {"message": "Résultat supprimé avec succès"}
        else:
            return {"message": "Résultat non trouvé ou non autorisé"}
    except Exception as e:
        return {"message": "Erreur lors de la suppression"}
