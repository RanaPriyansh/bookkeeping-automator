"""
Claude API service for AI generation
"""

import os
from typing import Optional
from anthropic import Anthropic
from .config import settings

class ClaudeService:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    async def generate(self, prompt: str, user_input: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Claude API"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n{user_input}"}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {e}")
    
    async def generate_with_json(self, prompt: str, user_input: str, json_schema: dict) -> dict:
        """Generate structured JSON output"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=f"Always respond with valid JSON matching this schema: {json_schema}",
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n{user_input}"}
                ]
            )
            import json
            return json.loads(message.content[0].text)
        except Exception as e:
            raise Exception(f"Claude API error: {e}")
