"""Document repository for database operations."""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import Document, DocumentStatus
from src.schemas.document import DocumentCreate, DocumentUpdate


class DocumentRepository:
    """Repository for document database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: The async database session
        """
        self.session = session
    
    async def create(self, document_data: DocumentCreate) -> Document:
        """Create a new document.
        
        Args:
            document_data: The document data to create
            
        Returns:
            The created document
        """
        document = Document(**document_data.model_dump())
        
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        
        return document
    
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            The document if found, None otherwise
        """
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get documents by user ID with pagination.
        
        Args:
            user_id: The user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of documents
        """
        result = await self.session.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_user_id(self, user_id: UUID) -> int:
        """Count documents for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            The count of documents
        """
        result = await self.session.execute(
            select(func.count(Document.id)).where(Document.user_id == user_id)
        )
        return result.scalar_one()
    
    async def update(self, document: Document, document_data: DocumentUpdate) -> Document:
        """Update a document.
        
        Args:
            document: The document to update
            document_data: The updated document data
            
        Returns:
            The updated document
        """
        update_data = document_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(document, field, value)
        
        await self.session.commit()
        await self.session.refresh(document)
        
        return document
    
    async def update_processing_status(
        self,
        document: Document,
        status: DocumentStatus,
        extracted_text: Optional[str] = None,
        page_count: Optional[int] = None,
        word_count: Optional[int] = None
    ) -> Document:
        """Update document processing status and metadata.
        
        Args:
            document: The document to update
            status: The new status
            extracted_text: Optional extracted text
            page_count: Optional page count
            word_count: Optional word count
            
        Returns:
            The updated document
        """
        from datetime import datetime
        
        document.status = status
        
        if extracted_text is not None:
            document.extracted_text = extracted_text
        if page_count is not None:
            document.page_count = page_count
        if word_count is not None:
            document.word_count = word_count
        
        if status == DocumentStatus.COMPLETED:
            document.processed_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(document)
        
        return document
    
    async def delete(self, document: Document) -> None:
        """Delete a document.
        
        Args:
            document: The document to delete
        """
        await self.session.delete(document)
        await self.session.commit()
