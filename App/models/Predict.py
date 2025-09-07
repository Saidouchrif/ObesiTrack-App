from .Connection import collection_predict
from datetime import datetime
from bson import ObjectId

def create_predict(user_id: str, predict_data: dict):
    """
    Créer une nouvelle prédiction associée à un utilisateur
    """
    predict_record = {
        "user_id": user_id,
        "prediction_data": predict_data,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection_predict.insert_one(predict_record)
    return {
        "message": "Prédiction créée avec succès",
        "predict_id": str(result.inserted_id)
    }

def get_user_predictions(user_id: str, limit: int = 10):
    """
    Récupérer les prédictions d'un utilisateur
    """
    predictions = list(collection_predict.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit))
    
    # Convertir ObjectId en string pour la sérialisation JSON
    for pred in predictions:
        pred["_id"] = str(pred["_id"])
        pred["created_at"] = pred["created_at"].isoformat()
        pred["updated_at"] = pred["updated_at"].isoformat()
    
    return predictions

def get_prediction_by_id(predict_id: str, user_id: str):
    """
    Récupérer une prédiction spécifique par ID (vérification que l'utilisateur en est propriétaire)
    """
    try:
        prediction = collection_predict.find_one({
            "_id": ObjectId(predict_id),
            "user_id": user_id
        })
        
        if prediction:
            prediction["_id"] = str(prediction["_id"])
            prediction["created_at"] = prediction["created_at"].isoformat()
            prediction["updated_at"] = prediction["updated_at"].isoformat()
        
        return prediction
    except Exception as e:
        return None

def delete_prediction(predict_id: str, user_id: str):
    """
    Supprimer une prédiction (vérification que l'utilisateur en est propriétaire)
    """
    try:
        result = collection_predict.delete_one({
            "_id": ObjectId(predict_id),
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            return {"message": "Prédiction supprimée avec succès"}
        else:
            return {"message": "Prédiction non trouvée ou non autorisée"}
    except Exception as e:
        return {"message": "Erreur lors de la suppression"}