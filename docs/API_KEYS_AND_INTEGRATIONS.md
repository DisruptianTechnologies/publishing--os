# Kindlepreneur 2.0 — API Keys & Integrations Guide

This guide details all external services, credentials, and API keys required or supported by Kindlepreneur 2.0, along with instructions on obtaining them and configuring them securely.

---

## 1. Summary of Credentials

| Service | Category | Required For | Env Variable | Demo Mode Fallback? |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini API** | LLM Gateway | Live agent intelligence (Default) | `GEMINI_API_KEY` | Yes (Mock outputs available) |
| **OpenAI API** | LLM Gateway | Fallback / alternative provider | `OPENAI_API_KEY` | Yes |
| **Anthropic Claude API**| LLM Gateway | Fallback / deep reasoning | `ANTHROPIC_API_KEY` | Yes |
| **Clerk Auth** | Authentication | User accounts, SSO, RBAC | `CLERK_SECRET_KEY`, `CLERK_PUBLISHABLE_KEY` | Yes (`DEMO_MODE=true` bypass) |
| **PostgreSQL 16** | Database | Multi-tenant persistent store | `DATABASE_URL` | Yes (Memory/mock fallback) |
| **Redis 7** | Cache & Queue | Background arq task queue & pub/sub | `REDIS_URL` | Yes |
| **AWS S3 / R2** | Storage | Production manuscript artifact storage | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET` | Yes (`STORAGE_BACKEND=local`) |
| **Amazon SP-API** | Marketplace | Direct Amazon KDP publishing | `AMAZON_APP_CLIENT_ID`, `AMAZON_APP_CLIENT_SECRET` | Yes (Sandbox simulation) |
| **Etsy Open API v3** | Marketplace | Direct Etsy digital listing push | `ETSY_API_KEY`, `ETSY_SHARED_SECRET` | Yes (Sandbox simulation) |

---

## 2. LLM Provider Credentials

Kindlepreneur 2.0 uses a provider-independent LLM Gateway located in `packages/llm_gateway/gateway.py`. You only need **one** active LLM provider, though configuring multiple provides automatic fallback resilience.

### 2.1 Google Gemini (Recommended Primary Provider)
- **Why:** High reasoning speed, large context windows, native structured JSON enforcement, and cost efficiency.
- **Models Used:** `gemini-2.0-flash` (Research, Formatting, Metadata) and `gemini-1.5-pro` (Strategy, Outlining, Ghostwriting, Compliance).
- **How to Get Your Key:**
  1. Visit the [Google AI Studio](https://aistudio.google.com/).
  2. Sign in with your Google account.
  3. Click **Get API key** ➔ **Create API key**.
  4. Copy the key and place it in `apps/api/.env`:
     ```ini
     LLM_PROVIDER=gemini
     GEMINI_API_KEY=AIzaSy...
     ```

### 2.2 OpenAI (Alternative Provider)
- **Models Used:** `gpt-4o-mini` (Fast) and `gpt-4o` (Deep).
- **How to Get Your Key:**
  1. Go to the [OpenAI Platform](https://platform.openai.com/).
  2. Navigate to **API Keys** under your project settings.
  3. Click **Create new secret key** and copy it:
     ```ini
     OPENAI_API_KEY=sk-proj-...
     ```

### 2.3 Anthropic Claude (Alternative Provider)
- **Models Used:** `claude-3-haiku-20240307` and `claude-3-5-sonnet-20241022`.
- **How to Get Your Key:**
  1. Go to the [Anthropic Console](https://console.anthropic.com/).
  2. Navigate to **API Keys** and generate a new key:
     ```ini
     ANTHROPIC_API_KEY=sk-ant-...
     ```

---

## 3. User Authentication: Clerk

Clerk powers multi-tenant organization management, JWT verification, and user roles.

### Getting Production Clerk Keys:
1. Create a free account at [Clerk.com](https://clerk.com/).
2. Create an application named **Kindlepreneur 2.0**.
3. In the Clerk Dashboard, navigate to **API Keys**.
4. Copy the Publishable Key and Secret Key into:
   - `apps/web/.env.local`:
     ```ini
     NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
     CLERK_SECRET_KEY=sk_live_...
     ```
   - `apps/api/.env`:
     ```ini
     CLERK_SECRET_KEY=sk_live_...
     CLERK_PUBLISHABLE_KEY=pk_live_...
     ```

> **Developer Note:** If you leave the keys empty or use `pk_test_...`, the system stays in `DEMO_MODE=true` mode, allowing immediate browsing of `/dashboard` without needing live sign-in.

---

## 4. Object Storage: AWS S3 / Cloudflare R2 / MinIO

For production deployments, manuscripts, generated EPUBs, and high-resolution PDF print interiors are stored in S3-compatible object storage.

### Configuration (`apps/api/.env`):
```ini
STORAGE_BACKEND=s3
S3_BUCKET=kindlepreneur-artifacts-prod
S3_ENDPOINT=https://s3.us-east-1.amazonaws.com # Or Cloudflare R2 endpoint
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

For local development, keep `STORAGE_BACKEND=local`. Files will be saved in `apps/api/storage/`.

---

## 5. Marketplace Connectors

### 5.1 Amazon Selling Partner API (SP-API) / KDP
- **Purpose:** Idempotent submission of manuscript packages, book metadata, pricing, and category placement.
- **Obtaining Access:** Requires registration as an Amazon Selling Partner Developer in [Amazon Seller Central](https://sellercentral.amazon.com/).
- **Required Credentials:**
  - LWA (Login with Amazon) Client ID & Client Secret
  - AWS IAM Role ARN for SP-API
  - Refresh Token
- **Sandbox Mode:** Kindlepreneur includes built-in adapter mocks (`packages/marketplace_service.py`) that simulate KDP package ingestion and return simulated ASIN identifiers (`B0...`) for testing without a live developer account.

### 5.2 Etsy Open API v3
- **Purpose:** Publishing printable planners, gratitude journals, and digital workbook bundles.
- **Obtaining Access:** Register an application on the [Etsy Developer Portal](https://developers.etsy.com/).
- **Required Scopes:** `listings_w`, `listings_r`, `shops_r`.
- **Sandbox Mode:** Full Etsy OAuth 2.0 simulation is included with rate-limiting counters.

---

## 6. AudienceOS Email Dispatchers (Post-MVP)

For Phase 3/4 automated double-opt-in subscriber validation and welcome sequences, AudienceOS connects with transactional email providers:

| Provider | Recommended Scenarios | Environment Variables |
| :--- | :--- | :--- |
| **Amazon SES** | High-volume, lowest per-email cost ($0.10/1000) | `SES_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_KEY` |
| **Postmark** | Dedicated delivery for transactional opt-in emails | `POSTMARK_SERVER_API_TOKEN` |
| **Resend** | Modern developer experience with React email templates | `RESEND_API_KEY` |

---

## 7. Security Best Practices

1. **Never Commit Secrets:** `.env` and `.env.local` are explicitly added to `.gitignore`. Never commit them to version control.
2. **Principle of Least Privilege:** S3 IAM policies should only grant `PutObject`, `GetObject`, and `DeleteObject` scoped to the tenant's prefix (`s3://bucket/{tenant_id}/*`).
3. **Idempotency Keys:** All external connector calls generate SHA-256 idempotency tokens (`X-Idempotency-Key: IDEM-{timestamp}-{hash}`) to prevent duplicate charges or listing creation on network drops.
