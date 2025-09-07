from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
try:
    client = MongoClient(MONGO_URI)
    dataBase = client[DB_NAME]
    collection = dataBase["Users"]
    collection_predict = dataBase["Predict"]
    print("Connected to MongoDB successfully")
except Exception as e:
    print("Error connecting to MongoDB:", e)
