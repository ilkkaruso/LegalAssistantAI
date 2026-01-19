"""Search schemas for request/response validation."""
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Search query request."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0-1)"
    )


class SearchResult(BaseModel):
    """Single search result."""
    document_id: str
    document_title: str
    document_filename: str
    document_type: str
    chunk_id: str
    chunk_text: str
    chunk_index: int
    similarity_score: float
    start_char: int | None = None
    end_char: int | None = None


class SearchResponse(BaseModel):
    """Search response with results."""
    query: str
    results: List[SearchResult]
    total_results: int
