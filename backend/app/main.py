from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

my_app = FastAPI()

origins = ["http://localhost:3000"]

my_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@my_app.get("/")
def getStuff():
    return {"mgs":"hello world"}
