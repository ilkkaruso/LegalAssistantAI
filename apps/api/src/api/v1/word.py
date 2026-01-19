"""Word add-in API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.word import (
    ImproveWritingRequest,
    ImproveWritingResponse,
    DraftClauseRequest,
    DraftClauseResponse,
    ProofreadRequest,
    ProofreadResponse,
    WordOperation,
    WordComment,
)
from src.services.openai_service import get_openai_service

router = APIRouter(prefix="/word", tags=["Word"])


@router.post("/improve-writing", response_model=ImproveWritingResponse)
async def improve_writing(
    payload: ImproveWritingRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ImproveWritingResponse:
    """Improve writing for the current selection.

    Returns structured operations for the add-in to apply (replace selection with tracked change).
    """
    _ = session  # reserved for future logging/audit

    text = payload.selection_text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No selection text provided")

    try:
        try:
            svc = get_openai_service()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e),
            )
        rewritten = svc.improve_writing(text=text, instructions=payload.instructions)

        if not rewritten:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM returned empty response",
            )

        op = WordOperation(
            type="replace_selection",
            new_text=rewritten,
            comment=WordComment(
                title="Improve writing",
                body="Rewrote for clarity and legal style while preserving meaning.",
            ),
        )

        return ImproveWritingResponse(operations=[op], model=svc.model)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Improve writing failed: {str(e)}",
        )


@router.post("/draft-clause", response_model=DraftClauseResponse)
async def draft_clause(
    payload: DraftClauseRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> DraftClauseResponse:
    """Draft a clause and return an insert operation for Word.

    The add-in should insert the generated clause after the current selection.
    """
    _ = current_user
    _ = session  # reserved for future audit

    clause_request = payload.clause_request.strip()
    if not clause_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Clause request is required")

    try:
        try:
            svc = get_openai_service()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e),
            )

        clause_text = svc.draft_clause(
            clause_request=clause_request,
            context_text=payload.context_text,
            style_instructions=payload.style_instructions,
        )

        if not clause_text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM returned empty response",
            )

        op = WordOperation(
            type="insert_after_selection",
            new_text="\n" + clause_text.strip() + "\n",
            comment=WordComment(
                title="Draft clause",
                body=f"Drafted clause for request: {clause_request}",
            ),
        )

        return DraftClauseResponse(operations=[op], model=svc.model)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Draft clause failed: {str(e)}",
        )


@router.post("/proofread", response_model=ProofreadResponse)
async def proofread(
    payload: ProofreadRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ProofreadResponse:
    """Proofread and highlight risks in the selection.

    Returns comment_on_quote operations for the add-in to apply.
    """
    _ = current_user
    _ = session

    text = payload.selection_text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No selection text provided")

    try:
        try:
            svc = get_openai_service()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e),
            )

        analysis = svc.proofread_and_highlight(text)

        operations: list[WordOperation] = []
        for issue in analysis.issues[:25]:
            highlight = issue.severity in ["warning", "risk"]
            operations.append(
                WordOperation(
                    type="comment_on_quote",
                    quote=issue.quote,
                    severity=issue.severity,
                    highlight=highlight,
                    comment=WordComment(
                        title=f"{issue.severity.upper()}"
                        if issue.severity else "Issue",
                        body=issue.message + (f"\nSuggestion: {issue.suggestion}" if issue.suggestion else ""),
                    ),
                )
            )

        return ProofreadResponse(operations=operations, model=svc.model)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Proofread failed: {str(e)}",
        )
