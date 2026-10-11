# Kindlepreneur 2.0 — Features & Functionalities Reference

Kindlepreneur 2.0 is a multi-tenant, multi-agent publishing and digital-commerce operating system. It provides an automated, supervised lifecycle taking ideas through research, strategy, drafting, editorial QA, formatting, metadata optimization, marketplace publishing, and consent-driven audience building.

---

## 1. System Ecosystem Overview

The platform is organized into three primary operational pillars supported by an internal execution layer:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        KINDLEPRENEUR 2.0 PLATFORM                      │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ 1. PUBLISHING OS   │ 2. MARKETPLACE     │ 3. AUDIENCEOS                │
│    Idea to QA      │    Distribution    │    Owned Audience Growth     │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ • Research Analyst │ • Amazon KDP Sand. │ • Verifiable Consent Ledger  │
│ • Strategy Arch.   │ • Etsy Printables  │ • Value-First Safety Scanner │
│ • Master Outliner  │ • Vector Preflight │ • Double Opt-In Manager      │
│ • Ghostwriter      │ • Idempotent Push  │ • Emergency Kill Switch      │
│ • Dev Editor QA    │ • Package Staging  │ • Lead Magnet Attribution    │
│ • Format & Metadata│ • ISBN & ASIN Sync │ • Nurture Sequence Auto-Flow │
├────────────────────┴────────────────────┴──────────────────────────────┤
│              POLICY & APPROVAL GATEWAY (BLOCKING CONTROLS)              │
│       • Deterministic Rules • Cost Caps • Risk Score Thresholds        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pillar 1: Publishing OS

Publishing OS handles the end-to-end creation of commercially viable non-fiction, fiction, journals, and digital assets.

### 2.1 The 10-Stage Research-to-Revenue Pipeline
Every project progresses through structured stages with strict state transitions:
1. **Idea Ingestion:** Captures niche hypothesis, target audience profile, and customer pain points.
2. **Market Research:** Evaluates commercial viability, demand signals, search volume, and competitor weaknesses.
3. **Opportunity Scoring:** Generates an algorithmic `opportunity_score` (0–10) with demand and competition indices.
4. **Product Strategy:** Defines the Unique Selling Proposition (USP), pricing recommendation, and reading level.
5. **Outlining:** Builds a hierarchical chapter blueprint with research slots and case study placeholders.
6. **Drafting:** Writes trope-free, active-voice chapters without generic AI filler phrases.
7. **Editorial QA:** Rigorous developmental critique assessing readability (Flesch score) and blocking issues.
8. **Interior & Cover Formatting:** Prepares interior layout guidelines (6x9 trim, bleed margins, font styling).
9. **SEO Metadata Optimization:** Generates 7 compliant KDP backend keywords, BISAC categories, and HTML book description.
10. **Compliance Audit:** Scans for copyright risks, trademark conflicts, unverified factual claims, and mandatory AI disclosures.

### 2.2 The 8 Specialist Autonomous Agents
Each agent has a dedicated role, versioned prompt, strict Pydantic input/output schema, and token budget:

| Specialist Agent | Agent Type | Primary Model Policy | Primary Deliverable |
| :--- | :--- | :--- | :--- |
| **Research Analyst** | `research_agent` | `gemini-2.0-flash` (Fast) | `ResearchOutput` (Opportunity score, demand & competitor signals) |
| **Strategy Architect** | `strategy_agent` | `gemini-1.5-pro` (Deep) | `StrategyOutput` (USP, target customer, pricing range, launch plan) |
| **Master Outliner** | `outline_agent` | `gemini-1.5-pro` (Deep) | `OutlineOutput` (Chapter breakdown, word counts, title candidates) |
| **Chapter Ghostwriter** | `writing_agent` | `gemini-1.5-pro` (Deep) | `WritingOutput` (Chapter content, claims made, [VERIFY] tags) |
| **Developmental Editor** | `editing_agent` | `gemini-1.5-flash` (Fast) | `EditingOutput` (Flesch readability score, numbered findings) |
| **Formatting Specialist**| `formatting_agent`| `gemini-2.0-flash` (Fast) | `FormattingOutput` (Trim size, bleed specs, preflight results) |
| **SEO Metadata Expert** | `metadata_agent` | `gemini-2.0-flash` (Fast) | `MetadataOutput` (7 KDP keywords, HTML description, BISAC paths) |
| **Compliance Guard** | `compliance_agent`| `gemini-1.5-pro` (Deep) | `ComplianceOutput` (Copyright, trademark, and AI disclosure audit) |

### 2.3 Structured Artifacts & Versioning
- Artifacts are stored in durable object storage (`LocalStorageBackend` or `S3StorageBackend`).
- Every revision increments `ArtifactVersion` with SHA-256 checksums, creator metadata, prompt versions, and token cost records.
- Approved artifacts cannot be silently overwritten; all updates generate audit events.

---

## 3. Pillar 2: Marketplace Studio

Marketplace Studio connects structured book artifacts with digital retail storefronts.

### 3.1 Multi-Marketplace Channel Management
- Supports multiple connected accounts (`MarketplaceAccount`) across Amazon KDP and Etsy Printables.
- Tracks authorization state, rate limit quotas, and synchronization timestamps.

### 3.2 Automated 5-Point Preflight Inspection Engine
Before any package can be published, the preflight engine (`run_package_preflight`) executes:
1. **Interior Trim & Bleed Inspection:** Validates page vector geometry against Amazon KDP print requirements (e.g. 6x9 inches, 0.125" bleed).
2. **Cover Barcode & Spine Calculation:** Computes exact spine width based on interior page count and paper type.
3. **Keyword Density & Trademark Sweep:** Scans title and 7 backend keywords against USPTO trademark databases.
4. **BISAC & Browse Node Resolution:** Validates marketplace category paths against Amazon browse nodes.
5. **Editorial & AI Disclosure Compliance:** Ensures mandatory platform AI-assistance disclosures are properly formatted.

### 3.3 Idempotent 1-Click Publishing Execution
- Uses unique idempotency keys (`idempotency_key`) to prevent duplicate listings on network retries.
- Simulates complete publication workflows in sandbox mode, producing mock ASINs (`B0...`) and Etsy listing URLs.

---

## 4. Pillar 3: AudienceOS

AudienceOS manages post-publication reader growth, conversion, and community distribution with strict ethical and legal safeguards.

### 4.1 First-Class Verifiable Consent Ledger
- **Consent as a First-Class Object:** Every reader profile (`SubscriberProfile`) is bound to a cryptographic `ConsentRecord`.
- Stores consent method (`gdpr_double_opt_in`, `can_spam_verified`), timestamp, source IP, and lead magnet attribution.
- **Instant Revocation:** Dedicated endpoint to immediately revoke consent and halt all communications.

### 4.2 Value-First Content Safety & Anti-Spam Scanner
- Scans proposed community engagement drafts, forum responses, and nurture emails in real time.
- **Deterministic Blocking Rules:**
  - Blocks commercial hype (e.g., *"guaranteed #1 bestseller"*, *"make money fast"*, *"guaranteed sales"*).
  - Flags unsolicited promotional outreach (e.g., *"dm me for"*).
  - Flags link shorteners on platforms where direct links trigger anti-spam flags (e.g., Reddit).
- Outputs an objective compliance score (0.0 to 1.0) and actionable remediation items.

### 4.3 Global Kill Switch Mechanism
- System-wide emergency brake (`GlobalKillSwitch`) that immediately halts all outbound agent workflows, social posting jobs, and nurture email dispatchers across the tenant.
- Accessible via API and the interactive dashboard with instant toggle controls.

---

## 5. Control Tower & Human Approval Gateway

### 5.1 Blocking Human-in-the-Loop Gateway
- **Policy as Execution Layer:** Irreversible or high-risk actions (publishing to store, sending mass emails, large budget increases) are blocked until approved by an authorized user.
- Approval requests (`ApprovalRequest`) include:
  - Calculated risk score (0.0 to 1.0).
  - Evidence summary and citation links.
  - Expected external side effects and estimated financial cost.
  - Expiration timestamps.

### 5.2 Observability & Telemetry
- Real-time token usage and dollar cost tracking by agent and model.
- Pipeline velocity metrics calculating duration per stage and identifying bottlenecks.
- Full immutable audit log (`AuditLog`) capturing all actions, IP addresses, actors, and correlation IDs.
