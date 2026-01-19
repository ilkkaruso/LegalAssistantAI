"""File processing utilities for text extraction."""
import logging
from typing import Optional, Tuple
from io import BytesIO

from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


class FileProcessor:
    """Utility class for processing different file types."""
    
    @staticmethod
    def extract_text_from_pdf(file_data: bytes) -> Tuple[str, int]:
        """Extract text from PDF file.
        
        Args:
            file_data: The PDF file data as bytes
            
        Returns:
            Tuple of (extracted_text, page_count)
            
        Raises:
            Exception: If PDF processing fails
        """
        try:
            pdf_file = BytesIO(file_data)
            reader = PdfReader(pdf_file)
            
            page_count = len(reader.pages)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            extracted_text = "\n\n".join(text_parts)
            
            logger.info(f"Extracted text from PDF: {page_count} pages, {len(extracted_text)} characters")
            return extracted_text, page_count
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_data: bytes) -> str:
        """Extract text from DOCX file.
        
        Args:
            file_data: The DOCX file data as bytes
            
        Returns:
            The extracted text
            
        Raises:
            Exception: If DOCX processing fails
        """
        try:
            docx_file = BytesIO(file_data)
            doc = DocxDocument(docx_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            extracted_text = "\n\n".join(text_parts)
            
            logger.info(f"Extracted text from DOCX: {len(extracted_text)} characters")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    @staticmethod
    def extract_text_from_txt(file_data: bytes) -> str:
        """Extract text from TXT file.
        
        Args:
            file_data: The TXT file data as bytes
            
        Returns:
            The extracted text
            
        Raises:
            Exception: If TXT processing fails
        """
        try:
            # Try UTF-8 first, fallback to latin-1
            try:
                text = file_data.decode('utf-8')
            except UnicodeDecodeError:
                text = file_data.decode('latin-1')
            
            logger.info(f"Extracted text from TXT: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise
    
    @staticmethod
    def process_document(file_data: bytes, file_type: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        """Process a document and extract text.
        
        Args:
            file_data: The file data as bytes
            file_type: The file type (pdf, docx, doc, txt)
            
        Returns:
            Tuple of (extracted_text, page_count, word_count)
        """
        extracted_text = None
        page_count = None
        word_count = None
        
        try:
            if file_type == "pdf":
                extracted_text, page_count = FileProcessor.extract_text_from_pdf(file_data)
            elif file_type in ["docx", "doc"]:
                extracted_text = FileProcessor.extract_text_from_docx(file_data)
            elif file_type == "txt":
                extracted_text = FileProcessor.extract_text_from_txt(file_data)
            else:
                logger.warning(f"Unsupported file type for text extraction: {file_type}")
                return None, None, None
            
            # Calculate word count
            if extracted_text:
                word_count = len(extracted_text.split())
            
            return extracted_text, page_count, word_count
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return None, None, None
    
    @staticmethod
    def get_file_type_from_filename(filename: str) -> str:
        """Get file type from filename extension.
        
        Args:
            filename: The filename
            
        Returns:
            The file type (pdf, docx, doc, txt, other)
        """
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if extension == 'pdf':
            return 'pdf'
        elif extension == 'docx':
            return 'docx'
        elif extension == 'doc':
            return 'doc'
        elif extension == 'txt':
            return 'txt'
        else:
            return 'other'
