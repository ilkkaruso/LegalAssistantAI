"""DocumentChunk model for vector embeddings."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

from src.db.base import Base


class DocumentChunk(Base):
    """Document chunk model for storing text segments with embeddings."""
    
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chunk information
    chunk_index = Column(Integer, nullable=False)  # Position in document (0-indexed)
    chunk_text = Column(Text, nullable=False)  # The actual text content
    chunk_size = Column(Integer, nullable=False)  # Length in characters
    
    # Vector embedding (384 dimensions for sentence-transformers/all-MiniLM-L6-v2)
    # Can be adjusted based on the embedding model used
    embedding = Column(Vector(384), nullable=True)
    
    # Metadata
    start_char = Column(Integer, nullable=True)  # Starting character position in original document
    end_char = Column(Integer, nullable=True)  # Ending character position in original document
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<DocumentChunk {self.id} (doc={self.document_id}, idx={self.chunk_index})>"
