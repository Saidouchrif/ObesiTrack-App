from .Connection import collection
import bcrypt
from fastapi import HTTPException

def create_user(email: str, name: str, password: str):
    if collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {"email": email, "name": name, "password": hashed_password}
    collection.insert_one(user)
    return {"message": "User created successfully"}

def authenticate_user(email: str, password: str):
    user = collection.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful"}