
from pymongo.mongo_client import MongoClient    
from pymongo.server_api import ServerApi    
from dotenv import load_dotenv
import os
from datetime import datetime
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError
load_dotenv("../../.env")
mongodb_username=os.getenv('MONGO_DB_USERNAME')
mongodb_password=os.getenv('MONGO_DB_PASSWORD')

uri =f"mongodb+srv://{mongodb_username}:{mongodb_password}@internal-ai.wmzdete.mongodb.net/?appName=internal-ai"


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))


#automatically create a new db if non existent 
db =client.internals_ai_db

#creating users collection inside internals_ai_db if not already created
users_collection= db.users


def insert_new_user(collection,user_obj):
    try:
        result= collection.insert_one(user_obj)
        (f"result from test user insert: {result.inserted_id}")
    except DuplicateKeyError as e:
        print(f"Duplicate key error: {e}")
        # Handle duplicate _id or unique index violations
        return None
    
    except WriteError as e:
        print(f"Write error: {e}")
        # Handle validation errors or other write issues
        return None
    
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
        # Catch any other MongoDB-related errors
        return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Catch any non-MongoDB errors
        return None

result=users_collection.insert_one(user_test)


