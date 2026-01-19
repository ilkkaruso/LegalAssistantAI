"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user.
    
    Args:
        user_data: The user registration data
        session: The database session
        
    Returns:
        The created user
        
    Raises:
        HTTPException: If email already exists
    """
    auth_service = AuthService(session)
    user = await auth_service.register_user(user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_db)
) -> Token:
    """Login and get access token.
    
    Args:
        login_data: The user login credentials
        session: The database session
        
    Returns:
        The JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(session)
    token = await auth_service.login(login_data)
    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
) -> UserResponse:
    """Get current user information.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The current user information
    """
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> Token:
    """Refresh access token.
    
    Args:
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        A new JWT access token
    """
    auth_service = AuthService(session)
    token = auth_service.create_access_token_for_user(current_user)
    return token
