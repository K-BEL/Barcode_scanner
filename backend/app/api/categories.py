"""Category management API routes."""
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService
from app.core.dependencies import get_category_service
from app.utils.datetime_utils import serialize_datetime

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse)
def add_category(
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service)
):
    """
    Add a new category.
    
    Args:
        category: Category data
        service: Category service dependency
        
    Returns:
        Created category information
    """
    created_category = service.add_category(category.dict())
    
    return CategoryResponse(
        id=created_category['id'],
        name=created_category['name'],
        description=created_category.get('description'),
        created_at=serialize_datetime(created_category['created_at'])
    )


@router.put("/{category_id}", response_model=CategoryResponse)
def modify_category(
    category_id: int,
    category: CategoryUpdate,
    service: CategoryService = Depends(get_category_service)
):
    """
    Modify an existing category.
    
    Args:
        category_id: Category ID
        category: Updated category data
        service: Category service dependency
        
    Returns:
        Updated category information
    """
    category_dict = {k: v for k, v in category.dict().items() if v is not None}
    updated_category = service.update_category(category_id, category_dict)
    
    return CategoryResponse(
        id=updated_category['id'],
        name=updated_category['name'],
        description=updated_category.get('description'),
        created_at=serialize_datetime(updated_category['created_at'])
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
):
    """
    Delete a category.
    
    Args:
        category_id: Category ID
        service: Category service dependency
        
    Returns:
        Success message
    """
    deleted_category = service.delete_category(category_id)
    
    return {
        "message": "Category deleted successfully",
        "deleted_category": {
            "id": deleted_category['id'],
            "name": deleted_category['name']
        }
    }


@router.get("", response_model=Dict[str, CategoryResponse])
def get_categories(
    service: CategoryService = Depends(get_category_service)
):
    """
    Get all categories.
    
    Args:
        service: Category service dependency
        
    Returns:
        Dictionary of categories
    """
    categories = service.get_all_categories()
    
    result = {}
    for category in categories:
        result[str(category['id'])] = CategoryResponse(
            id=category['id'],
            name=category['name'],
            description=category.get('description'),
            created_at=serialize_datetime(category['created_at'])
        )
    
    return result


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
):
    """
    Get a specific category by ID.
    
    Args:
        category_id: Category ID
        service: Category service dependency
        
    Returns:
        Category information
    """
    category = service.get_category(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return CategoryResponse(
        id=category['id'],
        name=category['name'],
        description=category.get('description'),
        created_at=serialize_datetime(category['created_at'])
    )

