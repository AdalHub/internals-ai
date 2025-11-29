
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv("../../.env")
mongodb_username=os.getenv('MONGO_DB_USERNAME')
mongodb_password=os.getenv('MONGO_DB_PASSWORD')

uri =f"mongodb+srv://{mongodb_username}:{mongodb_password}@internal-ai.wmzdete.mongodb.net/?appName=internal-ai"


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)