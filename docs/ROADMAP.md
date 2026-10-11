# Kindlepreneur 2.0 — Product & Technical Roadmap

This document outlines the strategic engineering roadmap for Kindlepreneur 2.0, from the completed MVP foundation to future enterprise and autonomous capabilities.

---

## Roadmap Overview

```text
[PHASE 0] Foundation & Architecture ───────────► COMPLETED (100%)
[PHASE 1] Core Pipeline & 8 Specialist Agents ──► COMPLETED (100%)
[PHASE 2] Marketplace Studio & AudienceOS ─────► COMPLETED (100%)
[PHASE 3] Multi-Format Compiling & Visuals ────► COMPLETED (100%)
[PHASE 4] Official Live Marketplace & Email ───► CURRENT / UPCOMING (Q4 2026)
[PHASE 5] Global Scale, Audiobooks & Teams ────► FUTURE (2027)
```

---

## Completed Milestones

### Phase 0: Multi-Tenant Architecture & Data Layer (Done)
- [x] Multi-tenant database schema with Alembic migration engine (`001_initial_schema`).
- [x] Tenant-isolation middleware enforcing tenant-scoping on every SQL query.
- [x] Provider-independent LLM Gateway with token and cost tracking for Gemini, OpenAI, and Anthropic.
- [x] Durable storage abstraction (`LocalStorageBackend` and `S3StorageBackend` with boto3).
- [x] Docker Compose development environment (PostgreSQL 16 + Redis 7).

### Phase 1: Core Pipeline & Specialist Agents (Done)
- [x] 8 Specialist autonomous agents implemented with strict Pydantic schemas:
  - `ResearchAgent`, `StrategyAgent`, `OutlineAgent`, `WritingAgent`, `EditingAgent`, `FormattingAgent`, `MetadataAgent`, `ComplianceAgent`.
- [x] Deterministic Policy Engine (`PolicyRule`, `TenantActiveRule`, `BudgetRule`, `ExternalEffectApprovalRule`).
- [x] Human Approval Gateway with risk scoring, review UI, and pause/resume mechanics.
- [x] arq worker integration for durable long-running background tasks.
- [x] Antigravity spatial landing page with 3D isometric deck and ecosystem overview.
- [x] Comprehensive automated test suite (17 tests, 100% passing).

### Phase 2: Marketplace Studio & AudienceOS (Done)
- [x] Marketplace Studio data models (`MarketplaceAccount`, `MarketplaceListing`, `PublishingJob`).
- [x] 5-point vector preflight verification engine (trim, bleed, spine width, 7 keywords, AI disclosure).
- [x] Idempotent 1-click publishing execution with sandbox ASIN generation.
- [x] AudienceOS first-class consent engine (`SubscriberProfile`, `ConsentRecord`) for GDPR/CAN-SPAM compliance.
- [x] Real-time Value-First Content Safety & Anti-Spam Scanner.
- [x] Global Kill Switch emergency brake for immediate automation shutdown.
- [x] Full interactive frontend dashboard views for Marketplace Studio, AudienceOS, and Analytics.

### Phase 3: Multi-Format Compiling & Production Studios (Done)
- [x] **EPUB 3.0 Production Engine:**
  - Automated generation of standards-compliant EPUB 3.0 containers (uncompressed `mimetype` first entry, `META-INF/container.xml`, `content.opf`, `nav.xhtml`, CSS styling, and chapter XHTML files).
  - Passes EPUBCheck 5 structural compliance rules.
- [x] **Print-Ready 6x9 Interior PDF Generator:**
  - Pure Python PDF compilation generating standard PDF-1.4 files (432pt x 648pt) with alternating gutter margins, running headers, dynamic Table of Contents, and page numbering.
- [x] **Amazon KDP Cover Blueprint Calculator:**
  - Exact mathematical paperback cover wrap calculation (0.125" bleed, white 0.002252"/page vs. cream 0.002500"/page spine thickness factors, 300 DPI canvas coordinates, barcode safe zone, and >= 80 page spine text eligibility).
  - Midjourney/DALL-E prompt synthesis based on genre and canvas aspect ratios.
- [x] **Interactive Writing Studio (`/dashboard/writing`):**
  - Chapter drawer with live status, target word count tracking, and Flesch readability scores.
  - Distraction-free manuscript editor with autosave.
  - AI Co-Author controls: AI Trope Cleaner, Case Study Expander, and Developmental Editorial Critique.
  - 1-click manuscript compilation button.
- [x] **Digital Asset Vault (`/dashboard/assets`):**
  - Catalog of all generated EPUBs, PDFs, and cover specifications with SHA-256 checksums and direct downloads.
  - Interactive cover geometry diagram with live canvas preview.
- [x] **Marketing Launchpad (`/dashboard/marketing`):**
  - 6-week launch timeline (Week -4 to Week +2).
  - Advance Review Copy (ARC) team tracker with review link verification.
  - KDP Select vs. Wide distribution economics simulator.
- [x] **Expanded Automated Test Suite:**
  - 24/24 passing unit and integration tests covering EPUB/PDF generation, cover math, trope cleaner, and editorial QA.

---

## Active & Upcoming Milestones

### Phase 4: Official Live Marketplace & Email Gateways (Current Focus / Q4 2026)
- [ ] **Amazon SP-API Official OAuth Connector:**
  - Production OAuth 2.0 handshake with Amazon Seller Central for direct KDP catalog synchronization.
- [ ] **Etsy Open API v3 Production Connector:**
  - Live listing creation, digital file attachment, and inventory sync.
- [ ] **AudienceOS Transactional Email Gateway:**
  - Amazon SES / Resend webhook integration for automated double-opt-in confirmation links.
  - Automatic unsubscribe link handling and suppression list sync (`SuppressionRecord`).
- [ ] **Automated Nurture Sequence Scheduler:**
  - Chronological email delivery triggered by subscriber signup milestones (Day 0, Day 2, Day 7).

### Phase 5: Global Scale, Audiobooks & Team Workspaces (2027)
- [ ] **Audiobook Studio (Narration & ACX Compliance):**
  - Text-to-speech rendering using ElevenLabs or Azure Speech with custom narrator voices.
  - Automated ACX audio preflight checking (RMS levels, peak amplitude, noise floor).
- [ ] **Multi-Language Publishing & Localization:**
  - Semantic translation preserving authorial voice, cultural nuances, and localized KDP keywords.
- [ ] **Agency & Publisher Team Workspaces:**
  - Granular Role-Based Access Control (RBAC): Owner, Senior Editor, Ghostwriter, Proofreader, Client Viewer.
  - Project-level member invitations and per-user audit trails.
- [ ] **Closed-Loop Performance Optimization:**
  - Ingestion of live Amazon KDP royalty reports and advertising CPC metrics to trigger automated keyword and price re-optimization.
