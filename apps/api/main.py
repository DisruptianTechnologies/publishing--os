import sys
import os
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from core.database import init_db
from core.config import settings
from routers.projects import router as projects_router
from routers.artifacts import router as artifacts_router
from routers.approvals import router as approvals_router
from routers.tasks import router as tasks_router
from routers.analytics import router as analytics_router
from routers.marketplace import router as marketplace_router
from routers.audience import router as audience_router
from routers.compilation import router as compilation_router
from routers.writing import router as writing_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database if configured
    try:
        await init_db()
    except Exception:
        # In testing or when migrations are preferred, continue gracefully
        pass
    yield

app = FastAPI(title="Kindlepreneur API", version="2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Correlation-Id"] = correlation_id
    return response

app.include_router(projects_router)
app.include_router(artifacts_router)
app.include_router(approvals_router)
app.include_router(tasks_router)
app.include_router(analytics_router)
app.include_router(marketplace_router)
app.include_router(audience_router)
app.include_router(compilation_router)
app.include_router(writing_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
