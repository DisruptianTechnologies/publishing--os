# Kindlepreneur 2.0 — Installation & Local Setup Guide

This guide provides instructions for setting up, configuring, and running Kindlepreneur 2.0 locally on Windows, macOS, or Linux.

---

## 1. System Prerequisites

Before starting, ensure you have the following installed on your workstation:

| Prerequisite | Minimum Version | Recommended Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Node.js** | `v20.x` | `v20.18.0` LTS | Next.js 15 web application runtime |
| **npm** | `v10.x` | `v10.9.x` | Node package manager |
| **Python** | `3.11.x` | `3.11.9` or `3.12.x` | FastAPI backend, specialist agents, and arq worker |
| **Git** | `2.x` | Latest | Version control |
| **Docker & Compose** | Optional | Docker Desktop v24+ | Local PostgreSQL 16 & Redis 7 services |

---

## 2. Repository Layout

```text
kindlepreneur-2/
├── apps/
│   ├── api/             # FastAPI backend (Python 3.11/3.12)
│   │   ├── core/        # Auth, config, database, storage, errors
│   │   ├── models/      # SQLAlchemy 2.0 async models (25 tables)
│   │   ├── routers/     # API route handlers
│   │   ├── schemas/     # Pydantic v2 validation contracts
│   │   ├── services/    # Business logic, workflows, marketplace, audience
│   │   ├── workers/     # arq background task workers
│   │   └── tests/       # Automated pytest suite (17 tests)
│   └── web/             # Next.js 15.3.4 App Router frontend
│       ├── app/         # Pages, layouts, API bindings
│       ├── components/  # Antigravity UI components
│       └── lib/         # Typed API client (lib/api.ts)
├── packages/            # Core Python domain packages
│   ├── agents/          # 8 specialist autonomous agent implementations
│   ├── llm_gateway/     # Provider-agnostic gateway (Gemini/OpenAI/Anthropic)
│   └── policy_engine/   # Deterministic policy rules and approval gates
├── migrations/          # Alembic database migration scripts
├── docs/                # Project documentation suite
├── docker-compose.dev.yml
└── .env.example
```

---

## 3. Backend Setup (`apps/api`)

### Step 3.1: Navigate to API Directory
```bash
cd apps/api
```

### Step 3.2: Python Virtual Environment (Recommended)
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3.3: Install Dependencies
```bash
pip install -r requirements.txt
```
Key packages installed:
- `fastapi`, `uvicorn[standard]`, `pydantic>=2.9`, `pydantic-settings`
- `sqlalchemy>=2.0`, `asyncpg`, `alembic`
- `redis`, `arq`, `boto3`
- `python-jose`, `httpx`, `pytest`, `pytest-asyncio`

### Step 3.4: Configure Backend Environment
Copy the example environment file or configure `.env` inside `apps/api/.env`:
```ini
# Database & Cache (Defaults work for local dev / demo mode)
DATABASE_URL=postgresql+asyncpg://kp:devpassword@localhost:5432/kindlepreneur
REDIS_URL=redis://localhost:6379

# LLM Providers (Optional for demo mode; add your key to run live agents)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Storage Backend
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./storage

# App Mode
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
DEMO_MODE=true
```

> **Note on Demo Mode:** When `DEMO_MODE=true`, the API automatically provisions a sandboxed demo tenant (`demo-tenant-00000000`) and mock user. You can test all API endpoints and mock agent outputs without live external API keys.

---

## 4. Frontend Setup (`apps/web`)

### Step 4.1: Navigate to Web Directory
```bash
cd apps/web
```

### Step 4.2: Install Node Dependencies
```bash
npm install
```

### Step 4.3: Configure Frontend Environment
Ensure `apps/web/.env.local` contains:
```ini
# Clerk Authentication (Default test keys enabled)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_Y2xlcmsua2luZGxlcHJlbmV1ci5kZXYk
CLERK_SECRET_KEY=sk_test_devmocksecretkey
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# API Connection
NEXT_PUBLIC_API_URL=http://localhost:8000

# App Settings
NEXT_PUBLIC_APP_NAME=Kindlepreneur 2.0
NEXT_PUBLIC_DEMO_MODE=true
DEMO_MODE=true
```

---

## 5. Database & Migrations Setup

### Option A: Using Local Docker (PostgreSQL + Redis)
If you have Docker Desktop installed, start PostgreSQL and Redis with a single command:
```bash
# From project root
docker compose -f docker-compose.dev.yml up -d postgres redis
```

### Option B: Running Alembic Migrations
Once PostgreSQL is running:
```bash
# From project root
alembic upgrade head
```
This applies:
- `001_initial_schema`: Base tables (tenants, users, projects, artifacts, workflows, approvals, audit).
- `002_phase2_marketplace_audience`: Marketplace accounts, listings, publishing jobs, subscribers, consent records, and kill switches.

*(If running without Docker, the API graceful startup handler allows running in zero-friction demo mode without database failure).*

---

## 6. Running the Servers

### Terminal 1: FastAPI Backend
```bash
# In apps/api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Healthcheck: `http://127.0.0.1:8000/health`

### Terminal 2: Background Task Worker (Optional for local queue execution)
```bash
# In apps/api
python -m arq workers.worker.WorkerSettings
```

### Terminal 3: Next.js Frontend
```bash
# In apps/web
npm run dev
# OR for production build:
npm run build
npm start
```
- Web Application: `http://localhost:3000`

---

## 7. Running Verification Tests

To verify that the backend and frontend are properly configured and all subsystems function correctly:

### Backend Automated Tests
```bash
cd apps/api
python -m pytest tests -v
```
*Expected: 17 passed in ~2s.*

### Frontend TypeScript Verification
```bash
cd apps/web
npm run type-check
```
*Expected: 0 errors.*

### Frontend Production Build
```bash
cd apps/web
npm run build
```
*Expected: 13/13 static and dynamic routes compiled successfully.*
