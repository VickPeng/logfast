# LogFast — AI Changelog Generator

> Never write a changelog by hand again. LogFast reads your Git commits, uses AI to understand what changed, and generates customer-ready changelogs in seconds.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Vue 3 + Vite + TailwindCSS |
| Backend | Python FastAPI |
| Database | PostgreSQL (via Supabase / asyncpg) |
| AI | DeepSeek / OpenAI-compatible API |
| Auth | GitHub OAuth |
| Payments | Lemon Squeezy |

## Quick Start

### 1. Backend

```bash
cd backend
cp .env.example .env   # Edit with your GitHub OAuth + AI API keys
pip install -r requirements.txt
python run.py           # Starts at http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev             # Starts at http://localhost:5173
```

### 3. Database

```bash
# Using Supabase (recommended):
# Set DATABASE_URL to your Supabase PostgreSQL connection string
# Tables are auto-created on first run

# Or local PostgreSQL:
createdb logfast
# Update DATABASE_URL in .env
```

## GitHub OAuth Setup

1. Go to https://github.com/settings/developers
2. Create a new OAuth App
3. Set callback URL to: `http://localhost:8000/api/auth/github/callback`
4. Copy Client ID and Secret to `.env`

## AI API Setup

Get an API key from [DeepSeek](https://platform.deepseek.com/) or any OpenAI-compatible provider. Set `AI_API_KEY` in `.env`.

## Project Structure

```
logfast/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Settings from env
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── database.py      # DB connection
│   │   ├── routes/
│   │   │   ├── auth.py      # GitHub OAuth
│   │   │   ├── changelog.py # Repo + changelog CRUD
│   │   │   └── webhook.py   # GitHub push webhook
│   │   └── services/
│   │       ├── github.py    # GitHub API client
│   │       └── ai.py        # AI changelog generation
│   ├── run.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── views/
    │   │   ├── LandingPage.vue
    │   │   ├── AuthCallback.vue
    │   │   ├── Dashboard.vue
    │   │   ├── ChangelogPage.vue
    │   │   └── PublicChangelog.vue
    │   └── stores/
    │       ├── auth.js
    │       └── repos.js
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## MVP Feature Checklist

- [x] GitHub OAuth sign-in
- [x] List user repos + connect/disconnect
- [x] Fetch commits from connected repos
- [x] AI changelog generation (DeepSeek)
- [x] Draft/publish workflow
- [x] Public changelog page (`/p/:owner/:repo`)
- [x] GitHub push webhook (auto-generate)
- [ ] Email subscriber notifications
- [ ] In-app widget embed
- [ ] Custom domain support
- [ ] Gitee / Coding.net support
- [ ] Chinese localization
- [ ] Lemon Squeezy payments
