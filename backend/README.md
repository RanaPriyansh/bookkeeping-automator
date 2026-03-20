# Backend Template for AI SaaS Apps

## Architecture
FastAPI backend with:
- Claude API integration (Anthropic)
- Stripe subscription payments
- Supabase database (PostgreSQL)
- CORS configuration for iOS app
- Environment-based configuration

## Quick Start

1. Clone and install:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in:
```
ANTHROPIC_API_KEY=your_key
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_PRICE_ID=price_xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyxxx
SECRET_KEY=random_secret_here
```

3. Run locally:
```bash
uvicorn main:app --reload
```

4. Deploy to Vercel/Railway/Heroku:
- Push to GitHub
- Connect repository
- Set environment variables
- Deploy

## Template Structure

```
backend/
├── main.py              # FastAPI app
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── config.py           # Configuration loader
├── models.py           # Pydantic models
├── routes/
│   ├── generate.py    # AI generation endpoint
│   ├── payments.py    # Stripe webhooks/checkout
│   └── auth.py        # User auth (optional)
├── services/
│   ├── claude.py      # Claude API wrapper
│   ├── stripe.py      # Stripe integration
│   └── database.py    # Supabase client
└── utils/
    └── prompts.py     # AI prompts per app type
```

## Customizing for Each App

1. Update `models.py` with app-specific schemas
2. Modify `services/claude.py` prompt for your use case
3. Adjust `routes/generate.py` to handle your input/output
4. Update Stripe price ID and product name
5. Customize database tables in Supabase

## Stripe Subscription Flow

- `POST /create-checkout-session` → returns session ID
- Redirect client to Stripe-hosted checkout
- Webhook `/stripe-webhook` handles subscription events
- Update user's subscription status in database

## Claude API Prompt Engineering

Each app needs specialized prompts. Store in `utils/prompts.py`:

```python
PROMPTS = {
    'resume_builder': """You are an expert resume writer...""",
    'contract_generator': """You are a legal contract specialist...""",
    'finance_coach': """You are a certified financial planner...""",
}
```

## Deployment Targets

- **Vercel**: Serverless, easy Stripe integration
- **Railway**: Simple Docker deployment
- **Heroku**: Hobby tier free (with limits)
- **Fly.io**: Global edge deployment

## Monitoring & Logging

- Use `logging` module (structured logging)
- Sentry for error tracking (optional)
- Vercel/Railway built-in logs
- Stripe dashboard for payment metrics

## Cost Optimization

- Claude API: ~$0.015 per 1K tokens (Sonnet)
- Stripe: 2.9% + $0.30 per transaction
- Supabase: Free tier (500MB DB, 10K rows)
- Vercel: Free tier (100GB-hrs, unlimited bandwidth)

Break-even: ~100 subscribers at $9/mo = $900 MRR → $270/month API costs at 1M tokens/day

## License

MIT - Open source, use freely
