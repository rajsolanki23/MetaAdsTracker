# Superpowers Brainstorm: Creative Leaderboard for Performance Marketing

## Goal
Build a 100% free-tier, open-source web application called **Creative Leaderboard** for a solo performance marketing operator managing multiple client ad accounts. The application reimagines Meta ad creative performance tracking as a gamified, real-time leaderboard instead of a slow, clunky spreadsheet. It provides instant creative ranking, automated performance classification (`WIN`, `LOSS`, `TESTING`, `PAUSED`), streak tracking, rank movement deltas vs. yesterday, client-level blended metrics, interactive trend analysis, resilient 4-hour scheduled & on-demand Meta Marketing API synchronization with immutable daily snapshots, manual CRUD, and fallback bulk paste CSV/TSV importing.

### Zero-Cost Stack Architecture
| Layer | Tool | Hosting / Tier | Cost |
| :--- | :--- | :--- | :--- |
| **IDE** | Antigravity | Local | Free |
| **AI** | Gemini 3.7 Flash | Google AI | Free |
| **Backend** | FastAPI (Python) | Render (Web Service Free Tier) | Free |
| **Frontend** | React (Vite + TypeScript) | Vercel (Hobby Free Tier) | Free |
| **Database** | MongoDB | MongoDB Atlas (M0 Free 512MB) | Free |
| **Total** | | | **$0/month** |

---

## Constraints
1. **Zero-Cost Deployment Constraints**:
   - **Frontend (Vercel)**: Static build output (`dist/`) with SPA rewrites (`vercel.json`), zero serverless lambda bloat, client-side caching with TanStack React Query.
   - **Backend (Render Free Tier)**: Standard web service with health check endpoint (`/api/health`) to support keep-alive pings if needed, lean memory footprint (<512MB RAM), robust startup connection handling.
   - **Database (MongoDB Atlas M0 Free Tier)**: 512MB storage ceiling requires lean document schemas, indexed queries (`client_id`, `date`, `creative_id`), and efficient snapshot storage without redundant blob payloads.
2. **Core Tech Stack**:
   - **Frontend**: React 18+ with TypeScript, Vite, Tailwind CSS + shadcn/ui design patterns, Lucide icons, TanStack React Query for server state, Recharts for trend visualization.
   - **Backend**: FastAPI (Python 3.10+), Pydantic v2 validation models, APScheduler for scheduled background sync tasks, HTTPX for resilient async Meta Graph API calls.
   - **Database**: MongoDB (async Motor driver + PyMongo), storing clients, ad credentials, creative metadata, immutable daily performance snapshots, and sync audit logs.
3. **Design & Gamification Aesthetics**:
   - Gamified leaderboard aesthetics: sleek dark theme, high information density, top 3 podium/trophy badges (🥇 🥈 🥉), streak flame indicators (`🔥 Xd`), rank movement delta badges (`▲ +N`, `▼ -N`, `▬ 0`, `NEW`), status tags (`WIN`, `LOSS`, `TESTING`, `PAUSED`).
   - Zero buried information: key metrics (Spend, ROAS, CTR, CPA, Days Live, Streak, Rank Change) accessible directly in the primary leaderboard view without requiring drill-downs.
4. **Data Integrity & Compliance**:
   - Never overwrite daily historical snapshots: daily snapshots remain immutable to calculate streaks, rank deltas, and multi-day trend graphs accurately.
   - Meta Graph API rate limit resilience: exponential backoff, rate limit header inspection (`x-business-use-case-usage`), and secure token handling.
   - Offline / Standalone operability: full manual entry and bulk TSV/CSV paste import so the operator can use the dashboard even without live Meta credentials.

---

## Known Context
- **Operator Workflow**: Performance marketers evaluate tens to hundreds of ad creatives daily across multiple client accounts. Traditional tools (Meta Ads Manager, Google Sheets) require frequent page loads, multi-level dropdowns, and manual formula updates to answer: *"Which creative is winning today? Which creative is bleeding cash? How long has this creative stayed on top?"*
- **Deployment Compatibility**: Both Render (Docker or native Python runtime) and Vercel (Vite SPA deployment) integrate seamlessly with GitHub repositories, and MongoDB Atlas provides standard M0 connection strings (`mongodb+srv://...`).

---

## Risks
1. **Render Free Tier Spin-Down / Sleep Behavior**:
   - *Risk*: Render free web services spin down after 15 minutes of inactivity, which can delay requests by 30-50s on initial wake-up and pause in-process APScheduler background cron tasks while sleeping.
   - *Mitigation*: 
     1. Build an on-demand "Sync Now" button on the frontend that triggers an immediate refresh whenever the operator opens the dashboard.
     2. Support standard webhook / cron ping trigger endpoint (`/api/sync/cron`) callable by free uptime monitors (e.g. Cron-Job.org / UptimeRobot) to both keep the backend awake and guarantee exact 4-hour sync intervals.
2. **MongoDB Atlas 512MB Free Tier Capacity**:
   - *Risk*: Continuous daily snapshots across hundreds of creatives over months could eventually grow storage.
   - *Mitigation*: Optimized snapshot schema storing only essential daily metrics (~200 bytes per record; 100 creatives * 365 days = ~7.3MB/year, easily fitting within 512MB for years). Exclude raw uncompressed JSON responses from permanent snapshot storage.
3. **Meta Graph API Rate Limiting & Token Invalidation**:
   - *Risk*: Multiple client accounts syncing simultaneously or querying dense Insights breakdowns triggering Meta API rate limits or token expiration.
   - *Mitigation*: Centralized async HTTP client with jittered exponential backoff, sequential per-account syncing, granular error logging with diagnostic UI alerts, and "Test Connection" token verification.
4. **Dynamic Ranking & Streak Calculation Drift**:
   - *Risk*: Calculating streaks and rank movements on-the-fly across large datasets without stable snapshot references causing performance lag or inconsistent streak history.
   - *Mitigation*: Persist formal `DailySnapshot` documents per creative per calendar day. Compute yesterday's rank and current streak based on continuous historical daily records with indexed queries.

---

## Options (2–4)

### Option 1: Decoupled Fullstack (Vercel SPA + Render FastAPI Web Service + MongoDB Atlas M0) — **(Recommended)**
- **Summary**: Deploy React Vite frontend to Vercel (free, global edge CDN), FastAPI backend to Render free tier, and database to MongoDB Atlas M0 (512MB free).
- **Pros**:
  - Exactly matches the specified $0/month zero-cost stack.
  - Vercel provides instant edge delivery, automatic SSL, and zero cold-start for the frontend UI.
  - FastAPI on Render provides full Python async capabilities, APScheduler, and HTTPX Meta API integrations.
  - MongoDB Atlas provides production-grade managed cloud database with SSL and automated backups.
  - Fully runnable locally via `docker-compose` or local dev servers (`npm run dev` + `uvicorn`).
- **Cons**:
  - Render free tier spins down after inactivity (mitigated via on-demand sync and ping trigger).
- **Complexity / Risk**: Low complexity, optimal architecture for solo operator performance and zero monthly cost.

### Option 2: Monolithic Single Container on Render Free Tier
- **Summary**: FastAPI backend serves pre-built React static files directly from a single Render web service.
- **Pros**: Single deployment target on Render.
- **Cons**: Frontend UI also gets blocked by Render's 30-50s cold start when sleeping; loses Vercel's global CDN and instant edge delivery.
- **Complexity / Risk**: Low, but worse user experience on wake-up compared to Option 1.

### Option 3: Serverless Functions on Vercel (Next.js / Python API routes)
- **Summary**: Replatform backend to Vercel Serverless Functions.
- **Pros**: Unified single-platform deployment on Vercel.
- **Cons**: Serverless execution limits (10s timeout on free tier) make multi-account Meta API pagination and scheduled background sync loops brittle and prone to timeout failures.
- **Complexity / Risk**: High risk of timeouts and sync failures.

---

## Recommendation
**Adopt Option 1 (Decoupled Fullstack: React 18+ Vite on Vercel + FastAPI on Render + MongoDB Atlas M0).**

This architecture achieves 100% free-tier zero monthly cost, instant frontend loading via Vercel CDN, secure and centralized Meta API synchronization via FastAPI on Render, robust cloud persistence on MongoDB Atlas, and seamless local development.

---

## Acceptance Criteria

### 1. Leaderboard & Gamification Engine
- [ ] **Rankings Table**: Displays rank (#1, #2, #3 badges/trophies, #4+ numbers), creative preview thumbnail, creative headline/name, client badge, spend ($), ROAS, CTR (%), CPA ($), days live, status pill, streak counter (`🔥 Xd`), and 24h rank movement indicator (`▲ +N`, `▼ -N`, `▬ 0`, `NEW`).
- [ ] **Dynamic Sorting**: Instant 1-click sorting by ROAS, Spend, CTR, CPA, Days Live, Streak, and Rank Delta.
- [ ] **Status Automation Rules**:
  - `WIN`: Creative ROAS $\ge$ Client Target ROAS.
  - `LOSS`: Creative ROAS $<$ Client Target ROAS **AND** Creative Spend $\ge$ Client Minimum Spend Threshold.
  - `TESTING`: Creative Spend $<$ Client Minimum Spend Threshold.
  - `PAUSED`: Creative marked as inactive/paused in Meta or manually toggled.
- [ ] **Top 3 Visual Podiums**: Highlighted gold/silver/bronze styling with vibrant glowing accents.
- [ ] **Interactive Filters**: Quick filtering by Client, Status (`WIN`, `LOSS`, `TESTING`, `PAUSED`), Date Range (Today, Yesterday, Last 7D, Last 30D, All Time), and search by creative name/tag.

### 2. Client View & Portfolio Health
- [ ] **Client Cards Grid**: Summarizes each client with Blended Spend, Blended ROAS vs. Target ROAS, Win/Loss/Testing creative counts, Active Creatives count, and overall account health status badge.
- [ ] **Direct Filter Integration**: Clicking a client card instantly focuses the Leaderboard on that client's creative roster.

### 3. Creative Detail & Analytics
- [ ] **Asset Preview**: Displays creative image/video thumbnail, ad copy, headline, CTA, and creative ID.
- [ ] **Historical Performance Chart**: Interactive Recharts time-series chart showing Daily ROAS, Spend, and CPA trends over time with target ROAS reference line.
- [ ] **Daily Snapshot Log**: Tabular breakdown of historical daily metrics for that creative.
- [ ] **Manual Override**: Allows operator to set manual status (`PAUSED`, custom notes, tags).

### 4. Meta Marketing API Sync & Settings
- [ ] **Account Connection Form**: Per-client configuration of Meta Ad Account ID (`act_XXXXXX`), Access Token, and Target/Min Spend thresholds.
- [ ] **Token Validation & Diagnostics**: "Test Connection" button verifying permissions against Meta Graph API `/me` or `/act_<ID>`.
- [ ] **Manual & Scheduled Ingestion**:
  - Manual "Sync Now" button with immediate progress and success/error feedback.
  - Background scheduler / cron endpoint running every 4 hours fetching insights for all active client accounts.
- [ ] **Immutable Snapshots**: Each sync saves/updates today's snapshot while preserving previous calendar days.
- [ ] **Sync Audit Log**: Displays timestamp of last sync, status (Success/Failed), records updated, and error messages.

### 5. Fallback Bulk Paste & Manual Operations
- [ ] **Bulk Paste Modal**: Allows pasting CSV/TSV data directly from Meta Ads Manager export, parsing columns (Creative Name, Spend, Purchases, Revenue/Value, Clicks, Impressions), and importing instantly into MongoDB.
- [ ] **Manual Add/Edit Modal**: Form to manually add or edit a creative for offline tracking or mock testing.

### 6. Client Settings Management
- [ ] **Client Management**: Create, edit, and archive clients with Target ROAS, Minimum Spend threshold, currency, and timezone.

### 7. Deployment & Configuration Readiness ($0/month)
- [ ] **Backend Configuration**: Production-ready FastAPI app with CORS configured for Vercel domains, MongoDB Atlas connection handling, `/api/health` keep-alive endpoint, and `render.yaml` / Dockerfile for Render free-tier deployment.
- [ ] **Frontend Configuration**: Vite configuration with `vercel.json` SPA routing rewrites, environment variable bindings (`VITE_API_URL`), and responsive dark-mode styling.
- [ ] **Seed & Test Suite**: Pytest test suite validating status classification, streak logic, and API endpoints, plus a rich demo seed script (`python -m backend.scripts.seed_demo`) for instant local or cloud testing.
