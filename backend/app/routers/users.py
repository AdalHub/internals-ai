from fastapi import APIRouter, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient    
from pymongo.server_api import ServerApi    
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError
from typing import Optional
from datetime import datetime
import pprint
import os
from bson.objectid import ObjectId
from database import db

router = APIRouter(
    prefix="/user",
    tags=['users']
)



#creating users collection inside internals_ai_db if not already created
users_collection= db.users


################################# USER ENDPOINTS #################################




'''//////////////////////////// USER CREATION ////////////////////////////'''


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


@router.post("/", response_model=User_Insert_Responce)
async def create_user(user_obj:User_Structure):
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




'''//////////////////////////// USER UPDATING ////////////////////////////'''

class User_Update_Response(BaseModel):
    status:bool
    message:str
    modified_count: int

class UpdateUser(BaseModel):
    username:Optional[str]= None
    first_name:Optional[str]= None
    last_name:Optional[str]= None
    email:Optional[str]= None
    auth_level:Optional[str]= None
    date: Optional[str]= None

@router.put('/{person_id}}', response_model=User_Update_Response)
async def update_user(person_id ,user_obj: UpdateUser):
    try:
        _id= ObjectId(person_id)


        user_doc_updated= user_obj.model_dump(exclude_none= True)
        update_items = {k:v for k,v in user_doc_updated.items() if v!= ""}

        #we check if there are any fields to actually update or we raise an error
        if not update_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = {
                    "error_type": "ValidationError",
                    "message": "No fields to update friend",
                    "details": "You must provide atleast one field to update friend"
                }
            )

        #we need to update by username, so we must first obtain their Object
        result= users_collection.update_one({"_id":_id}, {"$set": update_items})
        #verify the user document was found
        if result.modified_count==0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_type": "NotFound",
                    "message": "User not found",
                    "details": f"No user found with ID: {person_id}"
                }
            )
        #return successful response
        return User_Update_Response(
            status= True,
            message=f"Sucessfully updated {person_id} friend!",
            modified_count=result.modified_count
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




'''//////////////////////////// USER DELETE ////////////////////////////'''

