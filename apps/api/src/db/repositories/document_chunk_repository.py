"""Document chunk repository for database operations."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    """Repository for document chunk database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: The async database session
        """
        self.session = session
    
    async def create_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Create multiple document chunks.
        
        Args:
            chunks: List of document chunks to create
            
        Returns:
            The created chunks
        """
        self.session.add_all(chunks)
        await self.session.commit()
        
        for chunk in chunks:
            await self.session.refresh(chunk)
        
        return chunks
    
    async def get_by_document_id(self, document_id: UUID) -> List[DocumentChunk]:
        """Get all chunks for a document.
        
        Args:
            document_id: The document ID
            
        Returns:
            List of document chunks
        """
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())
    
    async def delete_by_document_id(self, document_id: UUID) -> None:
        """Delete all chunks for a document.
        
        Args:
            document_id: The document ID
        """
        result = await self.session.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        chunks = result.scalars().all()
        
        for chunk in chunks:
            await self.session.delete(chunk)
        
        await self.session.commit()
    
    async def search_similar(
        self,
        query_embedding: List[float],
        user_id: UUID,
        limit: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[tuple[DocumentChunk, float]]:
        """Search for similar chunks using vector similarity.
        
        Args:
            query_embedding: The query embedding vector
            user_id: The user ID to filter results
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of tuples (chunk, similarity_score)
        """
        # Convert embedding to string format for pgvector
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        # Use pgvector's cosine similarity operator (<=>)
        # Lower distance = more similar, so we use 1 - distance to get similarity
        query = text("""
            SELECT 
                id,
                document_id,
                user_id,
                chunk_index,
                chunk_text,
                chunk_size,
                start_char,
                end_char,
                created_at,
                updated_at,
                1 - (embedding <=> :embedding::vector) as similarity
            FROM document_chunks
            WHERE user_id = :user_id
                AND embedding IS NOT NULL
                AND 1 - (embedding <=> :embedding::vector) >= :threshold
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)
        
        result = await self.session.execute(
            query,
            {
                "embedding": embedding_str,
                "user_id": str(user_id),
                "threshold": similarity_threshold,
                "limit": limit
            }
        )
        
        rows = result.fetchall()
        
        # Convert rows to DocumentChunk objects with similarity scores
        chunks_with_scores = []
        for row in rows:
            chunk = DocumentChunk(
                id=row[0],
                document_id=row[1],
                user_id=row[2],
                chunk_index=row[3],
                chunk_text=row[4],
                chunk_size=row[5],
                start_char=row[6],
                end_char=row[7],
                created_at=row[8],
                updated_at=row[9]
            )
            similarity = float(row[10])
            chunks_with_scores.append((chunk, similarity))
        
        return chunks_with_scores
