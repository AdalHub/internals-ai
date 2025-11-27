from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
my_app = FastAPI()
'''
origins = ["http://localhost:8000"]

my_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)'''
#placeholder for database
documents = []
#custom data classes
class User(BaseModel):
    username: str
    age: int
    access_level: str


class UpdateUser(BaseModel):
    username: Optional[str]= None
    age: Optional[int]= None
    access_level: Optional[str]= None

#placeholder for users
users={
    1:{
        "username": "adal",
        "age": 26,
        "access_level": "admin"
    },
    2:{
        "username": "anjelica",
        "age": 19,
        "access_level": "user"
    },
}

#test function
@my_app.get("/")
def root():
    return {"msg":"hello world"}




######################## documents ########################
#we will post iternal document here
@my_app.post("/items")
def createItems(document: str):
    documents.append(document)
    return document

@my_app.get("/items")
def getList(limit: int=10):
    return documents[0:limit]

#view specific item
@my_app.get("/item/{itemId}")
def getItem(itemId: int):
    if itemId > len(documents):
        raise HTTPException(status_code=404, detail=f"item {itemId} does not exists my friend")
    else:
        return documents[itemId]







######################## USERS ########################
#get access to user information
@my_app.get("/user/{userId}")
def getUser(userId: int):
    if userId not in users:
        raise HTTPException(status_code=404, detail= f" user id number could not be retrieved because {userId} does not exists friend")
    else:
        return users[userId]

#placeholder for user creation
@my_app.post("/users")
def createUser(userId:int, user: User):
    if userId in users:
        raise HTTPException(status_code=400)
    else:
        users[userId]= user
        return users[userId]
    
#placeholder for updating user info
@my_app.put("/users/{userId}")
def updateUser(userId: int, user: UpdateUser):
    if userId not in users:
        raise HTTPException(status_code=404, detail="{userId} does not exists friend")
    else:
        currentUser = users[userId]
        if user.username != None:
            currentUser["username"]= user.username
        if user.age != None:
            currentUser["age"]= user.age
        if user.access_level != None:
            currentUser["access_level"]= user.access_level
        return currentUser
#placeholder for deleting a user
@my_app.delete("/user/{userId}")
def deleteUser(userId: int):
    if userId not in users:
        raise HTTPException(status_code=404, detail="{userId} does not exists friend")
    deletedUser = users.pop(userId)
    return {"responce": f"{deletedUser} has been removed friend!"}

#placeholder searching by username
@my_app.get("/user_search")
def searchByName(name: Optional[str]=None):
    if not name:
        raise HTTPException(status_code=404,  detail="no name given friend")
    for user in users.values():
        if user["username"]== name:
            return user
    raise HTTPException(status_code=404)