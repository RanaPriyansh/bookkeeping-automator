"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class GenerateRequest(BaseModel):
    email: EmailStr
    app_type: str = "resume_builder"
    input: str = Field(..., min_length=10, description="User input for generation")
    
class GenerateResponse(BaseModel):
    success: bool
    output: str
    tokens_used: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserUpdate(BaseModel):
    subscription_status: Optional[str] = None  # active, inactive, trialing
    stripe_subscription_id: Optional[str] = None

class CheckoutSessionRequest(BaseModel):
    email: EmailStr
    success_url: str
    cancel_url: str

class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str

# App-specific response models
class ResumeResponse(BaseModel):
    resume_text: str
    ats_score: Optional[int] = None
    suggestions: Optional[List[str]] = None

class ContractResponse(BaseModel):
    contract_text: str
    clauses_highlights: Optional[Dict[str, str]] = None
    risk_level: Optional[str] = None

class FinancePlanResponse(BaseModel):
    summary: str
    retirement_score: int = Field(..., ge=1, le=10)
    action_items: List[str]
    monthly_savings_target: Optional[float] = None
