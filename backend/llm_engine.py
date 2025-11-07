"""
LLM Engine for persona generation using OpenRouter API.
Handles structured output and prompt engineering.
"""
import httpx
import json
import logging
from typing import Optional
from config import settings
from models import AestheticResponse
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, AESTHETIC_HINT_TEMPLATE

logger = logging.getLogger(__name__)


class LLMEngine:
    """Handles all interactions with OpenRouter API for persona generation."""

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "mistralai/mixtral-8x7b-instruct"  # High quality, cost-effective
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate_persona(
        self,
        user_input: str,
        aesthetic_preference: Optional[str] = None
    ) -> AestheticResponse:
        """
        Generate an aesthetic persona using OpenRouter API.
        
        Args:
            user_input: User's description to transform
            aesthetic_preference: Optional aesthetic direction
            
        Returns:
            AestheticResponse: Structured persona data
            
        Raises:
            ValueError: If API response is invalid
        """
        try:
            # Build user message with optional aesthetic hint
            aesthetic_hint = ""
            if aesthetic_preference:
                aesthetic_hint = AESTHETIC_HINT_TEMPLATE.format(
                    aesthetic=aesthetic_preference
                )

            user_message = USER_PROMPT_TEMPLATE.format(
                user_input=user_input,
                aesthetic_hint=aesthetic_hint
            )

            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": settings.backend_url,
                "X-Title": "Muse.me"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.8,  # Creative but coherent
                "max_tokens": 1500,
                "response_format": {"type": "json_object"}  # Force JSON output
            }

            # Call OpenRouter API
            logger.info(f"Calling OpenRouter with model: {self.model}")
            response = await self.client.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse JSON response
            try:
                persona_dict = json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse API response as JSON: {content}")
                raise ValueError("API returned invalid JSON")

            # Validate and construct AestheticResponse
            persona = AestheticResponse(**persona_dict)
            logger.info(f"Successfully generated persona: {persona.aesthetic_identity}")
            return persona

        except httpx.HTTPError as e:
            logger.error(f"API request failed: {str(e)}")
            raise ValueError(f"Failed to generate persona: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM engine: {str(e)}")
            raise

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Singleton instance
_llm_engine: Optional[LLMEngine] = None


async def get_llm_engine() -> LLMEngine:
    """Get or create LLM engine singleton."""
    global _llm_engine
    if _llm_engine is None:
        _llm_engine = LLMEngine()
    return _llm_engine


async def close_llm_engine():
    """Close LLM engine."""
    global _llm_engine
    if _llm_engine:
        await _llm_engine.close()
        _llm_engine = None
