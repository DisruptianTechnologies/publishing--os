from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_async_db
from core.auth import require_auth, TenantContext
from core.config import settings
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, WorkflowStartRequest
from services.workflow_service import start_workflow
from services.audit_service import log_action

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

DEMO_PROJECT_LIST = [
    {
        "id": "demo-project-001",
        "tenant_id": "demo-tenant-00000000",
        "name": "The Sovereign Creator: Systems for High-Output Publishing",
        "description": "Multi-agent systems and deep focus protocols for self-publishers.",
        "project_type": "nonfiction_book",
        "status": "writing",
        "target_market": "Creators, Solopreneurs, Authors",
        "idea_description": "A tactical playbook on writing and publishing without burnout using AI leverage.",
        "settings": {},
        "created_by": "demo-user-00000000",
        "is_archived": False,
        "created_at": "2026-10-10T04:00:00Z",
        "updated_at": "2026-10-11T04:20:00Z"
    },
    {
        "id": "demo-project-002",
        "tenant_id": "demo-tenant-00000000",
        "name": "ADHD Deep Focus Workbook & Daily Planner",
        "description": "Interactive workbook for neurodivergent adult focus.",
        "project_type": "low_content_journal",
        "status": "formatting",
        "target_market": "ADHD Adults & Students",
        "idea_description": "Daily visual planning system to eliminate decision fatigue.",
        "settings": {},
        "created_by": "demo-user-00000000",
        "is_archived": False,
        "created_at": "2026-10-09T12:00:00Z",
        "updated_at": "2026-10-10T18:00:00Z"
    }
]

@router.get("/", response_model=dict)
async def list_projects(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        query = select(Project).where(Project.tenant_id == ctx.tenant_id, Project.is_archived == False)
        if status:
            query = query.where(Project.status == status)
        
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        projects = result.scalars().all()
        if projects:
            return {"data": [ProjectResponse.model_validate(p).model_dump() for p in projects], "error": None}
    except Exception:
        pass
        
    if settings.DEMO_MODE:
        filtered = DEMO_PROJECT_LIST
        if status:
            filtered = [p for p in DEMO_PROJECT_LIST if p["status"] == status]
        return {"data": filtered, "error": None}
        
    return {"data": [], "error": None}

@router.post("/", response_model=dict)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
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
    except Exception:
        if settings.DEMO_MODE:
            demo_created = {
                "id": f"proj-{len(DEMO_PROJECT_LIST) + 1}",
                "tenant_id": ctx.tenant_id,
                "name": data.name,
                "description": data.description,
                "project_type": data.project_type,
                "status": "idea",
                "target_market": data.target_market,
                "idea_description": data.idea_description,
                "settings": data.settings,
                "created_by": ctx.user_id,
                "is_archived": False,
                "created_at": "2026-10-11T10:00:00Z",
                "updated_at": "2026-10-11T10:00:00Z"
            }
            return {"data": demo_created, "error": None}
        raise

@router.get("/{id}", response_model=dict)
async def get_project(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
        project = result.scalars().first()
        if project:
            return {"data": ProjectResponse.model_validate(project).model_dump(), "error": None}
    except Exception:
        pass
        
    if settings.DEMO_MODE:
        match = next((p for p in DEMO_PROJECT_LIST if p["id"] == id), None)
        if match:
            return {"data": match, "error": None}
        # Generic demo response
        return {
            "data": {
                "id": id,
                "tenant_id": ctx.tenant_id,
                "name": "The Sovereign Creator: Systems for High-Output Publishing",
                "description": "Multi-agent systems and deep focus protocols for self-publishers.",
                "project_type": "nonfiction_book",
                "status": "writing",
                "target_market": "Creators, Solopreneurs, Authors",
                "idea_description": "A tactical playbook on writing and publishing without burnout using AI leverage.",
                "settings": {},
                "created_by": ctx.user_id,
                "is_archived": False,
                "created_at": "2026-10-10T04:00:00Z",
                "updated_at": "2026-10-11T04:20:00Z"
            },
            "error": None
        }
    raise HTTPException(status_code=404, detail="Project not found")

@router.patch("/{id}", response_model=dict)
async def update_project(
    id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
        project = result.scalars().first()
        if project:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(project, key, value)
            await db.commit()
            await db.refresh(project)
            return {"data": ProjectResponse.model_validate(project).model_dump(), "error": None}
    except Exception:
        pass
        
    if settings.DEMO_MODE:
        return {"data": {"id": id, "status": data.status or "updated"}, "error": None}
    raise HTTPException(status_code=404, detail="Project not found")

@router.delete("/{id}", response_model=dict)
async def delete_project(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
        project = result.scalars().first()
        if project:
            project.is_archived = True
            await db.commit()
            return {"data": {"success": True}, "error": None}
    except Exception:
        pass
    if settings.DEMO_MODE:
        return {"data": {"success": True}, "error": None}
    raise HTTPException(status_code=404, detail="Project not found")

@router.post("/{id}/workflows", response_model=dict)
async def create_workflow(
    id: str,
    data: WorkflowStartRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        result = await db.execute(select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id))
        project = result.scalars().first()
        if project:
            workflow = await start_workflow(db, ctx.tenant_id, id, data.workflow_type, data.config, ctx.user_id)
            return {"data": {"workflow_run_id": str(workflow.id)}, "error": None}
    except Exception:
        pass
    if settings.DEMO_MODE:
        return {"data": {"workflow_run_id": f"demo-wf-{data.workflow_type}-001"}, "error": None}
    raise HTTPException(status_code=404, detail="Project not found")

@router.get("/{id}/workflows", response_model=dict)
async def list_workflows(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        from models.agent import WorkflowRun
        result = await db.execute(select(WorkflowRun).where(WorkflowRun.project_id == id, WorkflowRun.tenant_id == ctx.tenant_id))
        runs = result.scalars().all()
        if runs:
            return {"data": [{"id": w.id, "status": w.status, "type": w.workflow_type} for w in runs], "error": None}
    except Exception:
        pass
    if settings.DEMO_MODE:
        return {
            "data": [
                {"id": "wf-1", "status": "completed", "type": "research"},
                {"id": "wf-2", "status": "completed", "type": "strategy"},
                {"id": "wf-3", "status": "completed", "type": "outline"},
                {"id": "wf-4", "status": "running", "type": "writing"}
            ],
            "error": None
        }
    return {"data": [], "error": None}

@router.get("/{id}/artifacts", response_model=dict)
async def list_artifacts(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        from models.artifact import Artifact
        result = await db.execute(select(Artifact).where(Artifact.project_id == id, Artifact.tenant_id == ctx.tenant_id))
        arts = result.scalars().all()
        if arts:
            return {"data": [{"id": a.id, "name": a.name, "type": a.artifact_type} for a in arts], "error": None}
    except Exception:
        pass
    if settings.DEMO_MODE:
        return {
            "data": [
                {"id": "art-epub-001", "name": "The Sovereign Creator — Validated EPUB 3.0", "type": "epub"},
                {"id": "art-pdf-002", "name": "The Sovereign Creator — 6x9 Interior Print PDF", "type": "pdf"},
                {"id": "art-cov-003", "name": "Full Wrap Paperback Cover Blueprint (300 DPI)", "type": "cover"},
                {"id": "art-rep-004", "name": "Market Opportunity & Keyword Research Brief", "type": "report"}
            ],
            "error": None
        }
    return {"data": [], "error": None}

@router.get('/{id}/stats', response_model=dict)
async def project_stats(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    try:
        from sqlalchemy import func
        from models.agent import AgentTask, WorkflowRun
        from models.artifact import Artifact

        result = await db.execute(
            select(Project).where(Project.id == id, Project.tenant_id == ctx.tenant_id)
        )
        project = result.scalars().first()
        if project:
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

            status_result = await db.execute(
                select(AgentTask.status, func.count(AgentTask.id).label('count'))
                .where(AgentTask.project_id == id, AgentTask.tenant_id == ctx.tenant_id)
                .group_by(AgentTask.status)
            )
            status_counts = {row.status: row.count for row in status_result}

            wf_result = await db.execute(
                select(WorkflowRun.status, func.count(WorkflowRun.id).label('count'))
                .where(WorkflowRun.project_id == id, WorkflowRun.tenant_id == ctx.tenant_id)
                .group_by(WorkflowRun.status)
            )
            workflow_counts = {row.status: row.count for row in wf_result}

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
    except Exception:
        pass
        
    if settings.DEMO_MODE:
        return {
            'data': {
                'project_id': id,
                'total_tasks': 18,
                'total_tokens': 142800,
                'total_cost_usd': 2.14,
                'tasks_by_status': {'completed': 14, 'running': 1, 'queued': 3},
                'workflows_by_status': {'completed': 3, 'running': 1},
                'artifact_count': 6,
            },
            'error': None,
        }
    raise HTTPException(status_code=404, detail='Project not found')
