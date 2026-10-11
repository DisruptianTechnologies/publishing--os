from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_async_db
from core.auth import require_auth, TenantContext
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, WorkflowStartRequest
from services.workflow_service import start_workflow
from services.audit_service import log_action

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

@router.get("/", response_model=dict)
async def list_projects(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    query = select(Project).where(Project.tenant_id == ctx.tenant_id, Project.is_archived == False)
    if status:
        query = query.where(Project.status == status)
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return {"data": [ProjectResponse.model_validate(p).model_dump() for p in projects], "error": None}

@router.post("/", response_model=dict)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    project = Project(
        tenant_id=ctx.tenant_id,
        name=data.name,
        description=data.description,
        project_type=data.project_type,
        target_market=data.target_market,
        idea_description=data.idea_description,
        settings=data.settings,
        created_by=ctx.user_id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    await log_action(db, ctx.tenant_id, "user", ctx.user_id, "create", "project", str(project.id))
    
    return {"data": ProjectResponse.model_validate(project).model_dump(), "error": None}

@router.get("/{id}", response_model=dict)
async def get_project(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {"data": ProjectResponse.model_validate(project).model_dump(), "error": None}

@router.patch("/{id}", response_model=dict)
async def update_project(
    id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    await db.commit()
    await db.refresh(project)
    return {"data": ProjectResponse.model_validate(project).model_dump(), "error": None}

@router.delete("/{id}", response_model=dict)
async def delete_project(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project.is_archived = True
    await db.commit()
    return {"data": {"success": True}, "error": None}

@router.post("/{id}/workflows", response_model=dict)
async def create_workflow(
    id: str,
    data: WorkflowStartRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    workflow = await start_workflow(db, ctx.tenant_id, id, data.workflow_type, data.config, ctx.user_id)
    return {"data": {"workflow_run_id": str(workflow.id)}, "error": None}

@router.get("/{id}/workflows", response_model=dict)
async def list_workflows(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    from models.agent import WorkflowRun
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.project_id == id, WorkflowRun.tenant_id == ctx.tenant_id))
    return {"data": [{"id": w.id, "status": w.status, "type": w.workflow_type} for w in result.scalars().all()], "error": None}

@router.get("/{id}/artifacts", response_model=dict)
async def list_artifacts(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    from models.artifact import Artifact
    result = await db.execute(select(Artifact).where(Artifact.project_id == id, Artifact.tenant_id == ctx.tenant_id))
    return {"data": [{"id": a.id, "name": a.name, "type": a.artifact_type} for a in result.scalars().all()], "error": None}

@router.get('/{id}/stats', response_model=dict)
async def project_stats(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    """Return aggregated cost, token, and task stats for a project."""
    from sqlalchemy import func
    from models.agent import AgentTask, WorkflowRun

    # Verify project belongs to tenant
    result = await db.execute(
        select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')

    # Task stats
    task_result = await db.execute(
        select(
            func.count(AgentTask.id).label('total_tasks'),
            func.sum(AgentTask.token_usage).label('total_tokens'),
            func.sum(AgentTask.cost_usd).label('total_cost'),
        ).where(
            AgentTask.project_id == id,
            AgentTask.tenant_id == ctx.tenant_id,
        )
    )
    task_agg = task_result.first()

    # Task counts by status
    status_result = await db.execute(
        select(AgentTask.status, func.count(AgentTask.id).label('count'))
        .where(AgentTask.project_id == id, AgentTask.tenant_id == ctx.tenant_id)
        .group_by(AgentTask.status)
    )
    status_counts = {row.status: row.count for row in status_result}

    # Workflow counts by status
    wf_result = await db.execute(
        select(WorkflowRun.status, func.count(WorkflowRun.id).label('count'))
        .where(WorkflowRun.project_id == id, WorkflowRun.tenant_id == ctx.tenant_id)
        .group_by(WorkflowRun.status)
    )
    workflow_counts = {row.status: row.count for row in wf_result}

    # Artifact counts
    from models.artifact import Artifact
    art_result = await db.execute(
        select(func.count(Artifact.id))
        .where(Artifact.project_id == id, Artifact.tenant_id == ctx.tenant_id, Artifact.is_deleted == False)
    )
    artifact_count = art_result.scalar() or 0

    return {
        'data': {
            'project_id': id,
            'total_tasks': task_agg.total_tasks or 0,
            'total_tokens': int(task_agg.total_tokens or 0),
            'total_cost_usd': round(float(task_agg.total_cost or 0), 4),
            'tasks_by_status': status_counts,
            'workflows_by_status': workflow_counts,
            'artifact_count': artifact_count,
        },
        'error': None,
    }
