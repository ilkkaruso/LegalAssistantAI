"""Schemas for Word add-in operations."""
from typing import Literal, Optional, List

from pydantic import BaseModel, Field


class WordComment(BaseModel):
    """A comment to add in Word."""

    title: Optional[str] = None
    body: str


class WordOperation(BaseModel):
    """A structured operation the add-in should apply.

    NOTE: For v1, operations are relative to the current selection.
    """

    type: Literal[
        "replace_selection",
        "insert_after_selection",
        "insert_before_selection",
        "comment_on_quote",
    ]

    # For insert/replace ops
    new_text: Optional[str] = Field(default=None, description="Text to insert/replace")

    # For proofread/risk ops
    quote: Optional[str] = Field(default=None, description="Exact snippet to find within the selection")
    severity: Optional[Literal["info", "warning", "risk"]] = None
    highlight: bool = False

    comment: Optional[WordComment] = None


class ImproveWritingRequest(BaseModel):
    """Request payload for Improve Writing."""

    selection_text: str = Field(..., min_length=1, description="The currently selected text in Word")
    instructions: Optional[str] = Field(
        default=None,
        description="Optional user instructions (e.g., 'make it more formal')",
    )


class ImproveWritingResponse(BaseModel):
    """Response payload for Improve Writing."""

    operations: List[WordOperation]
    model: str


class DraftClauseRequest(BaseModel):
    """Request payload for Draft Clause."""

    clause_request: str = Field(
        ..., min_length=3, max_length=2000, description="What clause to draft (e.g., 'termination for convenience')"
    )
    context_text: Optional[str] = Field(
        default=None,
        description="Optional context from the document/selection to align tone and defined terms",
    )
    style_instructions: Optional[str] = Field(
        default=None,
        description="Optional style instructions (e.g., 'UK English, formal, short')",
    )


class DraftClauseResponse(BaseModel):
    """Response payload for Draft Clause."""

    operations: List[WordOperation]
    model: str


class ProofreadRequest(BaseModel):
    """Request payload for Proofread + Risk Highlight."""

    selection_text: str = Field(..., min_length=1, description="Text to analyze (typically the selection)")


class ProofreadResponse(BaseModel):
    """Response payload for Proofread + Risk Highlight."""

    operations: List[WordOperation]
    model: str
