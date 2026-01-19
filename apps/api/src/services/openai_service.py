"""OpenAI service wrapper."""
import logging
from typing import Optional

from pydantic import ValidationError

from src.schemas.proofread import ProofreadAnalysis

from openai import OpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Minimal OpenAI client wrapper for server-side calls."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE

    def improve_writing(self, text: str, instructions: Optional[str] = None) -> str:
        """Rewrite text for clarity while preserving meaning.

        Returns rewritten text only.
        """
        system = (
            "You are a senior legal editor. Rewrite the user's text to improve clarity, "
            "precision, and professionalism while preserving meaning. Do not add new facts. "
            "Return ONLY the rewritten text, no quotes, no markdown."
        )

        user = "Rewrite the following text:\n\n" + text
        if instructions:
            user += f"\n\nAdditional instructions: {instructions}"

        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        return (resp.choices[0].message.content or "").strip()

    def draft_clause(
        self,
        clause_request: str,
        context_text: Optional[str] = None,
        style_instructions: Optional[str] = None,
    ) -> str:
        """Draft a legal clause.

        Returns clause text only (no markdown, no quotes).
        """
        system = (
            "You are an expert transactional lawyer. Draft a clause suitable for insertion into a contract. "
            "Use clear legal drafting, preserve defined terms from context if present, and do not invent facts. "
            "Return ONLY the clause text, no markdown, no headings unless they are part of the clause label."
        )

        user_parts = [f"Clause to draft: {clause_request}"]
        if style_instructions:
            user_parts.append(f"Style instructions: {style_instructions}")
        if context_text:
            user_parts.append("Context (may include defined terms and surrounding language):\n" + context_text)

        user = "\n\n".join(user_parts)

        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        return (resp.choices[0].message.content or "").strip()

    def proofread_and_highlight(self, text: str) -> ProofreadAnalysis:
        """Analyze text for issues and risks.

        Returns a structured list of issues with exact quotes from the input.
        """
        system = (
            "You are a senior legal reviewer. Identify issues in the provided contract text. "
            "Focus on: ambiguous language, missing definitions, inconsistent terms, risky obligations, "
            "and basic grammar/clarity. Return a JSON object with an array 'issues'. "
            "Each issue must include: quote (exact substring from input), severity (info|warning|risk), "
            "message (explain), and optional suggestion (replacement text). "
            "Return ONLY valid JSON."
        )

        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
        )

        content = (resp.choices[0].message.content or "").strip()
        try:
            return ProofreadAnalysis.model_validate_json(content)
        except ValidationError as e:
            raise ValueError(f"Invalid proofread JSON: {e}")


_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
