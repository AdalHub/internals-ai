# routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator
from database import db
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from auth import hash_password, verify_password, create_access_token, create_refresh_token
import re

router = APIRouter(prefix="/auth", tags=["authentication"])

# Models
class UserSignUp(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)  # No max length - unlimited!
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Enforce strong password requirements"""
        # Check minimum length
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for required character types
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

# Endpoints
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignUp):
    """Register a new user"""
    try:
        # Check if user already exists
        if db['users'].find_one({"email": user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if db['users'].find_one({"username": user.username}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash the password (now handles unlimited length!)
        hashed_password = hash_password(user.password)
        
        # Create user document
        user_doc = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "auth_level": "user",
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db['users'].insert_one(user_doc)
        
        # Create tokens for automatic login after signup
        access_token = create_access_token(data={"sub": str(result.inserted_id)})
        refresh_token = create_refresh_token(data={"sub": str(result.inserted_id)})
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": str(result.inserted_id),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return tokens"""
    # Find user by email or username
    user = db['users'].find_one({"email": form_data.username})
    if not user:
        user = db['users'].find_one({"username": form_data.username})
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user['_id'])})
    refresh_token = create_refresh_token(data={"sub": str(user['_id'])})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user['_id']),
            "username": user['username'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "auth_level": user.get('auth_level', 'user')
        }
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Get new access token using refresh token"""
    from jose import jwt, JWTError
    from auth import SECRET_KEY, ALGORITHM
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise credentials_exception
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise credentials_exception