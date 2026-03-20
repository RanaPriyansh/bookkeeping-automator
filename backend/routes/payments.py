"""
Stripe payment endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
import stripe
from services.database import Database
from ..config import settings

router = APIRouter()
db = Database(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    """Create Stripe checkout session"""
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email required")
        
        # Get or create user
        user = await db.get_user_by_email(email)
        if not user:
            user = await db.create_user(email)
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=["card"],
            line_items=[{
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{settings.APP_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.APP_URL}/cancel",
        )
        
        return {"session_id": session.id, "url": session.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")
        subscription_id = session.get("subscription")
        
        if customer_email:
            user = await db.get_user_by_email(customer_email)
            if user:
                await db.update_user_subscription(
                    user_id=user["id"],
                    status="active",
                    stripe_subscription_id=subscription_id
                )
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        # Find user by subscription ID and deactivate
        result = await db.client.table("users").select("id").eq("stripe_subscription_id", subscription["id"]).execute()
        if result.data:
            await db.update_user_subscription(result.data[0]["id"], "inactive")
    
    return {"status": "ok"}
