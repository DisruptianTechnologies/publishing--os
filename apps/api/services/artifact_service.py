import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from models.artifact import Artifact, ArtifactVersion
from core.storage import get_storage

async def create_artifact(db: AsyncSession, tenant_id: str, project_id: str, artifact_type: str, name: str, description: str = '') -> Artifact:
    artifact = Artifact(
        tenant_id=tenant_id,
        project_id=project_id,
        artifact_type=artifact_type,
        name=name,
        description=description
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    return artifact

async def add_version(db: AsyncSession, artifact_id: str, tenant_id: str, project_id: str, content: bytes | str, structured_data: dict, agent_info: dict) -> ArtifactVersion:
    artifact = await db.get(Artifact, artifact_id)
    if not artifact or artifact.tenant_id != tenant_id:
        raise ValueError("Artifact not found")

    content_bytes = content if isinstance(content, bytes) else content.encode('utf-8')
    checksum = hashlib.sha256(content_bytes).hexdigest()
    
    storage = get_storage()
    key = f"tenant_{tenant_id}/project_{project_id}/artifact_{artifact_id}/v{artifact.current_version + 1}_{checksum[:8]}"
    await storage.save(key, content_bytes)
    
    artifact.current_version += 1
    
    version = ArtifactVersion(
        artifact_id=artifact_id,
        tenant_id=tenant_id,
        project_id=project_id,
        version=artifact.current_version,
        content_location=key,
        size_bytes=len(content_bytes),
        checksum=checksum,
        structured_data=structured_data,
        **agent_info
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return version

async def get_current_version(db: AsyncSession, artifact_id: str, tenant_id: str) -> ArtifactVersion | None:
    result = await db.execute(
        select(ArtifactVersion)
        .where(ArtifactVersion.artifact_id == artifact_id, ArtifactVersion.tenant_id == tenant_id)
        .order_by(desc(ArtifactVersion.version))
        .limit(1)
    )
    return result.scalars().first()

async def get_download_url(db: AsyncSession, artifact_id: str, version: int = None, tenant_id: str = None) -> str:
    query = select(ArtifactVersion).where(ArtifactVersion.artifact_id == artifact_id, ArtifactVersion.tenant_id == tenant_id)
    if version is not None:
        query = query.where(ArtifactVersion.version == version)
    else:
        query = query.order_by(desc(ArtifactVersion.version)).limit(1)
        
    result = await db.execute(query)
    v = result.scalars().first()
    if not v:
        raise ValueError("Version not found")
        
    storage = get_storage()
    return await storage.get_signed_url(v.content_location)
