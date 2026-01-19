"""Search API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.search import SearchQuery, SearchResponse, SearchResult
from src.services.vector_search_service import VectorSearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=SearchResponse)
async def search_documents(
    search_query: SearchQuery,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> SearchResponse:
    """Search documents using semantic similarity.
    
    Args:
        search_query: The search query parameters
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        Search results with similarity scores
        
    Raises:
        HTTPException: If search fails
    """
    try:
        search_service = VectorSearchService(session)
        results = await search_service.search(
            query=search_query.query,
            user_id=current_user.id,
            limit=search_query.limit,
            similarity_threshold=search_query.similarity_threshold
        )
        
        search_results = [SearchResult(**result) for result in results]
        
        return SearchResponse(
            query=search_query.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/health")
async def search_health() -> dict:
    """Check if search service is available.
    
    Returns:
        Status of the search service
    """
    try:
        from src.services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        
        # Try to get embedding dimension
        dimension = embedding_service.get_embedding_dimension()
        
        return {
            "status": "healthy",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dimension": dimension
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
