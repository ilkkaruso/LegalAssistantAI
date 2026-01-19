"""Text chunking utilities for splitting documents into manageable segments."""
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class TextChunker:
    """Utility for chunking text into segments suitable for embedding."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize the text chunker.
        
        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[Tuple[str, int, int]]:
        """Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of tuples (chunk_text, start_char, end_char)
        """
        if not text or len(text) == 0:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at sentence or word boundary if not at the end
            if end < text_length:
                # Look for sentence boundary (., !, ?)
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if sentence_end > start:
                    end = sentence_end + 1  # Include the punctuation
                else:
                    # Look for word boundary (space)
                    space_pos = text.rfind(' ', start, end)
                    if space_pos > start:
                        end = space_pos
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunks.append((chunk_text, start, end))
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap if end < text_length else text_length
        
        return chunks
    
    def chunk_text_by_sentences(self, text: str, max_sentences: int = 5) -> List[Tuple[str, int, int]]:
        """Split text into chunks of N sentences.
        
        Args:
            text: The text to chunk
            max_sentences: Maximum number of sentences per chunk
            
        Returns:
            List of tuples (chunk_text, start_char, end_char)
        """
        if not text:
            return []
        
        # Simple sentence splitting (can be improved with nltk or spacy)
        sentences = []
        current_pos = 0
        
        for delimiter in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
            parts = text.split(delimiter)
            if len(parts) > 1:
                for i, part in enumerate(parts[:-1]):
                    sentence = part + delimiter.rstrip()
                    sentences.append((sentence, current_pos, current_pos + len(sentence)))
                    current_pos += len(sentence)
                
                # Last part
                if parts[-1]:
                    sentences.append((parts[-1], current_pos, current_pos + len(parts[-1])))
        
        if not sentences and text:
            # No sentence delimiters found, treat as single sentence
            sentences = [(text, 0, len(text))]
        
        # Group sentences into chunks
        chunks = []
        i = 0
        while i < len(sentences):
            chunk_sentences = sentences[i:i + max_sentences]
            
            if chunk_sentences:
                chunk_text = ' '.join(s[0] for s in chunk_sentences)
                start_char = chunk_sentences[0][1]
                end_char = chunk_sentences[-1][2]
                
                chunks.append((chunk_text, start_char, end_char))
            
            i += max_sentences
        
        return chunks
    
    def chunk_text_by_paragraphs(self, text: str) -> List[Tuple[str, int, int]]:
        """Split text into chunks by paragraphs.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of tuples (chunk_text, start_char, end_char)
        """
        if not text:
            return []
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_pos = 0
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # If paragraph is too long, split it further
                if len(para) > self.chunk_size:
                    sub_chunks = self.chunk_text(para)
                    for sub_chunk, _, _ in sub_chunks:
                        chunks.append((sub_chunk, current_pos, current_pos + len(sub_chunk)))
                        current_pos += len(sub_chunk)
                else:
                    chunks.append((para, current_pos, current_pos + len(para)))
                    current_pos += len(para)
            
            current_pos += 2  # Account for \n\n
        
        return chunks
