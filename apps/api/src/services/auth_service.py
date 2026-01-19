"""Authentication service layer."""
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.repositories.user_repository import UserRepository
from src.models.user import User
from src.schemas.auth import Token, UserCreate, UserLogin, UserRegister
from src.utils.security import create_access_token, verify_password


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service with database session.
        
        Args:
            session: The async database session
        """
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def register_user(self, user_data: UserRegister) -> User:
        """Register a new user.
        
        Args:
            user_data: The user registration data
            
        Returns:
            The created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            organization=user_data.organization,
            role=user_data.role,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        
        user = await self.user_repo.create(user_create)
        return user
    
    async def authenticate_user(self, login_data: UserLogin) -> User:
        """Authenticate a user with email and password.
        
        Args:
            login_data: The user login credentials
            
        Returns:
            The authenticated user
            
        Raises:
            HTTPException: If authentication fails
        """
        # Get user by email
        user = await self.user_repo.get_by_email(login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        await self.user_repo.update_last_login(user)
        
        return user
    
    def create_access_token_for_user(self, user: User) -> Token:
        """Create an access token for a user.
        
        Args:
            user: The user to create token for
            
        Returns:
            The JWT token
        """
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    async def login(self, login_data: UserLogin) -> Token:
        """Login a user and return access token.
        
        Args:
            login_data: The user login credentials
            
        Returns:
            The JWT access token
        """
        user = await self.authenticate_user(login_data)
        token = self.create_access_token_for_user(user)
        return token
