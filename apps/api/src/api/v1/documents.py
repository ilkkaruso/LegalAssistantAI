"""Document API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.document import (
    DocumentResponse,
    DocumentList,
    DocumentUpdate,
    DocumentUploadResponse,
    DocumentWithUrl
)
from src.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> DocumentUploadResponse:
    """Upload a new document.
    
    Args:
        file: The file to upload
        title: Optional document title
        description: Optional document description
        tags: Optional comma-separated tags
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        The created document with upload confirmation
        
    Raises:
        HTTPException: If upload fails or file type is not supported
    """
    document_service = DocumentService(session)
    document = await document_service.upload_document(
        file=file,
        user_id=current_user.id,
        title=title,
        description=description,
        tags=tags
    )
    
    return DocumentUploadResponse(
        document=DocumentResponse.model_validate(document),
        message="Document uploaded and processing started"
    )


@router.get("/", response_model=DocumentList)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> DocumentList:
    """List all documents for the current user.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of documents per page
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        Paginated list of documents
    """
    document_service = DocumentService(session)
    documents = await document_service.list_documents(
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Get a specific document by ID.
    
    Args:
        document_id: The document ID
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        The document details
        
    Raises:
        HTTPException: If document not found or user not authorized
    """
    document_service = DocumentService(session)
    document = await document_service.get_document(document_id, current_user.id)
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/url", response_model=DocumentWithUrl)
async def get_document_with_url(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> DocumentWithUrl:
    """Get a document with a presigned download URL.
    
    Args:
        document_id: The document ID
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        The document details with download URL
        
    Raises:
        HTTPException: If document not found or user not authorized
    """
    document_service = DocumentService(session)
    document = await document_service.get_document(document_id, current_user.id)
    download_url = await document_service.get_download_url(document_id, current_user.id)
    
    document_dict = DocumentResponse.model_validate(document).model_dump()
    return DocumentWithUrl(**document_dict, download_url=download_url)


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """Download a document file.
    
    Args:
        document_id: The document ID
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        The file content as streaming response
        
    Raises:
        HTTPException: If document not found or user not authorized
    """
    document_service = DocumentService(session)
    document = await document_service.get_document(document_id, current_user.id)
    file_data = await document_service.download_document(document_id, current_user.id)
    
    from io import BytesIO
    
    return StreamingResponse(
        BytesIO(file_data),
        media_type=document.mime_type,
        headers={
            "Content-Disposition": f"attachment; filename={document.original_filename}"
        }
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Update document metadata.
    
    Args:
        document_id: The document ID
        document_data: The updated document data
        current_user: The current authenticated user
        session: The database session
        
    Returns:
        The updated document
        
    Raises:
        HTTPException: If document not found or user not authorized
    """
    document_service = DocumentService(session)
    document = await document_service.update_document(document_id, current_user.id, document_data)
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> None:
    """Delete a document.
    
    Args:
        document_id: The document ID
        current_user: The current authenticated user
        session: The database session
        
    Raises:
        HTTPException: If document not found or user not authorized
    """
    document_service = DocumentService(session)
    await document_service.delete_document(document_id, current_user.id)
