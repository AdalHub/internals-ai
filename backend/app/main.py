# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routers import users
from routers import auth

my_app = FastAPI(
    title="Internal AI API",
    description="Now including professional authentication system with JWT",
    version="0.0.1"
)

# CORS middleware
my_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''
#Trusted host middleware for production
my_app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com"]
)
'''

# Include routers
my_app.include_router(auth.router)
my_app.include_router(users.router)

# Root endpoint
@my_app.get("/")
def root():
    return {
        "message": "Welcome to Internal AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }