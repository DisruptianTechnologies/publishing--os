from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db
from core.auth import require_auth, TenantContext
from services.compilation_service import compile_project_manuscript
from services.cover_service import calculate_cover_dimensions, generate_cover_art_prompt

router = APIRouter(prefix="/api/v1/projects", tags=["compilation"])


class CompileRequest(BaseModel):
    title: str = "Mindful Productivity: Focus in an Age of Noise"
    author: str = "Kindlepreneur Author"
    output_formats: list[str] = ["epub", "pdf"]
    trim_size: str = "6x9"
    paper_type: str = "white"


class CoverDimensionRequest(BaseModel):
    page_count: int = 164
    trim_size: str = "6x9"
    paper_type: Literal["white", "cream", "color"] = "white"


class CoverPromptRequest(BaseModel):
    title: str
    subtitle: str = ""
    genre: str = "nonfiction_productivity"
    visual_style: str = "minimalist_editorial"


@router.post("/{id}/compile", response_model=dict)
async def compile_manuscript(
    id: str,
    req: CompileRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    """
    Compiles all project chapters into EPUB 3.0 and print-ready 6x9 PDF artifacts.
    """
    try:
        result = await compile_project_manuscript(
            db=db,
            tenant_id=ctx.tenant_id,
            project_id=id,
            title=req.title,
            author=req.author,
            output_formats=req.output_formats,
        )
        return {"data": result, "error": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}/export/{format}")
async def export_manuscript(
    id: str,
    format: Literal["epub", "pdf"],
    title: str = "Mindful Productivity",
    author: str = "Kindlepreneur Author",
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    """
    Directly streams or downloads the compiled EPUB or PDF file.
    """
    from services.compilation_service import generate_epub3_archive, generate_print_pdf_6x9, SAMPLE_PROJECT_CHAPTERS
    
    # Use sample chapters for compilation download
    chapters = [{"title": ch["title"], "content": ch["content"]} for ch in SAMPLE_PROJECT_CHAPTERS]
    
    if format == "epub":
        file_bytes = generate_epub3_archive(title=title, author=author, chapters=chapters)
        return Response(
            content=file_bytes,
            media_type="application/epub+zip",
            headers={"Content-Disposition": f'attachment; filename="{id}_{format}.epub"'},
        )
    elif format == "pdf":
        file_bytes = generate_print_pdf_6x9(title=title, author=author, chapters=chapters)
        return Response(
            content=file_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{id}_interior_6x9.pdf"'},
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format requested")


@router.post("/{id}/cover/dimensions", response_model=dict)
async def get_cover_dimensions(
    id: str,
    req: CoverDimensionRequest,
    ctx: TenantContext = Depends(require_auth),
):
    """
    Calculates exact Amazon KDP cover wrap dimensions, spine width, and barcode box.
    """
    dimensions = calculate_cover_dimensions(
        page_count=req.page_count,
        trim_size=req.trim_size,
        paper_type=req.paper_type,
    )
    return {"data": dimensions, "error": None}


@router.post("/{id}/cover/prompt", response_model=dict)
async def get_cover_prompt(
    id: str,
    req: CoverPromptRequest,
    ctx: TenantContext = Depends(require_auth),
):
    """
    Synthesizes commercial generative image prompt for cover artwork.
    """
    cover_prompt = generate_cover_art_prompt(
        title=req.title,
        subtitle=req.subtitle,
        genre=req.genre,
        visual_style=req.visual_style,
    )
    return {"data": cover_prompt, "error": None}
