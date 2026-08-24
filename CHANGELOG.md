# CHANGELOG

## 2026-08-24 (Update 3: Production Fresh State - Zero Demo Data)

### Changed
- **Database Initializer (`backend/database.py`)**: Removed automatic demo seeding on startup so deployed environments launch in a clean, production-ready state with 0 mock clients, 0 mock creatives, and 0 mock snapshots.
- **Frontend Empty States**:
  - `MetaSyncSettings.tsx`: Polished onboarding banner with a 1-click button to connect the first client account when 0 clients exist.
  - `PodiumTop3.tsx`: Graceful hiding when 0 creatives exist.
  - `ClientCardsGrid.tsx` & `LeaderboardTable.tsx`: Clean empty state messages for fresh account onboarding.

---

## 2026-08-24 (Update 2: Operator Security & Authentication)

### Added
- **Single-Operator Authentication Module**: Secure Email + Password Sign In dashboard guarding all internal screens and API endpoints.
- **Backend Auth Service (`backend/services/auth_service.py`)**:
  - Salted PBKDF2-HMAC-SHA256 password hashing (100,000 iterations).
  - Cryptographically signed JWT access token issuance and signature verification (`pyjwt`).
  - `get_current_admin` FastAPI security dependency guarding all operational routers.
  - Password hashing CLI helper `backend/scripts/hash_password.py`.
- **Backend Auth Router (`backend/routers/auth.py`)**:
  - `POST /api/auth/login`: Authenticates email and password, returning JWT bearer token.
  - `GET /api/auth/me`: Validates operator session.
- **Frontend Authentication Architecture**:
  - `AuthContext` & `AuthProvider` (`frontend/src/context/AuthContext.tsx`) for global token and session state persistence.
  - `ProtectedRoute` guard (`frontend/src/components/auth/ProtectedRoute.tsx`) redirecting unauthenticated visitors to `/login`.
  - Gaming dark-theme `LoginPage` (`frontend/src/pages/LoginPage.tsx`) with brand banner, password visibility toggle, and error states.
  - `Navbar` update with operator profile badge and 1-click Sign Out button.
  - Automatic `Authorization: Bearer <token>` header attachment and 401 interceptor in `frontend/src/api/client.ts`.
- **Test Suite**: 5 new authentication unit and endpoint tests in `backend/tests/test_auth.py` (17/17 pytest tests passing).

### Changed
- Protected `/api/clients`, `/api/creatives`, `/api/leaderboard`, `/api/meta`, and `/api/import` with `Depends(get_current_admin)`.
- Maintained public health access for `/api/health` and keep-alive ping for `/api/sync/cron` (protected by `X-Cron-Secret`).

---

## 2026-08-24 (Initial Release)

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
