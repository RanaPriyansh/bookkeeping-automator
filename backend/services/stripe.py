"""
Stripe integration for subscription payments
"""

import stripe
from typing import Optional
from config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def create_customer(email: str, name: Optional[str] = None) -> stripe.Customer:
        return stripe.Customer.create(email=email, name=name)

    @staticmethod
    def create_checkout_session(
        customer_id: str, price_id: str, success_url: str, cancel_url: str
    ) -> stripe.checkout.Session:
        return stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
        )

    @staticmethod
    def retrieve_session(session_id: str) -> stripe.checkout.Session:
        return stripe.checkout.Session.retrieve(session_id)

    @staticmethod
    def create_billing_portal(customer_id: str, return_url: str) -> stripe.billing_portal.Session:
        return stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

    @staticmethod
    def construct_event(payload: bytes, signature: str) -> stripe.Event:
        return stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )
