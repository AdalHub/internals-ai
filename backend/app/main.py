from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from routers import users


my_app = FastAPI()


#CORS and other middleware
my_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#we add necessary routers
my_app.include_router(users)




#test function
@my_app.get("/")
def root():
    return {"msg":"hello world"}



