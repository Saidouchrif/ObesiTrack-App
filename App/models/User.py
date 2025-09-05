from .Connection import collection
import bcrypt
from fastapi import HTTPException
from .Auth import create_access_token
from datetime import timedelta

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
    
    # Création du token JWT
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, 
        expires_delta=access_token_expires
    )
    
    # Retour du token avec les informations utilisateur
    return {
        "name": user["name"],
        "email": user["email"],
        "token": access_token
    }