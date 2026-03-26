"""
AI generation endpoint with freemium enforcement
"""

import logging
from fastapi import APIRouter, HTTPException, Request
from services.claude import ClaudeService
from services.database import Database
from utils.prompts import get_prompt
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FREE_GENERATIONS = 1

claude_service = ClaudeService()
db = Database(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@router.post("/generate")
async def generate(request: Request):
    """
    Generate AI content.
    Free users: 1 generation lifetime.
    Subscribed users: unlimited.
    """
    try:
        data = await request.json()
        user_email = data.get("email")
        app_type = data.get("app_type", "invoice_generator")
        user_input = data.get("input", "")

        if not user_email or not user_input:
            raise HTTPException(status_code=400, detail="email and input are required")

        if len(user_input.strip()) < 10:
            raise HTTPException(status_code=400, detail="Input must be at least 10 characters")

        # Get or create user
        user = await db.get_user_by_email(user_email)
        if not user:
            user = await db.create_user(user_email)

        # Freemium enforcement
        is_subscribed = user.get("subscription_status") == "active"
        if not is_subscribed and user.get("generations_used", 0) >= MAX_FREE_GENERATIONS:
            raise HTTPException(
                status_code=403,
                detail="Free generation limit reached. Upgrade to Pro for unlimited access.",
            )

        # Validate template type
        try:
            system_prompt, prompt_template = get_prompt(app_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown app_type: {app_type}")

        # Generate with Claude
        output = await claude_service.generate(
            prompt=prompt_template,
            user_input=user_input,
            system_prompt=system_prompt,
        )

        # Persist generation and increment counter
        await db.save_generation(
            user_id=user["id"],
            input_text=user_input,
            output_text=output,
            app_type=app_type,
        )
        await db.increment_generations(user["id"])

        return {"success": True, "output": output}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Generation failed. Please try again.")
