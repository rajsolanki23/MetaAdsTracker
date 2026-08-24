# CHANGELOG

## 2026-08-24

### Added
- **Creative Leaderboard Application**: Full-stack, 100% open-source web application for performance marketing operators on a $0/month stack (React + TypeScript + Vite + FastAPI + Motor MongoDB + Vercel + Render + MongoDB Atlas).
- **Gamified Leaderboard & Podium View**: Interactive rankings table displaying rank (#1 Gold 🥇, #2 Silver 🥈, #3 Bronze 🥉), thumbnail, creative name, client badge, spend, ROAS, CTR, CPA, days live, status tag, streak, and rank movement vs. yesterday.
- **Automated Status & Streak Engine**:
  - `WIN`: ROAS $\ge$ client target.
  - `LOSS`: ROAS $<$ client target AND spend $\ge$ client minimum spend threshold.
  - `TESTING`: spend $<$ client minimum spend threshold.
  - `PAUSED`: manual status override.
  - `Streak`: Positive flame streak (`🔥 +Xd`) and negative ice streak (`❄️ -Xd`).
  - `Rank Movement`: Comparison against yesterday's immutable snapshot (`▲ +N`, `▼ -N`, `▬ 0`, `NEW`).
- **Client Portfolio View**: Cards displaying blended ROAS vs. target, total spend, revenue, win/loss breakdown bar, and 1-click filter navigation.
- **Creative Detail & Recharts Trendline**: 30-day interactive time-series chart comparing Daily ROAS vs. Target ROAS, Daily Spend ($), and CPA ($) with custom tooltip and historical daily snapshots table.
- **Meta Marketing API Integration (v18.0)**: Centralized async HTTPX client with rate limit backoff, 4-hour background scheduler via APScheduler, live token connection testing, and sync audit log tracking.
- **Bulk CSV/TSV Paste Import**: Backup import modal supporting copied cells from Meta Ads Manager table exports with auto-column mapping and validation preview before database commit.
- **Manual CRUD**: Add and edit creative entries, notes, tags, and status overrides independent of Meta sync.
- **Demo Seed Generator**: Rich seed script (`python -m backend.scripts.seed_demo`) generating 3 realistic clients, 13 ad creatives with high-res thumbnails, and 30 days of immutable snapshots.
- **Deployment Configs**: `render.yaml` for Render free tier web service and `frontend/vercel.json` for Vercel SPA routing.

### Impacted Modules
- `backend/` (FastAPI REST API, Motor DB, APScheduler, HTTPX Meta Client, Pytest suite)
- `frontend/` (React 18 + TypeScript + Vite, Tailwind CSS, TanStack Query, Recharts, Lucide React)

### APIs Changed / Added
- `GET /api/health`
- `GET /api/sync/cron`
- `GET /api/leaderboard`
- `GET /api/leaderboard/podium`
- `GET /api/clients`, `POST /api/clients`, `GET /api/clients/{id}`, `PUT /api/clients/{id}`, `DELETE /api/clients/{id}`
- `GET /api/creatives/{id}`, `POST /api/creatives`, `PUT /api/creatives/{id}`, `GET /api/creatives/{id}/snapshots`, `GET /api/creatives/{id}/trend`
- `POST /api/meta/test-connection`, `POST /api/meta/sync/{client_id}`, `POST /api/meta/sync-all`, `GET /api/meta/logs`
- `POST /api/import/preview`, `POST /api/import/bulk-paste`

### Migration Requirements
- None (Initial setup).

### Breaking Changes
- None.

### Notes
- All 12 automated unit/integration tests in Pytest pass cleanly.
- Frontend builds cleanly in `frontend/dist/` without errors.
