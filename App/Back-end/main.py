from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
# Add the parent directory to the path to access the models directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from models.User import create_user, authenticate_user

app = FastAPI()
class UserSignup(BaseModel):
    email: str
    name: str
    password: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the ObesiTrack API"}

@app.post("/signup")
def signup(user: UserSignup):
    return create_user(user.email, user.name, user.password)

@app.post('/login')
def login(user: UserSignup):
    return authenticate_user(user.email, user.password)