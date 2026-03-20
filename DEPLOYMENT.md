# Deploying AI Bookkeeping Automator

## Backend (One-time)
1. Create Stripe product and price ($19/month)
2. Create Supabase database (users, generations tables)
3. Deploy backend to Vercel/Railway
4. Set webhook endpoint in Stripe dashboard

## iOS App
1. Open Xcode project in iOS/BookkeepingAutomator/
2. Set bundle identifier: com.thielon.bookkeepingautomator
3. Add RevenueCat API key
4. Configure App Store Connect entry
5. Build and submit for review
6. Release to TestFlight first

## RevenueCat Setup
- Create entitlement: "premium"
- Create product: "AI Bookkeeping Automator" ($19/mo)
- Add to configurations in Xcode

## Database Schema
Run in Supabase SQL editor:

CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    stripe_customer_id TEXT,
    subscription_status TEXT DEFAULT 'inactive',
    generations_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE generations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    input_text TEXT,
    output_text TEXT,
    app_type TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE FUNCTION increment_generations(user_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE users SET generations_used = generations_used + 1 WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;
