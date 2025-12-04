"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.auth import UserLogin, UserRegister, UserAuthResponse, PasswordChange
from app.services.auth_service import AuthService
from app.core.dependencies import get_auth_service

security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service() -> AuthService:
    """Get auth service instance."""
    return AuthService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Get current authenticated user from token.
    
    Args:
        credentials: HTTP Bearer token credentials
        service: Auth service dependency
        
    Returns:
        User dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    user = service.get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    return user


@router.post("/register", response_model=UserAuthResponse)
def register(
    user_data: UserRegister,
    service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        service: Auth service dependency
        
    Returns:
        Created user information
    """
    user = service.register_user(
        username=user_data.username,
        password=user_data.password,
        name=user_data.name,
        email=user_data.email
    )
    
    # Create token for immediate login
    token_data = {
        "sub": user["user_id"],
        "username": user["username"],
        "roles": user["roles"]
    }
    access_token = service._create_access_token(data=token_data)
    
    return UserAuthResponse(
        user_id=user["user_id"],
        username=user["username"],
        name=user["name"],
        email=user.get("email"),
        roles=user["roles"],
        access_token=access_token
    )


@router.post("/login", response_model=UserAuthResponse)
def login(
    credentials: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate a user and return access token.
    
    Args:
        credentials: Login credentials
        service: Auth service dependency
        
    Returns:
        User information with access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = service.authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return UserAuthResponse(**user)


@router.get("/me", response_model=UserAuthResponse)
def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        User information
    """
    return UserAuthResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        name=current_user["name"],
        email=current_user.get("email"),
        roles=current_user["roles"]
    )


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Change user password.
    
    Args:
        password_data: Old and new password
        current_user: Current authenticated user
        service: Auth service dependency
        
    Returns:
        Success message
    """
    service.change_password(
        current_user["user_id"],
        password_data.old_password,
        password_data.new_password
    )
    
    return {"message": "Password changed successfully"}

