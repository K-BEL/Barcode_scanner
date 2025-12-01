"""User management API routes."""
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.dependencies import get_user_service
from app.utils.datetime_utils import serialize_datetime_optional
from app.utils.validators import validate_user_id

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
def add_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    Add a new user.
    
    Args:
        user: User data
        service: User service dependency
        
    Returns:
        Created user information
    """
    created_user = service.add_user(user.name)
    
    return UserResponse(
        id=created_user['id'],
        name=created_user['name'],
        added_at=serialize_datetime_optional(created_user['added_at']),
        modified_at=serialize_datetime_optional(created_user.get('modified_at'))
    )


@router.put("/{user_id}", response_model=UserResponse)
def modify_user(
    user_id: str,
    name: str = Query(..., description="New user name", min_length=1, max_length=255),
    service: UserService = Depends(get_user_service)
):
    """
    Modify an existing user.
    
    Args:
        user_id: User ID
        name: New user name
        service: User service dependency
        
    Returns:
        Updated user information
    """
    # Validate user ID format
    try:
        user_id = validate_user_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Validate name
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="User name cannot be empty or whitespace only")
    name = name.strip()
    
    updated_user = service.update_user(user_id, name)
    
    return UserResponse(
        id=updated_user['id'],
        name=updated_user['name'],
        added_at=serialize_datetime_optional(updated_user['added_at']),
        modified_at=serialize_datetime_optional(updated_user.get('modified_at'))
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Delete a user.
    
    Args:
        user_id: User ID
        service: User service dependency
        
    Returns:
        Success message
    """
    # Validate user ID format
    try:
        user_id = validate_user_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    deleted_user = service.delete_user(user_id)
    
    return {
        "message": "User deleted successfully",
        "deleted_user": {
            "id": deleted_user['id'],
            "name": deleted_user['name']
        }
    }


@router.get("", response_model=Dict[str, UserResponse])
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    service: UserService = Depends(get_user_service)
):
    """
    Get all users with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        service: User service dependency
        
    Returns:
        Dictionary of users
    """
    users = service.get_all_users(page=page, page_size=page_size)
    
    result = {}
    for user in users:
        result[user['id']] = UserResponse(
            id=user['id'],
            name=user['name'],
            added_at=serialize_datetime_optional(user['added_at']),
            modified_at=serialize_datetime_optional(user.get('modified_at'))
        )
    
    return result
