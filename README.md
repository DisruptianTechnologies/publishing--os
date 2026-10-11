# Kindlepreneur 2.0 — Publishing OS & AudienceOS

> Multi-tenant, policy-bounded multi-agent publishing and digital-commerce operating system. Transforming validated ideas into market-ready books, digital storefront listings, and consent-driven owned audiences.

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.3.4-black.svg)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19.0-61dafb.svg)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-v4.1-38bdf8.svg)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/pytest-32%2F32%20passing-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Phase-Phase%203%20Complete-success.svg)]()

---

## Table of Contents

- [Ecosystem Overview](#ecosystem-overview)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Quick Start in 3 Minutes](#quick-start-in-3-minutes)
- [Localhost Access Links](#localhost-access-links)
- [Phase 3 Multi-Format Compilation Endpoints](#phase-3-multi-format-compilation-endpoints)
- [Specialist Agent Swarm](#specialist-agent-swarm)
- [Detailed Documentation Suite](#detailed-documentation-suite)
- [Development Roadmap](#development-roadmap)
- [Verification & Testing](#verification--testing)

---

## Ecosystem Overview

Kindlepreneur 2.0 is built on four interconnected operational pillars backed by an execution layer:

1. **Publishing OS:** The 10-stage Research-to-Revenue pipeline from idea validation, opportunity scoring, hierarchical outlining, active-voice drafting, developmental editorial QA, to KDP print formatting.
2. **Production Studios (Phase 3):** Automated EPUB 3.0 compilation, 6x9 interior PDF generation, KDP paperback wrap calculator with 300 DPI canvas coordinates, and interactive manuscript writing studio.
3. **Marketplace Studio:** Multi-channel distribution (Amazon KDP & Etsy Printables) with automated 5-point vector preflight verification and idempotent publishing jobs.
4. **AudienceOS:** Permission-based reader discovery, GDPR/CAN-SPAM double-opt-in consent ledger, real-time value-first content safety auditing, and a global emergency kill switch.
5. **Control Tower & Policy Engine:** A blocking authorization gateway that enforces budget limits, autonomy caps, and human sign-off for high-risk external side effects.

---

## Architecture & Tech Stack

```text
kindlepreneur-2/
├── apps/
│   ├── api/             # FastAPI Backend
│   │   ├── core/        # Tenant middleware, JWT auth, storage, database
│   │   ├── models/      # SQLAlchemy 2.0 async models (25 domain tables)
│   │   ├── routers/     # 9 REST API routers (Projects, Artifacts, Approvals, Compilation, Writing, etc.)
│   │   ├── services/    # Business services (Compilation, Cover, Chapter, Workflow, Marketplace, Audience)
│   │   └── workers/     # arq background task worker with Redis
│   └── web/             # Next.js 15.3.4 App Router
│       ├── app/         # 16 verified routes + Antigravity 3D landing page
│       ├── components/  # Spatial 3D, weightless cards, glassmorphic pills
│       └── lib/         # Typed API client with complete Phase 3 bindings
├── packages/            # Core Domain Packages
│   ├── agents/          # 8 specialist autonomous agents with Pydantic schemas
│   ├── llm_gateway/     # Provider-agnostic gateway (Gemini, OpenAI, Anthropic)
│   └── policy_engine/   # Deterministic policy rules and approval gating
├── migrations/          # Alembic database migration scripts (001, 002)
├── docs/                # Comprehensive technical documentation suite
├── docker-compose.dev.yml
└── .env.example
```

---

## Quick Start in 3 Minutes

### 1. Backend (FastAPI on Port 8000)
```bash
cd apps/api
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1 | Unix: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend (Next.js on Port 3000)
```bash
cd apps/web
npm install
npm run dev
# OR for production build:
npm run build && npm start
```

> **Zero-Friction Demo Mode:** Both frontend and backend ship with `DEMO_MODE=true` enabled by default. You can test all UI routes, run preflight simulations, compile EPUB/PDFs, review consent logs, and audit content without setting up external API keys or Docker!

---

## Localhost Access Links

| Surface | URL | What to View / Test |
| :--- | :--- | :--- |
| **Landing Page** | [http://localhost:3000/](http://localhost:3000/) | 3D isometric deck, 10-stage pipeline, 8 agents, approval simulator |
| **Command Center** | [http://localhost:3000/dashboard](http://localhost:3000/dashboard) | Active projects, recent agent activity, quick starts |
| **Writing Studio** | [http://localhost:3000/dashboard/writing](http://localhost:3000/dashboard/writing) | Interactive manuscript editor, chapter drawer, AI Trope Cleaner, 1-click compiler |
| **Digital Asset Vault** | [http://localhost:3000/dashboard/assets](http://localhost:3000/dashboard/assets) | EPUB/PDF artifact catalog, SHA-256 hashes, KDP cover wrap calculator & blueprint |
| **Marketing Launchpad** | [http://localhost:3000/dashboard/marketing](http://localhost:3000/dashboard/marketing) | 6-week launch roadmap, ARC review team tracker, KDP Select vs. Wide economics |
| **Marketplace Studio** | [http://localhost:3000/dashboard/marketplace](http://localhost:3000/dashboard/marketplace) | Connected KDP/Etsy accounts, 5-point preflight audit, 1-click publishing |
| **AudienceOS** | [http://localhost:3000/dashboard/audience](http://localhost:3000/dashboard/audience) | Consent Ledger, real-time value-first safety scanner, global kill switch |
| **Analytics & Telemetry** | [http://localhost:3000/dashboard/analytics](http://localhost:3000/dashboard/analytics) | Live agent token and cost telemetry, pipeline velocity benchmarks |
| **Niche Research Lab** | [http://localhost:3000/dashboard/research](http://localhost:3000/dashboard/research) | Commercial viability evaluation and competitor signal analysis |
| **Human Approval Inbox** | [http://localhost:3000/dashboard/approvals](http://localhost:3000/dashboard/approvals) | Human-in-the-loop review queue for irreversible actions |
| **FastAPI Swagger Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive OpenAPI documentation for all 9 routers |
| **Backend Health Check** | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) | API health check endpoint (`{"status": "ok"}`) |

---

## Phase 3 Multi-Format Compilation Endpoints

The API provides production-grade endpoints for multi-format publishing:

- `POST /api/v1/projects/{id}/compile`: Compiles full manuscript into validated EPUB 3.0 container and 6x9 interior PDF.
- `GET /api/v1/projects/{id}/export/{format}`: Streams compiled binary files (`.epub` or `.pdf`) with content-disposition headers.
- `POST /api/v1/projects/{id}/cover/dimensions`: Calculates exact spine width, bleed margins, 300 DPI canvas coordinates, and barcode placement.
- `POST /api/v1/projects/{id}/cover/prompt`: Generates Midjourney/DALL-E cover art prompts with exact canvas aspect ratios.
- `GET /api/v1/projects/{id}/chapters`: Retrieves chapter list with word count stats, statuses, and Flesch readability scores.
- `POST /api/v1/projects/{id}/chapters/{num}/assist`: Executes AI Trope Cleaner, Case Study Expander, or Developmental Editorial Critique.

---

## Specialist Agent Swarm

The internal execution layer delegates tasks to 8 specialized agents rather than one general-purpose model:

1. **Research Analyst:** Market viability, demand signals, and opportunity score (0–10).
2. **Strategy Architect:** Unique selling proposition, pricing strategy, and launch roadmap.
3. **Master Outliner:** Hierarchical chapter blueprint with research slots and case study placeholders.
4. **Chapter Ghostwriter:** Active voice, bursty, trope-free chapter content.
5. **Developmental Editor:** Structural review, readability analysis, and publication-readiness score.
6. **Formatting Specialist:** 6x9 print layout, bleed margins, and font specification.
7. **SEO Metadata Expert:** 7 KDP backend keywords, BISAC browse nodes, and HTML description.
8. **Compliance Guard:** Copyright audit, trademark sweep, factual verification, and AI disclosure.

---

## Detailed Documentation Suite

Complete guides are located in the [`docs/`](./docs) directory:

- 🛠 **[Installation & Local Setup Guide](./docs/INSTALLATION_GUIDE.md):** Step-by-step setup, Docker Compose, Alembic migrations, and environments.
- ⚙️ **[Features & Functionality Reference](./docs/FEATURES_AND_FUNCTIONALITY.md):** In-depth functional specification of Publishing OS, Marketplace Studio, and AudienceOS.
- 🔑 **[API Keys & Integrations Guide](./docs/API_KEYS_AND_INTEGRATIONS.md):** Credentials guide for Gemini, OpenAI, Anthropic, Clerk, S3, Amazon SP-API, and Etsy.
- 🗺 **[Product & Technical Roadmap](./docs/ROADMAP.md):** Milestone breakdown from MVP completion through multi-format compilation and global scale.

---

## Verification & Testing

Verify system stability with the built-in test commands:

```bash
# 1. Backend automated test suite (32 tests)
cd apps/api
python -m pytest tests -v

# 2. Frontend TypeScript type checking
cd apps/web
npm run type-check

# 3. Next.js production build (16 routes)
cd apps/web
npm run build
```
