# AI Bookkeeping Automator

[![GitHub](https://img.shields.io/badge/GitHub-000000?logo=github)](https://github.com/RanaPriyansh/bookkeeping-automator)
[![License](https://img.shields.io/github/license/RanaPriyansh/bookkeeping-automator)](https://github.com/RanaPriyansh/bookkeeping-automator/blob/main/LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/RanaPriyansh/bookkeeping-automator)](https://github.com/RanaPriyansh/bookkeeping-automator/commits/main)

AI-powered bookkeeping automator for iOS.

## Features
- AI generation using Claude API
- Stripe subscription payments ($19/month)
- Freemium model: 1 free generation
- PDF export (coming soon)

## Setup
1. Copy `.env.example` to `.env` and fill in your API keys
2. Run: `pip install -r requirements.txt`
3. Run: `uvicorn main:app --reload`
4. Open http://localhost:8000/docs for API docs

## Deployment
Deploy to Vercel, Railway, or Heroku. Set all environment variables.

## App Store
iOS app template: iOS/BookkeepingAutomator/
Configure bundle ID: com.appfactory.bookkeepingautomator
Set RevenueCat product: AI Bookkeeping Automator

## Revenue
- Freemium: 1 free generation
- Pro: $19/month
- Target: 100+ subscribers in first month = $1900/mo
