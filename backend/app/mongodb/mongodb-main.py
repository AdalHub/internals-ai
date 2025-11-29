
from pymongo.mongo_client import MongoClient    
from pymongo.server_api import ServerApi    
from dotenv import load_dotenv
import os
from datetime import datetime

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



#automatically create a new db
db =client.internals_ai_db



#creating users collection
users_collection= db.users




user_test = {
    "name": "jose",
    "age":53,
    "access_leve": "admin",
    "created_at": datetime.now()
}
result=users_collection.insert_one(user_test)
print(f"result from test user insert: {result.inserted_id}")

multiple_users = [
    {
        "name": "justin",
        "age":25,
        "access_leve": "user",
        "created_at": datetime.now()
    },
    {
        "name": "sam",
        "age":25,
        "access_leve": "user",
        "created_at": datetime.now()
    },
    {
        "name": "alex",
        "age":24,
        "access_leve": "user",
        "created_at": datetime.now()
    },
]

result_1= users_collection.insert_many(multiple_users)
print(f"successfully inserted this many test users: {len(result.inserted_ids)}")

#listing database names
print(client.list_database_names())
