"""User repository for database operations."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.auth import UserCreate, UserUpdate
from src.utils.security import get_password_hash


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: The async database session
        """
        self.session = session
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user.
        
        Args:
            user_data: The user data to create
            
        Returns:
            The created user
        """
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            organization=user_data.organization,
            role=user_data.role,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
            is_verified=user_data.is_verified,
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.
        
        Args:
            email: The user email
            
        Returns:
            The user if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update(self, user: User, user_data: UserUpdate) -> User:
        """Update a user.
        
        Args:
            user: The user to update
            user_data: The updated user data
            
        Returns:
            The updated user
        """
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def delete(self, user: User) -> None:
        """Delete a user.
        
        Args:
            user: The user to delete
        """
        await self.session.delete(user)
        await self.session.commit()
    
    async def update_last_login(self, user: User) -> User:
        """Update the user's last login timestamp.
        
        Args:
            user: The user to update
            
        Returns:
            The updated user
        """
        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(user)
        return user
