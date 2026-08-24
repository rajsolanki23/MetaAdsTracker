# 🏆 Creative Leaderboard

> **The Gamified Meta Ad Creative Performance Dashboard for Performance Marketers**  
> Rank ad creatives like a live leaderboard instead of a slow, clunky spreadsheet. 100% Open Source • **$0/month Zero-Cost Stack**.

---

## ⚡ Zero-Cost Architecture ($0/month)

| Layer | Technology | Hosting / Service | Cost |
| :--- | :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind, Recharts | **Vercel** (Hobby Free Tier) | **$0** |
| **Backend** | FastAPI, Python 3.10+, Motor, APScheduler, HTTPX | **Render** (Web Service Free Tier) | **$0** |
| **Database** | MongoDB (Async Motor driver) | **MongoDB Atlas** (M0 Free 512MB) | **$0** |
| **Meta API** | Marketing Graph API v18.0 | Meta for Developers | **$0** |
| **Total** | | | **$0/month** |

---

## 🎮 Core Features

- **🏆 Gamified Leaderboard**: Instant visual ranking (#1 Gold 🥇, #2 Silver 🥈, #3 Bronze 🥉).
- **📊 Inline Metrics**: Spend, ROAS, CTR (%), CPA ($), Days Live, Status Pill, Streak, Rank Movement vs. yesterday.
- **🔥 Flame & ❄️ Ice Streaks**: Automatic tracking of consecutive winning days (`🔥 +Xd`) and losing days (`❄️ -Xd`).
- **▲ Rank Movement**: Real-time delta comparison against yesterday's immutable daily snapshot (`▲ +2`, `▼ -1`, `▬ 0`, `NEW`).
- **🎯 Automated Status Rules**:
  - `WIN`: Creative ROAS $\ge$ Client Target ROAS.
  - `LOSS`: Creative ROAS $<$ Client Target ROAS **AND** Spend $\ge$ Client Minimum Spend Threshold.
  - `TESTING`: Spend $<$ Minimum Spend Threshold (too early to judge).
  - `PAUSED`: Manually paused or flagged inactive in Meta.
- **📈 30-Day Interactive Trendlines**: Interactive Recharts time-series chart of Daily ROAS, Spend, and CPA with Target ROAS reference lines.
- **🏢 Client Portfolio Health**: Blended ROAS, total spend, win/loss breakdowns, best & worst creative highlights, and 1-click filtering.
- **🔄 Resilient Meta Marketing API Sync**: Ingests daily insights every 4 hours via APScheduler + on-demand manual triggers with token testing.
- **📋 Bulk Paste Import**: Copy-paste CSV/TSV table exports from Ads Manager with live preview and validation for offline backups.
- **🛡️ Immutable Snapshots**: Historical daily performance records are preserved forever for accurate streak and rank movement auditing.

---

## 🚀 Quick Start (Local Development)

### 1. Backend Setup (FastAPI)

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. (Optional) Run tests
pytest backend/tests/ -v

# 3. (Optional) Seed realistic demo data
python -m backend.scripts.seed_demo

# 4. Start the FastAPI server (runs on http://127.0.0.1:8000)
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup (React + Vite)

```bash
# 1. Navigate to frontend & install packages
cd frontend
npm install

# 2. Start Vite dev server (runs on http://localhost:5173)
npm run dev
```

Visit **http://localhost:5173** to view the live dashboard!

---

## ☁️ Zero-Cost Deployment Guide ($0/Month)

### 1. Database: MongoDB Atlas M0 (Free 512MB)
1. Sign up for free at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a free **M0 Sandbox Cluster**.
3. Under **Database Access**, create a database user and password.
4. Under **Network Access**, add `0.0.0.0/0` (allow all IP addresses).
5. Copy your connection string: `mongodb+srv://<username>:<password>@cluster0.xxxx.mongodb.net/creative_leaderboard?retryWrites=true&w=majority`.

### 2. Backend: Render Free Web Service ($0)
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New > Web Service**.
3. Connect your repository and configure:
   - **Root Directory**: Leave blank (repo root)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. Add Environment Variables:
   - `MONGODB_URI`: Your MongoDB Atlas connection string.
   - `DATABASE_NAME`: `creative_leaderboard`
   - `CORS_ORIGINS`: `https://your-frontend.vercel.app,http://localhost:5173`
   - `CRON_SECRET`: Random secure string (e.g. `leaderboard-cron-key-123`)
5. Deploy! Note your Render service URL (e.g. `https://creative-leaderboard.onrender.com`).

> **Tip for Render Sleep Prevention**: Free web services sleep after 15 min of inactivity. Use [Cron-Job.org](https://cron-job.org) (100% free) to ping `https://creative-leaderboard.onrender.com/api/sync/cron` every 10–15 minutes with header `X-Cron-Secret: leaderboard-cron-key-123`. This keeps the service awake and triggers exact periodic syncs!

### 3. Frontend: Vercel Free Hobby Tier ($0)
1. Sign in to [Vercel](https://vercel.com) and click **Add New > Project**.
2. Select your repository.
3. In **Build & Output Settings**:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. In **Environment Variables**:
   - `VITE_API_URL`: `https://creative-leaderboard.onrender.com/api`
5. Click **Deploy**!

---

## 🧪 Testing

Run backend unit and integration test suite:

```bash
python -m pytest backend/tests/ -v
```

Run frontend typecheck and production build verification:

```bash
npm --prefix frontend run build
```

---

## 📄 License
MIT License • 100% Open Source.
