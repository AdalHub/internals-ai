# routers/users.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError
from typing import Optional
from datetime import datetime
from bson.objectid import ObjectId
from database import db
from auth import get_current_user, get_current_active_user

router = APIRouter(
    prefix="/user",
    tags=['users']
)

# Creating users collection
users_collection = db.users

# Models
class User_Update_Response(BaseModel):
    status: bool
    message: str
    modified_count: int

class UpdateUser(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

# Protected endpoints (require authentication)
@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user's profile"""
    current_user['_id'] = str(current_user['_id'])
    current_user.pop('password', None)  # Never return password
    return current_user

@router.put("/me", response_model=User_Update_Response)
async def update_current_user_profile(
    user_obj: UpdateUser,
    current_user: dict = Depends(get_current_user)
):
    """Update current authenticated user's profile"""
    try:
        user_doc_updated = user_obj.model_dump(exclude_none=True)
        update_items = {k: v for k, v in user_doc_updated.items() if v != ""}
        
        if not update_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_type": "ValidationError",
                    "message": "No fields to update",
                    "details": "You must provide at least one field to update"
                }
            )
        
        # Add updated_at timestamp
        update_items['updated_at'] = datetime.now()
        
        # Update user
        result = users_collection.update_one(
            {"_id": current_user['_id']},
            {"$set": update_items}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_type": "NotFound",
                    "message": "User not found"
                }
            )
        
        return User_Update_Response(
            status=True,
            message="Successfully updated your profile!",
            modified_count=result.modified_count
        )
        
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_type": "DuplicateKeyError",
                "message": "Email or username already exists",
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

@router.delete("/me")
async def delete_current_user_account(current_user: dict = Depends(get_current_user)):
    """Delete current authenticated user's account (soft delete)"""
    try:
        # Soft delete - just mark as inactive
        result = users_collection.update_one(
            {"_id": current_user['_id']},
            {"$set": {"is_active": False, "deleted_at": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": "Account deactivated successfully"
        }
        
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "PyMongoError", "message": str(e)}
        )

# Admin-only endpoints (require admin authentication)
@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user by ID (admin only)"""
    # Check if current user is admin
    if current_user.get('auth_level') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view other users"
        )
    
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user['_id'] = str(user['_id'])
        user.pop('password', None)
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user.get('auth_level') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all users"
        )
    
    try:
        users = list(users_collection.find({}))
        for user in users:
            user['_id'] = str(user['_id'])
            user.pop('password', None)
        return {"users": users, "count": len(users)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )