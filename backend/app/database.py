# database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

load_dotenv("../.env")
mongodb_username=os.getenv('MONGO_DB_USERNAME')
mongodb_password=os.getenv('MONGO_DB_PASSWORD')
uri =f"mongodb+srv://{mongodb_username}:{mongodb_password}@internal-ai.wmzdete.mongodb.net/?appName=internal-ai"


#creates a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["internals_ai_db"]
