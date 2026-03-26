"""
Stripe payment endpoints
"""

import logging
import stripe
from fastapi import APIRouter, HTTPException, Request
from services.database import Database
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

db = Database(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    """Create a Stripe checkout session for Pro subscription"""
    try:
        data = await request.json()
        email = data.get("email")

        if not email:
            raise HTTPException(status_code=400, detail="email is required")

        # Get or create user
        user = await db.get_user_by_email(email)
        if not user:
            user = await db.create_user(email)

        session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=["card"],
            line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.APP_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.APP_URL}/cancel",
        )

        return {"session_id": session.id, "url": session.url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout session error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    event_data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        customer_email = event_data.get("customer_email")
        subscription_id = event_data.get("subscription")
        if customer_email:
            user = await db.get_user_by_email(customer_email)
            if user:
                await db.update_user_subscription(
                    user_id=user["id"],
                    status="active",
                    stripe_subscription_id=subscription_id,
                )
                logger.info(f"Activated subscription for {customer_email}")

    elif event_type == "customer.subscription.deleted":
        subscription_id = event_data.get("id")
        if subscription_id:
            user = await db.get_user_by_subscription_id(subscription_id)
            if user:
                await db.update_user_subscription(
                    user_id=user["id"], status="canceled"
                )
                logger.info(f"Canceled subscription {subscription_id}")

    elif event_type == "customer.subscription.updated":
        subscription_id = event_data.get("id")
        new_status = event_data.get("status")  # active, past_due, canceled, etc.
        if subscription_id and new_status:
            user = await db.get_user_by_subscription_id(subscription_id)
            if user:
                db_status = "active" if new_status == "active" else "canceled"
                await db.update_user_subscription(
                    user_id=user["id"], status=db_status
                )
                logger.info(f"Updated subscription {subscription_id} → {db_status}")

    elif event_type == "invoice.payment_failed":
        subscription_id = event_data.get("subscription")
        if subscription_id:
            user = await db.get_user_by_subscription_id(subscription_id)
            if user:
                await db.update_user_subscription(
                    user_id=user["id"], status="past_due"
                )
                logger.warning(f"Payment failed for subscription {subscription_id}")

    return {"status": "ok"}
