"""Document model for file management."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from src.db.base import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    """Document type classification."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    OTHER = "other"


class Document(Base):
    """Document model for file storage and management."""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(DocumentType), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    
    # Storage information
    storage_path = Column(String(500), nullable=False)  # MinIO object key
    storage_bucket = Column(String(100), nullable=False, default="documents")
    
    # Processing information
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.UPLOADING)
    extracted_text = Column(Text, nullable=True)  # Extracted text content
    page_count = Column(Integer, nullable=True)  # For PDFs
    word_count = Column(Integer, nullable=True)
    
    # Metadata
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationship
    # user = relationship("User", back_populates="documents")
    
    def __repr__(self) -> str:
        return f"<Document {self.filename} ({self.status})>"
