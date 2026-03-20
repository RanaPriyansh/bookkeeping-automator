"""
Supabase database service
"""

from supabase import create_client, Client
from typing import Optional, Dict, Any, List
from .config import settings

class Database:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client: Optional[Client] = None
    
    async def connect(self):
        """Connect to Supabase"""
        self.client = create_client(self.url, self.key)
        print("✓ Connected to Supabase")
    
    async def disconnect(self):
        """Disconnect from Supabase"""
        self.client = None
    
    async def create_user(self, email: str, stripe_customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user"""
        data = {
            "email": email,
            "stripe_customer_id": stripe_customer_id,
            "subscription_status": "inactive",
            "generations_used": 0
        }
        result = self.client.table("users").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        result = self.client.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    async def update_user_subscription(self, user_id: str, status: str, stripe_subscription_id: str = None):
        """Update user subscription status"""
        data = {"subscription_status": status}
        if stripe_subscription_id:
            data["stripe_subscription_id"] = stripe_subscription_id
        self.client.table("users").update(data).eq("id", user_id).execute()
    
    async def increment_generations(self, user_id: str):
        """Increment generation count"""
        self.client.rpc("increment_generations", {"user_id": user_id}).execute()
    
    async def save_generation(self, user_id: str, input_text: str, output_text: str, app_type: str):
        """Save generation history"""
        data = {
            "user_id": user_id,
            "input_text": input_text,
            "output_text": output_text,
            "app_type": app_type
        }
        self.client.table("generations").insert(data).execute()
