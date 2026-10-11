from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_async_db
from core.auth import require_auth, TenantContext
from models.artifact import Artifact, ArtifactVersion
from schemas.artifact import ArtifactResponse, ArtifactVersionResponse
from services.artifact_service import get_download_url, create_artifact, add_version

router = APIRouter(prefix="/api/v1/artifacts", tags=["artifacts"])

@router.get("/{id}", response_model=dict)
async def get_artifact(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    result = await db.execute(select(Artifact).where(Artifact.id == id, Artifact.tenant_id == ctx.tenant_id))
    artifact = result.scalars().first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    return {"data": ArtifactResponse.model_validate(artifact).model_dump(), "error": None}

@router.get("/{id}/versions", response_model=dict)
async def list_versions(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    result = await db.execute(select(ArtifactVersion).where(ArtifactVersion.artifact_id == id, ArtifactVersion.tenant_id == ctx.tenant_id))
    versions = result.scalars().all()
    return {"data": [ArtifactVersionResponse.model_validate(v).model_dump() for v in versions], "error": None}

@router.get("/{id}/download")
async def download_artifact(
    id: str,
    version: int = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        url = await get_download_url(db, id, version, ctx.tenant_id)
        return RedirectResponse(url)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=dict)
async def create_new_artifact(
    project_id: str,
    artifact_type: str,
    name: str,
    description: str = "",
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    artifact = await create_artifact(db, ctx.tenant_id, project_id, artifact_type, name, description)
    return {"data": ArtifactResponse.model_validate(artifact).model_dump(), "error": None}

@router.post("/{id}/versions", response_model=dict)
async def create_artifact_version(
    id: str,
    content: str,
    project_id: str,
    structured_data: dict = {},
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    agent_info = {"creator_agent": "user", "creator_user_id": ctx.user_id}
    version = await add_version(db, id, ctx.tenant_id, project_id, content, structured_data, agent_info)
    return {"data": ArtifactVersionResponse.model_validate(version).model_dump(), "error": None}
