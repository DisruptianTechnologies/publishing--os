from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from core.auth import require_auth, TenantContext
from services.chapter_service import SAMPLE_PROJECT_CHAPTERS, assist_chapter_draft

router = APIRouter(prefix="/api/v1/projects", tags=["writing"])


class AssistRequest(BaseModel):
    action: Literal["polish_active_voice", "expand_case_study", "run_editorial_qa"]
    text: str


@router.get("/{id}/chapters", response_model=dict)
async def list_chapters(
    id: str,
    ctx: TenantContext = Depends(require_auth),
):
    """
    Returns drafted chapters with word counts, flesch scores, and completion state.
    """
    return {"data": SAMPLE_PROJECT_CHAPTERS, "error": None}


@router.post("/{id}/chapters/{num}/assist", response_model=dict)
async def assist_chapter(
    id: str,
    num: int,
    req: AssistRequest,
    ctx: TenantContext = Depends(require_auth),
):
    """
    Triggers real-time AI writing assistant: polish voice, expand case study, or run dev edit critique.
    """
    result = assist_chapter_draft(action=req.action, text=req.text)
    return {"data": result, "error": None}
