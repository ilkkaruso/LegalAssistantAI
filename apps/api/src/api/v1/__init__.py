"""API v1 routes."""
from fastapi import APIRouter
from src.api.v1 import auth, documents, search, word

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(search.router)
api_router.include_router(word.router)

__all__ = ["api_router"]
