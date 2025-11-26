from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

#test function
@my_app.get("/")
def getStuff():
    return {"mgs":"hello world"}


#we will post iternal document here
@my_app.post("/items")
def createItems(document: str):
    documents.append(document)
    return document

#view specific item
@my_app.get("/items/{itemId}")
def getItem(itemId: int):
    if itemId not in range(len(documents)):
        return "not found"
    else:
        return documents[itemId]