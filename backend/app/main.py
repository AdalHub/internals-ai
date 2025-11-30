from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient    
from pymongo.server_api import ServerApi    
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError
from typing import Optional
from datetime import datetime
import pprint
from dotenv import load_dotenv
import os
my_app = FastAPI()

load_dotenv("../.env")
mongodb_username=os.getenv('MONGO_DB_USERNAME')
mongodb_password=os.getenv('MONGO_DB_PASSWORD')

uri =f"mongodb+srv://{mongodb_username}:{mongodb_password}@internal-ai.wmzdete.mongodb.net/?appName=internal-ai"


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))


#automatically create a new db if non existent 
db =client.internals_ai_db

#creating users collection inside internals_ai_db if not already created
users_collection= db.users

#test function
@my_app.get("/")
def root():
    return {"msg":"hello world"}

documents= []




######################## USERS ########################


class User_Insert_Responce(BaseModel):
    status:bool
    message:str
    inserted_id: str=None

class User_Structure(BaseModel):
    username:str
    fisrt_name:str
    last_name:str
    email:str
    auth_level:str
    date: str=None


class UpdateUser(BaseModel):
    username:Optional[str]= None
    fisrt_name:Optional[str]= None
    last_name:Optional[str]= None
    email:Optional[str]= None
    auth_level:Optional[str]= None
    date: Optional[str]= None

@my_app.post("/users", response_model=User_Insert_Responce)
async def createUser(user_obj:User_Structure):
    try:
        user_doc= user_obj.model_dump()
        #before we insert the user object we must add the date from our backend
        #this is to for simplicity preventing any erros with the date formatting or client-side manipulation
        user_doc['date']= datetime.now()
        #insert new user
        result= users_collection.insert_one(user_doc)
        #create a printer for logging
        printer= pprint.PrettyPrinter()
        printer.pprint(result.inserted_id)
        return User_Insert_Responce(
            status= True,
            message="Sucessfully inserted new user friend!",
            inserted_id=str(result.inserted_id)
        )
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_type": "DuplicateKeyError",
                "message": "A document with this key already exists",
                "details": str(e)
            }
        )
    
    except WriteError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_type": "WriteError",
                "message": "Document validation failed",
                "details": str(e)
            }
        )
    
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "PyMongoError",
                "message": "Database error occurred",
                "details": str(e)
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "UnexpectedError",
                "message": "An unexpected error occurred",
                "details": str(e)
            }
        )
