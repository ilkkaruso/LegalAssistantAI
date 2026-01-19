"""Document service layer."""
import logging
from typing import Optional, List, BinaryIO
from uuid import UUID
import uuid

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.repositories.document_repository import DocumentRepository
from src.models.document import Document, DocumentStatus, DocumentType
from src.schemas.document import DocumentCreate, DocumentUpdate, DocumentList
from src.services.storage_service import StorageService
from src.utils.file_processor import FileProcessor

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service with database session.
        
        Args:
            session: The async database session
        """
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.storage = StorageService()
        self.file_processor = FileProcessor()
    
    async def upload_document(
        self,
        file: UploadFile,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None
    ) -> Document:
        """Upload a document file.
        
        Args:
            file: The uploaded file
            user_id: The user ID uploading the document
            title: Optional document title
            description: Optional document description
            tags: Optional comma-separated tags
            
        Returns:
            The created document
            
        Raises:
            HTTPException: If upload fails or file type is not allowed
        """
        # Validate file type
        file_type = self.file_processor.get_file_type_from_filename(file.filename)
        
        if file_type not in [ft.value for ft in DocumentType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed types: {', '.join([ft.value for ft in DocumentType])}"
            )
        
        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Generate unique storage path
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        storage_filename = f"{uuid.uuid4()}.{file_extension}"
        storage_path = f"users/{user_id}/documents/{storage_filename}"
        
        try:
            # Upload to MinIO
            from io import BytesIO
            file_data = BytesIO(file_content)
            self.storage.upload_file(
                file_data=file_data,
                object_name=storage_path,
                content_type=file.content_type or "application/octet-stream",
                file_size=file_size
            )
            
            # Create document record
            document_data = DocumentCreate(
                user_id=user_id,
                filename=storage_filename,
                original_filename=file.filename,
                file_type=DocumentType(file_type),
                file_size=file_size,
                mime_type=file.content_type or "application/octet-stream",
                storage_path=storage_path,
                storage_bucket=settings.S3_BUCKET,
                status=DocumentStatus.PROCESSING,
                title=title,
                description=description,
                tags=tags
            )
            
            document = await self.doc_repo.create(document_data)
            
            # Process document asynchronously (extract text)
            await self._process_document(document, file_content)
            
            return document
            
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            # Clean up storage if document creation failed
            try:
                self.storage.delete_file(storage_path)
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload document: {str(e)}"
            )
    
    async def _process_document(self, document: Document, file_content: bytes) -> None:
        """Process document to extract text and generate embeddings (internal method).
        
        Args:
            document: The document to process
            file_content: The file content as bytes
        """
        try:
            # Extract text from document
            extracted_text, page_count, word_count = self.file_processor.process_document(
                file_content,
                document.file_type.value
            )
            
            # Update document with processing results
            await self.doc_repo.update_processing_status(
                document,
                status=DocumentStatus.COMPLETED,
                extracted_text=extracted_text,
                page_count=page_count,
                word_count=word_count
            )
            
            # Generate embeddings for the document if text was extracted
            if extracted_text:
                try:
                    await self._generate_embeddings(document, extracted_text)
                except Exception as embed_error:
                    logger.error(f"Error generating embeddings for document {document.id}: {embed_error}")
                    # Don't fail the whole process if embeddings fail
            
            logger.info(f"Successfully processed document {document.id}")
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {e}")
            await self.doc_repo.update_processing_status(
                document,
                status=DocumentStatus.FAILED
            )
    
    async def _generate_embeddings(self, document: Document, text: str) -> None:
        """Generate embeddings for document chunks (internal method).
        
        Args:
            document: The document
            text: The extracted text
        """
        from src.utils.text_chunker import TextChunker
        from src.services.embedding_service import get_embedding_service
        from src.db.repositories.document_chunk_repository import DocumentChunkRepository
        from src.models.document_chunk import DocumentChunk
        
        try:
            # Chunk the text
            chunker = TextChunker(chunk_size=500, chunk_overlap=50)
            chunks_data = chunker.chunk_text(text)
            
            if not chunks_data:
                logger.info(f"No chunks created for document {document.id}")
                return
            
            logger.info(f"Created {len(chunks_data)} chunks for document {document.id}")
            
            # Generate embeddings
            embedding_service = get_embedding_service()
            chunk_texts = [chunk_text for chunk_text, _, _ in chunks_data]
            embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
            
            # Create chunk records
            chunk_repo = DocumentChunkRepository(self.session)
            chunk_records = []
            
            for idx, ((chunk_text, start_char, end_char), embedding) in enumerate(zip(chunks_data, embeddings)):
                chunk = DocumentChunk(
                    document_id=document.id,
                    user_id=document.user_id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    chunk_size=len(chunk_text),
                    embedding=embedding,
                    start_char=start_char,
                    end_char=end_char
                )
                chunk_records.append(chunk)
            
            # Save chunks to database
            await chunk_repo.create_chunks(chunk_records)
            
            logger.info(f"Successfully generated {len(chunk_records)} embeddings for document {document.id}")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def get_document(self, document_id: UUID, user_id: UUID) -> Document:
        """Get a document by ID.
        
        Args:
            document_id: The document ID
            user_id: The user ID (for authorization)
            
        Returns:
            The document
            
        Raises:
            HTTPException: If document not found or user not authorized
        """
        document = await self.doc_repo.get_by_id(document_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document"
            )
        
        return document
    
    async def list_documents(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> DocumentList:
        """List documents for a user with pagination.
        
        Args:
            user_id: The user ID
            page: Page number (1-indexed)
            page_size: Number of documents per page
            
        Returns:
            Paginated list of documents
        """
        skip = (page - 1) * page_size
        
        documents = await self.doc_repo.get_by_user_id(user_id, skip=skip, limit=page_size)
        total = await self.doc_repo.count_by_user_id(user_id)
        total_pages = (total + page_size - 1) // page_size
        
        return DocumentList(
            documents=documents,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    async def download_document(self, document_id: UUID, user_id: UUID) -> bytes:
        """Download a document file.
        
        Args:
            document_id: The document ID
            user_id: The user ID (for authorization)
            
        Returns:
            The file content as bytes
            
        Raises:
            HTTPException: If document not found or user not authorized
        """
        document = await self.get_document(document_id, user_id)
        
        try:
            file_data = self.storage.download_file(document.storage_path, document.storage_bucket)
            return file_data
        except Exception as e:
            logger.error(f"Error downloading document {document_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download document"
            )
    
    async def get_download_url(self, document_id: UUID, user_id: UUID) -> str:
        """Get a presigned download URL for a document.
        
        Args:
            document_id: The document ID
            user_id: The user ID (for authorization)
            
        Returns:
            The presigned download URL
            
        Raises:
            HTTPException: If document not found or user not authorized
        """
        document = await self.get_document(document_id, user_id)
        
        try:
            url = self.storage.get_file_url(document.storage_path, document.storage_bucket)
            return url
        except Exception as e:
            logger.error(f"Error generating download URL for document {document_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate download URL"
            )
    
    async def update_document(
        self,
        document_id: UUID,
        user_id: UUID,
        document_data: DocumentUpdate
    ) -> Document:
        """Update document metadata.
        
        Args:
            document_id: The document ID
            user_id: The user ID (for authorization)
            document_data: The updated document data
            
        Returns:
            The updated document
            
        Raises:
            HTTPException: If document not found or user not authorized
        """
        document = await self.get_document(document_id, user_id)
        updated_document = await self.doc_repo.update(document, document_data)
        return updated_document
    
    async def delete_document(self, document_id: UUID, user_id: UUID) -> None:
        """Delete a document.
        
        Args:
            document_id: The document ID
            user_id: The user ID (for authorization)
            
        Raises:
            HTTPException: If document not found or user not authorized
        """
        document = await self.get_document(document_id, user_id)
        
        try:
            # Delete from storage
            self.storage.delete_file(document.storage_path, document.storage_bucket)
            
            # Delete from database
            await self.doc_repo.delete(document)
            
            logger.info(f"Deleted document {document_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )
