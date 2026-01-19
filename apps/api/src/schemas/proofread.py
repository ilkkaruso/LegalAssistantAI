"""Schemas for proofreading/risk highlighting."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ProofreadIssue(BaseModel):
    """A single proofreading/risk issue."""

    quote: str = Field(..., min_length=3, description="Exact snippet from the input text")
    severity: Literal["info", "warning", "risk"]
    message: str = Field(..., min_length=3, description="Explanation / suggested improvement")
    suggestion: Optional[str] = Field(default=None, description="Optional suggested replacement text")


class ProofreadAnalysis(BaseModel):
    """Structured analysis returned by the LLM."""

    issues: List[ProofreadIssue] = Field(default_factory=list)
