from .Connection import collection
import bcrypt
from fastapi import HTTPException

def create_user(email: str, name: str, password: str, role: str = "user"):
    if collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {"email": email, "name": name, "password": hashed_password, "Role": role}
    collection.insert_one(user)
    return {"message": "User created successfully"}

def authenticate_user(email: str, password: str):
    user = collection.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Vérification du rôle et retour du message approprié
    if user.get('Role') == "user":
        return {"message": "Login user successful", "role": "user"}
    elif user.get('Role') == "admin":
        return {"message": "Login admin successful", "role": "admin"}
    else:
        raise HTTPException(status_code=403, detail="Action non autorisée - Rôle non reconnu")