"""Import all models here for Alembic to detect."""

from src.db.session import Base

# Import all models here so Alembic can detect them
# from src.models.user import User, Firm
# from src.models.document import Document, DocumentChunk
# from src.models.conversation import Conversation, Message, MessageCitation

__all__ = ["Base"]
