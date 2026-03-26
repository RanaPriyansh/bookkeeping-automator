# CLAUDE.md — Bookkeeping Automator

This document provides context for AI assistants working on this codebase.

---

## Project Overview

**Bookkeeping Automator** is an AI-powered iOS SaaS app that generates bookkeeping documents and financial content using Claude. It follows a freemium model (1 free generation, then paid subscription).

**Stack:**
- Backend: Python/FastAPI deployed on Vercel (serverless)
- AI: Anthropic Claude API (`claude-3-5-sonnet-20241022`)
- Database: Supabase (PostgreSQL)
- Payments: Stripe (web checkout) + RevenueCat (iOS in-app purchase)
- iOS: Swift/SwiftUI

---

## Repository Structure

```
bookkeeping-automator/
├── backend/                    # FastAPI Python backend
│   ├── routes/
│   │   ├── generate.py         # POST /api/v1/generate — main AI generation endpoint
│   │   └── payments.py         # Stripe checkout + webhook handlers
│   ├── services/
│   │   ├── claude.py           # Anthropic API wrapper
│   │   ├── database.py         # Supabase CRUD (users, generations)
│   │   └── stripe.py           # Stripe session/billing utilities
│   ├── utils/
│   │   └── prompts.py          # Prompt templates per use case
│   ├── config.py               # Pydantic settings (loaded from .env)
│   ├── main.py                 # FastAPI app init, CORS, route registration
│   ├── models.py               # Pydantic request/response models
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variable template
│   ├── vercel.json             # Vercel serverless deployment config
│   └── README.md               # Backend-specific documentation
├── iOS/
│   └── BookkeepingAutomator/
│       ├── Views/
│       │   ├── ContentView.swift     # Main generation UI
│       │   ├── OnboardingView.swift  # First-run onboarding
│       │   └── PaywallView.swift     # Subscription upgrade screen
│       ├── Services/
│       │   ├── APIClient.swift       # HTTP client for backend API
│       │   └── StoreManager.swift    # RevenueCat subscription management
│       └── AIApp.swift               # App entry point
├── README.md                   # Project overview and setup guide
├── DEPLOYMENT.md               # Deployment steps for backend and iOS
└── TODO.md                     # Agent protocol and priority tasks
```

---

## Development Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env            # Fill in all required values
uvicorn main:app --reload       # Runs on http://localhost:8000
```

API docs available at: `http://localhost:8000/docs`

### Required Environment Variables

See `backend/.env.example`. The critical ones:

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API access |
| `STRIPE_SECRET_KEY` | Stripe backend operations |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature verification |
| `SUPABASE_URL` | Database connection |
| `SUPABASE_KEY` | Supabase service role key |
| `SECRET_KEY` | App-level secret (JWT/signing) |

### iOS

Open `iOS/BookkeepingAutomator.xcodeproj` in Xcode. Update the `baseURL` in `Services/APIClient.swift` to point to your backend URL before building.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check — returns `{"status": "ok"}` |
| POST | `/api/v1/generate` | Generate AI content (freemium gated) |
| POST | `/api/v1/create-checkout-session` | Create Stripe checkout session |
| POST | `/api/v1/stripe-webhook` | Receive Stripe events |

---

## Key Conventions

### Backend

- **Settings** are managed via `backend/config.py` using Pydantic `BaseSettings`. Access via `from config import settings`.
- **Models** for request/response validation live in `backend/models.py`. Add new models there — do not define inline.
- **Prompts** for each use case (resume builder, contract generator, finance coach, etc.) are defined in `backend/utils/prompts.py`. The `get_prompt(template_name, **kwargs)` function returns formatted prompts.
- **Claude calls** go through `services/claude.py`. Use `generate()` for plain text, `generate_with_json()` when structured output is needed.
- **Database operations** go through `services/database.py`. The Supabase client is initialized once at startup via `lifespan` in `main.py`.
- **Error handling**: Raise `HTTPException` with appropriate status codes. Do not swallow exceptions silently.
- **CORS**: Configured in `main.py` to allow iOS app and web origins. Update `allow_origins` when adding new deployment targets.

### iOS

- `StoreManager.swift` handles all subscription state. Check `StoreManager.shared.isSubscribed` before allowing premium actions.
- `APIClient.swift` sends `user_email` and `is_subscribed` with every generation request. The backend uses `is_subscribed` to bypass the free-tier limit.
- The paywall (`PaywallView`) is presented when `APIClient` receives a 403 indicating the free limit is reached.
- RevenueCat product ID: `bookkeeping_pro_monthly` (configure in RevenueCat dashboard).

### Freemium Model

- Free users: **1 generation** max (`maxFreeGenerations = 1` in `APIClient.swift`)
- Tracked server-side in Supabase `users.generations_used` column
- SQL function `increment_generations(user_id UUID)` atomically increments the counter
- When limit is hit, backend returns 403; iOS presents `PaywallView`

---

## Database Schema

```sql
-- users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    stripe_customer_id TEXT,
    subscription_status TEXT DEFAULT 'free',  -- 'free' | 'active' | 'canceled'
    generations_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- generations table
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    template_type TEXT,
    input_data JSONB,
    output_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- atomic increment function
CREATE OR REPLACE FUNCTION increment_generations(user_id UUID)
RETURNS void AS $$
    UPDATE users SET generations_used = generations_used + 1 WHERE id = user_id;
$$ LANGUAGE sql;
```

---

## Known Issues and Gaps

These are existing gaps to be aware of — fix them when touching related code:

1. **Missing `utils/logging.py`**: `main.py` imports `from utils.logging import setup_logging` but this file does not exist. The app will fail to start until this is created or the import is removed.
2. **Missing `__init__.py` files**: `routes/`, `services/`, and `utils/` have no `__init__.py`. Add them if module imports break.
3. **No `.gitignore`**: The repository has no `.gitignore`. Create one to exclude `.env`, `__pycache__/`, `*.pyc`, `.DS_Store`, `*.xcuserdata`, etc.
4. **Hardcoded `baseURL` in iOS**: `APIClient.swift` has a placeholder URL. Must be updated before iOS builds will work against a real backend.
5. **Price inconsistency**: `PaywallView.swift` shows `$9.99/month` but `README.md` mentions `$19/month`. Align these.
6. **Missing `settings.APP_URL`**: `payments.py` references `settings.APP_URL` which is not defined in `config.py`. Add it or replace with a concrete value.
7. **No tests**: There is zero test coverage. Any new features should include at least a basic smoke test.
8. **No CI/CD**: No GitHub Actions or other pipeline exists. Consider adding one for linting and tests.

---

## Prompt Templates

Available in `backend/utils/prompts.py`:

| Template Key | Description |
|---|---|
| `resume_builder` | Generates professional resume content |
| `contract_generator` | Drafts legal/business contracts |
| `finance_coach` | Provides financial planning advice |
| `teacher_assistant` | Generates educational content |
| `landlord_utility` | Rental/property management documents |

To add a new template: add an entry to the `PROMPTS` dict in `prompts.py` with `system` and `template` keys.

---

## Deployment

### Backend (Vercel)

```bash
cd backend
vercel deploy --prod
```

`vercel.json` routes all requests to `main.py` as a serverless function. Set all environment variables in the Vercel project dashboard.

### iOS

1. Set bundle ID: `com.appfactory.bookkeepingautomator`
2. Configure RevenueCat with your API key in `AIApp.swift`
3. Update `baseURL` in `APIClient.swift` to your production backend URL
4. Archive and submit via Xcode / App Store Connect

See `DEPLOYMENT.md` for the full step-by-step guide.

---

## Agent Protocol (from TODO.md)

When starting a session on this repo:

1. Pull latest changes from the active branch
2. Validate the environment (check `.env` is populated, dependencies installed)
3. Confirm the app starts (`uvicorn main:app`)
4. Work in small, committed increments
5. Update `TODO.md` when tasks are completed or new blockers are found

**Definition of done for any task:**
- A fresh clone can reproduce the feature in under 5 minutes
- The highest-leverage blocker is addressed
- `README.md` and `TODO.md` reflect current reality
