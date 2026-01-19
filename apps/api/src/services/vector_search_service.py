"""Vector search service for semantic document search."""
import logging
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.document_chunk_repository import DocumentChunkRepository
from src.db.repositories.document_repository import DocumentRepository
from src.services.embedding_service import get_embedding_service
from src.models.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)


class VectorSearchService:
    """Service for vector-based semantic search."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service with database session.
        
        Args:
            session: The async database session
        """
        self.session = session
        self.chunk_repo = DocumentChunkRepository(session)
        self.doc_repo = DocumentRepository(session)
        self.embedding_service = get_embedding_service()
    
    async def search(
        self,
        query: str,
        user_id: UUID,
        limit: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for documents using semantic similarity.
        
        Args:
            query: The search query
            user_id: The user ID to filter results
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of search results with document and chunk information
        """
        try:
            # Generate query embedding
            logger.info(f"Generating embedding for query: {query[:50]}...")
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Search for similar chunks
            logger.info(f"Searching for similar chunks (limit={limit}, threshold={similarity_threshold})")
            chunks_with_scores = await self.chunk_repo.search_similar(
                query_embedding=query_embedding,
                user_id=user_id,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            # Group results by document and prepare response
            results = []
            seen_documents = set()
            
            for chunk, similarity in chunks_with_scores:
                # Get document details if not already fetched
                if chunk.document_id not in seen_documents:
                    document = await self.doc_repo.get_by_id(chunk.document_id)
                    
                    if document:
                        results.append({
                            "document_id": str(document.id),
                            "document_title": document.title or document.original_filename,
                            "document_filename": document.original_filename,
                            "document_type": document.file_type.value,
                            "chunk_id": str(chunk.id),
                            "chunk_text": chunk.chunk_text,
                            "chunk_index": chunk.chunk_index,
                            "similarity_score": round(similarity, 4),
                            "start_char": chunk.start_char,
                            "end_char": chunk.end_char
                        })
                        
                        seen_documents.add(chunk.document_id)
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            raise
    
    async def get_document_chunks_count(self, document_id: UUID) -> int:
        """Get the number of chunks for a document.
        
        Args:
            document_id: The document ID
            
        Returns:
            The number of chunks
        """
        chunks = await self.chunk_repo.get_by_document_id(document_id)
        return len(chunks)
