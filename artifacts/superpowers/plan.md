# Superpowers Implementation Plan: Creative Leaderboard

## Goal
Build and deploy a 100% open-source, $0/month full-stack web application called **Creative Leaderboard** for solo performance marketing operators. The app ranks Meta ad creatives in real-time with a fast, high-density, gamified dark-theme leaderboard. It automates status classification (`WIN`, `LOSS`, `TESTING`, `PAUSED`), tracks streaks (`🔥` flame / `❄️` ice), computes rank movement deltas vs. yesterday, aggregates client portfolio health, renders 30-day interactive Recharts trendlines, runs 4-hour background & on-demand Meta Marketing API (v18.0) syncs with immutable daily snapshots, and provides fallback bulk CSV/TSV paste importing and manual CRUD.

---

## Assumptions
1. **Environment**: Python 3.10+ (detected Python 3.14 on local system) and Node.js v20+ / npm (detected Node v24.11 / npm 11.7 on local system).
2. **Database**: MongoDB connection string configured via `MONGODB_URI` environment variable (defaults to `mongodb://localhost:27017/creative_leaderboard` for local development, with seamless connection to MongoDB Atlas free M0 cluster in production). Includes an automatic in-memory / mock mode for testing and instant seed demonstration.
3. **Deployment**: Frontend deploys to Vercel as a Vite SPA with `vercel.json` rewrites. Backend deploys to Render free tier with `render.yaml` / standard web service configuration and `/api/health` keep-alive endpoint. No Docker required.
4. **Meta API**: Uses Meta Marketing API v18.0 with graceful token validation and mock fallback data when API credentials are not yet configured.

---

## Plan

### Step 1: Project Scaffolding & Configuration
- **Files**:
  - `backend/requirements.txt`
  - `backend/config.py`
  - `backend/.env.example`
  - `frontend/package.json`
  - `frontend/vite.config.ts`
  - `frontend/tsconfig.json`
  - `frontend/tailwind.config.js`
  - `frontend/postcss.config.js`
  - `frontend/index.html`
  - `frontend/vercel.json`
- **Change**:
  - Initialize FastAPI backend dependencies (`fastapi`, `uvicorn`, `motor`, `pydantic`, `pydantic-settings`, `httpx`, `apscheduler`, `pytest`, `pytest-asyncio`).
  - Initialize React 18 + TypeScript + Vite frontend with Tailwind CSS, Lucide icons, TanStack Query, React Router DOM, and Recharts.
  - Setup dark-first cyberpunk/gaming color palette tokens in Tailwind (slate-950 background, glowing emerald/gold/ruby/cyan accents).
  - Add `vercel.json` for client-side routing on Vercel.
- **Verify**:
  - Backend: `python -m pip install -r backend/requirements.txt` runs cleanly.
  - Frontend: `npm --prefix frontend install` runs cleanly.

---

### Step 2: Database Layer & Domain Schemas
- **Files**:
  - `backend/database.py`
  - `backend/models/client.py`
  - `backend/models/creative.py`
  - `backend/models/snapshot.py`
  - `backend/models/sync_log.py`
- **Change**:
  - Implement async Motor client connection manager with graceful reconnects and index creation (`client_id`, `date`, `creative_id`).
  - Define Pydantic v2 schemas:
    - `Client`: `id`, `name`, `meta_account_id`, `access_token`, `target_roas` (e.g. 2.5), `min_spend_threshold` (e.g. $100), `currency`, `timezone`, `created_at`.
    - `Creative`: `id`, `client_id`, `meta_creative_id`, `name`, `thumbnail_url`, `body_copy`, `headline`, `cta`, `status_override`, `notes`, `tags`, `first_seen_date`.
    - `DailySnapshot`: `creative_id`, `client_id`, `date` (YYYY-MM-DD), `spend`, `revenue`, `purchases`, `roas`, `ctr`, `cpa`, `impressions`, `clicks`, `rank`, `streak`, `status`.
    - `SyncLog`: `id`, `client_id`, `started_at`, `finished_at`, `status` (`SUCCESS`, `FAILED`), `records_synced`, `error_message`.
- **Verify**:
  - Python import test: `python -c "import backend.models.client, backend.models.creative, backend.models.snapshot; print('Models OK')"`

---

### Step 3: Status, Streak & Rank Movement Computation Engine
- **Files**:
  - `backend/services/leaderboard_service.py`
  - `backend/tests/test_status_and_streaks.py`
- **Change**:
  - Implement strict business logic for status classification:
    - `WIN`: Creative ROAS $\ge$ Client Target ROAS.
    - `LOSS`: Creative ROAS $<$ Client Target ROAS **AND** Creative Spend $\ge$ Client Minimum Spend Threshold.
    - `TESTING`: Creative Spend $<$ Client Minimum Spend Threshold (too early to judge).
    - `PAUSED`: Manual override or ad flagged inactive.
  - Implement streak calculation:
    - Positive flame streak (`🔥 +N` days) for consecutive days in `WIN` status.
    - Negative ice streak (`❄️ -N` days) for consecutive days in `LOSS` status.
    - Reset to 0 / 1 on status transition.
  - Implement rank movement engine:
    - Compare today's calculated rank vs. yesterday's immutable snapshot rank: `▲ +N` (climbed), `▼ -N` (dropped), `▬ 0` (unchanged), `NEW` (new creative).
  - Implement client portfolio aggregator: Blended Spend, Blended ROAS, Win/Loss/Testing counts, Best and Worst performing creatives.
  - Write comprehensive unit tests in `pytest`.
- **Verify**:
  - Run `pytest backend/tests/test_status_and_streaks.py -v` (100% pass).

---

### Step 4: Meta Marketing API Integration & Resilient Sync Engine
- **Files**:
  - `backend/services/meta_client.py`
  - `backend/services/sync_service.py`
  - `backend/services/scheduler.py`
  - `backend/tests/test_meta_sync.py`
- **Change**:
  - Implement async `MetaClient` using HTTPX:
    - Calls Meta Graph API v18.0 (`/act_{account_id}/insights`, `/adcreatives`, `/ads`).
    - Handles rate limiting headers (`x-business-use-case-usage`), exponential backoff, and pagination.
    - Provides `test_connection(account_id, access_token)` returning account validity, name, and permissions.
  - Implement `SyncService`:
    - Ingests daily insights, parses spend, purchase revenue, impressions, clicks, conversions.
    - Calculates ROAS, CTR, CPA.
    - Upserts/creates creative entities and writes immutable `DailySnapshot` documents for today's date.
    - Computes and assigns updated streaks and rank deltas.
    - Records structured `SyncLog` entries with error logging.
  - Implement `scheduler.py`:
    - Configures APScheduler background job running sync every 4 hours.
- **Verify**:
  - Run `pytest backend/tests/test_meta_sync.py -v`.

---

### Step 5: Bulk TSV/CSV Import & Manual CRUD Services
- **Files**:
  - `backend/services/import_service.py`
  - `backend/tests/test_bulk_import.py`
- **Change**:
  - Implement resilient CSV/TSV parser supporting standard Meta Ads Manager export formats:
    - Handles headers: Creative Name / Ad Name, Spend / Amount Spent, Purchases, Purchase ROAS / Conversion Value, CTR, Impressions, Link Clicks.
    - Flexible column auto-detection and number sanitization (currency symbols `$`, `,`, `%`).
    - Generates preview with validation errors before database commit.
    - Creates/updates creative and daily snapshot records with automated status and streak evaluation.
- **Verify**:
  - Run `pytest backend/tests/test_bulk_import.py -v`.

---

### Step 6: FastAPI REST API Endpoints & Seed Script
- **Files**:
  - `backend/main.py`
  - `backend/routers/leaderboard.py`
  - `backend/routers/clients.py`
  - `backend/routers/creatives.py`
  - `backend/routers/meta_sync.py`
  - `backend/routers/import_export.py`
  - `backend/routers/health.py`
  - `backend/scripts/seed_demo.py`
  - `backend/tests/test_api_endpoints.py`
- **Change**:
  - Assemble FastAPI application with CORS middleware, error handlers, and routers:
    - `GET /api/leaderboard`: Query with client, status, date range, min spend, search, sort.
    - `GET /api/leaderboard/podium`: Top 3 winning creatives.
    - `GET /api/clients`: All clients with blended performance cards.
    - `POST /api/clients`, `PUT /api/clients/{id}`, `DELETE /api/clients/{id}`.
    - `GET /api/creatives/{id}`: Creative details, 30-day historical snapshots, trendlines.
    - `POST /api/creatives`, `PUT /api/creatives/{id}`: Manual CRUD & status override.
    - `POST /api/meta/test-connection`: Live token check.
    - `POST /api/meta/sync/{client_id}` & `POST /api/meta/sync-all`: Manual sync triggers.
    - `GET /api/meta/logs`: Sync audit logs.
    - `POST /api/import/preview` & `POST /api/import/bulk-paste`: Bulk CSV/TSV ingestion.
    - `GET /api/health` & `GET /api/sync/cron`: Render keep-alive & external cron ping endpoint.
  - Implement `seed_demo.py` generating realistic multi-client performance data with 30-day snapshot histories, flame streaks, and rank movements.
- **Verify**:
  - Run `python -m backend.scripts.seed_demo`
  - Run `pytest backend/tests/test_api_endpoints.py -v` (100% pass).

---

### Step 7: Frontend Core Design System & UI Components
- **Files**:
  - `frontend/src/index.css`
  - `frontend/src/types/index.ts`
  - `frontend/src/api/client.ts`
  - `frontend/src/api/queries.ts`
  - `frontend/src/components/ui/Badge.tsx`
  - `frontend/src/components/ui/Button.tsx`
  - `frontend/src/components/ui/Card.tsx`
  - `frontend/src/components/ui/Dialog.tsx`
  - `frontend/src/components/ui/Input.tsx`
  - `frontend/src/components/ui/Select.tsx`
  - `frontend/src/components/ui/Slider.tsx`
  - `frontend/src/components/ui/Toast.tsx`
  - `frontend/src/components/layout/Navbar.tsx`
- **Change**:
  - Setup TypeScript definitions matching backend models.
  - Configure TanStack React Query provider and Axios/Fetch API client.
  - Build reusable game-leaderboard UI components with dark theme styling:
    - Status pills: `WIN` (neon emerald), `LOSS` (neon crimson/rose), `TESTING` (amber/cyan), `PAUSED` (slate/zinc).
    - Streak badge: `🔥 +X` (fire flame gradient) and `❄️ -X` (ice frost gradient).
    - Rank Delta badge: `▲ +N` (green up), `▼ -N` (red down), `▬ 0` (neutral grey), `NEW` (glowing purple).
    - Top 3 Podium Badges: Gold 🥇, Silver 🥈, Bronze 🥉 with metallic glow effects.
  - Build top navigation bar with quick client switcher, global sync trigger button, and route tabs.
- **Verify**:
  - Run `npm --prefix frontend run build` to verify clean TypeScript compilation.

---

### Step 8: Frontend Core Views Implementation
- **Files**:
  - `frontend/src/components/leaderboard/LeaderboardTable.tsx`
  - `frontend/src/components/leaderboard/LeaderboardFilters.tsx`
  - `frontend/src/components/leaderboard/PodiumTop3.tsx`
  - `frontend/src/pages/LeaderboardPage.tsx`
  - `frontend/src/components/clients/ClientCardsGrid.tsx`
  - `frontend/src/components/clients/ClientFormModal.tsx`
  - `frontend/src/pages/ClientsPage.tsx`
  - `frontend/src/components/creative/CreativeHeader.tsx`
  - `frontend/src/components/creative/CreativeTrendChart.tsx`
  - `frontend/src/components/creative/CreativeSnapshotTable.tsx`
  - `frontend/src/components/creative/CreativeEditModal.tsx`
  - `frontend/src/pages/CreativeDetailPage.tsx`
  - `frontend/src/components/meta-sync/MetaSyncSettings.tsx`
  - `frontend/src/components/meta-sync/SyncAuditLogsTable.tsx`
  - `frontend/src/pages/MetaSyncPage.tsx`
  - `frontend/src/components/import/BulkImportModal.tsx`
  - `frontend/src/pages/ClientSettingsPage.tsx`
  - `frontend/src/App.tsx`
- **Change**:
  - **Leaderboard Screen**:
    - High-density gaming leaderboard table with inline columns: Rank, Thumbnail preview, Creative Name, Client, Spend ($), ROAS, CTR (%), CPA ($), Days Live, Status Tag, Streak, Rank Movement vs. yesterday.
    - Top 3 animated podium cards.
    - Real-time multi-filter bar (Client selector, Status multi-select, Date Range, Min Spend slider, Search bar, Sort selector).
  - **Client View Screen**:
    - Portfolio grid showing Blended ROAS vs. Target ROAS, Total Spend, Win/Loss/Testing counts, and Best/Worst Creative.
    - 1-click filter interaction navigating to filtered leaderboard.
  - **Creative Detail Screen**:
    - High-res asset preview, copy, headline, and CTA.
    - 30-day interactive Recharts trendline chart (Daily ROAS, Spend, CPA with target ROAS reference line).
    - Historical daily snapshot log table.
    - Manual edit modal (notes, status override, tags).
  - **Meta Sync Settings Screen**:
    - Ad Account ID & Access Token form per client.
    - "Test Connection" button with instant diagnostic feedback.
    - Manual "Sync Now" button with progress spinner and toast notifications.
    - Sync audit log table with last sync timestamp, records count, and error viewer.
  - **Bulk Import Modal**:
    - Copy-paste TSV/CSV area with live column mapping preview, validation warnings, and instant save.
- **Verify**:
  - Run `npm --prefix frontend run build` to verify 0 build errors.

---

### Step 9: End-to-End Integration, Verification & Deployment Documentation
- **Files**:
  - `render.yaml`
  - `backend/Dockerfile` (optional fallback for non-native builds)
  - `frontend/vercel.json`
  - `README.md`
  - `walkthrough.md` (artifact)
- **Change**:
  - Validate full backend test suite (`pytest`).
  - Run full frontend production build (`npm run build`).
  - Start both backend and frontend servers and test end-to-end user workflows (ranking, filtering, streak tracking, manual edits, CSV import, client overview, Recharts rendering).
  - Create step-by-step deployment guide for Vercel ($0) + Render ($0) + MongoDB Atlas ($0).
- **Verify**:
  - All automated test suites pass: `pytest -v`
  - Clean frontend production build: `npm --prefix frontend run build`

---

## Risks & Mitigations
1. **Render Free Tier Spin-Down**:
   - *Mitigation*: Provide an on-demand manual "Sync Now" button directly on the UI and a lightweight `/api/sync/cron` ping endpoint compatible with free uptime monitors.
2. **MongoDB Atlas 512MB Ceiling**:
   - *Mitigation*: Lean snapshot schema storing only numeric performance attributes without redundant nested JSON payloads.
3. **Meta API Rate Limits & Token Expiration**:
   - *Mitigation*: Centralized HTTP client with exponential backoff, rate limit header detection, and a clear "Test Connection" token validation tool.

---

## Rollback Plan
- Each step is modularly contained in dedicated directories (`backend/` and `frontend/`).
- Database migrations are schema-less with Pydantic validation, allowing backward-compatible rollbacks without data corruption.
- Git checkpoints after each verified step ensure immediate revert capability if regressions arise.
