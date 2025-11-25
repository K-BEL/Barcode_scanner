"""User management API routes."""
from typing import Dict
from fastapi import APIRouter, Query

from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
def add_user(user: UserCreate):
    """
    Add a new user.
    
    Args:
        user: User data
        
    Returns:
        Created user information
    """
    service = UserService()
    created_user = service.add_user(user.name)
    
    added_at = created_user['added_at']
    modified_at = created_user.get('modified_at')
    
    if hasattr(added_at, 'isoformat'):
        added_at = added_at.isoformat()
    if modified_at and hasattr(modified_at, 'isoformat'):
        modified_at = modified_at.isoformat()
    
    return UserResponse(
        id=created_user['id'],
        name=created_user['name'],
        added_at=str(added_at),
        modified_at=str(modified_at) if modified_at else None
    )


@router.put("/{user_id}", response_model=UserResponse)
def modify_user(user_id: str, name: str = Query(..., description="New user name")):
    """
    Modify an existing user.
    
    Args:
        user_id: User ID
        name: New user name
        
    Returns:
        Updated user information
    """
    service = UserService()
    updated_user = service.update_user(user_id, name)
    
    added_at = updated_user['added_at']
    modified_at = updated_user.get('modified_at')
    
    if hasattr(added_at, 'isoformat'):
        added_at = added_at.isoformat()
    if modified_at and hasattr(modified_at, 'isoformat'):
        modified_at = modified_at.isoformat()
    
    return UserResponse(
        id=updated_user['id'],
        name=updated_user['name'],
        added_at=str(added_at),
        modified_at=str(modified_at) if modified_at else None
    )


@router.delete("/{user_id}")
def delete_user(user_id: str):
    """
    Delete a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Success message
    """
    service = UserService()
    deleted_user = service.delete_user(user_id)
    
    return {
        "message": "User deleted successfully",
        "deleted_user": {
            "id": deleted_user['id'],
            "name": deleted_user['name']
        }
    }


@router.get("", response_model=Dict[str, UserResponse])
def get_users():
    """
    Get all users.
    
    Returns:
        Dictionary of all users
    """
    service = UserService()
    users = service.get_all_users()
    
    result = {}
    for user in users:
        added_at = user['added_at']
        modified_at = user.get('modified_at')
        
        if hasattr(added_at, 'isoformat'):
            added_at = added_at.isoformat()
        if modified_at and hasattr(modified_at, 'isoformat'):
            modified_at = modified_at.isoformat()
        
        result[user['id']] = UserResponse(
            id=user['id'],
            name=user['name'],
            added_at=str(added_at),
            modified_at=str(modified_at) if modified_at else None
        )
    
    return result
