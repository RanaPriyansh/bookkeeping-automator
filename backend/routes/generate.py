"""
Generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from services.claude import ClaudeService
from services.database import Database
from ..config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
claude_service = ClaudeService()
db = Database(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

@router.post("/generate")
async def generate(request: Request):
    """Main generation endpoint"""
    try:
        data = await request.json()
        user_email = data.get("email")
        app_type = data.get("app_type", "resume_builder")
        user_input = data.get("input", "")
        
        if not user_email or not user_input:
            raise HTTPException(status_code=400, detail="Email and input required")
        
        # Get or create user
        user = await db.get_user_by_email(user_email)
        if not user:
            user = await db.create_user(user_email)
        
        # Check subscription (if needed)
        # For freemium: check generations_used < limit
        
        # Generate with Claude
        from utils.prompts import get_prompt
        system_prompt, prompt_template = get_prompt(app_type)
        
        output = await claude_service.generate(
            prompt=prompt_template,
            user_input=user_input,
            system_prompt=system_prompt
        )
        
        # Save generation
        await db.save_generation(
            user_id=user["id"],
            input_text=user_input,
            output_text=output,
            app_type=app_type
        )
        
        # Increment counter
        await db.increment_generations(user["id"])
        
        return {"success": True, "output": output}
        
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
