"""Document schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.models.document import DocumentStatus, DocumentType


# Document response schemas
class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    original_filename: str
    file_type: DocumentType
    file_size: int
    mime_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Document creation schema (internal use)."""
    user_id: UUID
    storage_path: str
    storage_bucket: str = "documents"
    status: DocumentStatus = DocumentStatus.UPLOADING


class DocumentUpdate(BaseModel):
    """Document update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[DocumentStatus] = None


class DocumentResponse(DocumentBase):
    """Document response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    storage_path: str
    storage_bucket: str
    status: DocumentStatus
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None


class DocumentWithUrl(DocumentResponse):
    """Document response with download URL."""
    download_url: str


class DocumentList(BaseModel):
    """Paginated list of documents."""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    document: DocumentResponse
    message: str = "Document uploaded successfully"


# File upload schemas
class FileUploadMetadata(BaseModel):
    """Metadata for file upload."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


# Document processing schemas
class DocumentProcessingResult(BaseModel):
    """Result of document processing."""
    document_id: UUID
    status: DocumentStatus
    extracted_text: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    error_message: Optional[str] = None
