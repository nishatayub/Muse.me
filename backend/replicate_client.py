"""
Replicate API integration for AI image generation (Stable Diffusion).
"""
import asyncio
import httpx
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


class ReplicateClient:
    """Client for Replicate API (Stable Diffusion image generation)."""

    def __init__(self):
        self.api_token = settings.replicate_api_token
        self.api_url = "https://api.replicate.com/v1"
        self.model_version = "db21e45d3f7023abc9db3d3be7779425163b8f11ccbde76a5f7e29e0fbc00ae6"  # Stable Diffusion 3

    async def generate_image(
        self,
        prompt: str,
        width: int = 768,
        height: int = 768,
        num_outputs: int = 1
    ) -> Optional[str]:
        """
        Generate image using Stable Diffusion.
        
        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            num_outputs: Number of images to generate
            
        Returns:
            URL of generated image or None
        """
        try:
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "version": self.model_version,
                "input": {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": num_outputs,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 50
                }
            }

            async with httpx.AsyncClient(timeout=300.0) as client:
                # Create prediction
                response = await client.post(
                    f"{self.api_url}/predictions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                prediction = response.json()
                prediction_id = prediction.get("id")
                logger.info(f"Created prediction: {prediction_id}")

                # Poll for completion
                max_attempts = 120  # 10 minutes with 5-second intervals
                for attempt in range(max_attempts):
                    await asyncio.sleep(5)

                    check_response = await client.get(
                        f"{self.api_url}/predictions/{prediction_id}",
                        headers=headers
                    )
                    check_response.raise_for_status()

                    prediction = check_response.json()
                    status = prediction.get("status")

                    if status == "succeeded":
                        output = prediction.get("output", [])
                        if output:
                            image_url = output[0]
                            logger.info(f"Image generated successfully: {image_url}")
                            return image_url
                    elif status == "failed":
                        error = prediction.get("error")
                        logger.error(f"Image generation failed: {error}")
                        return None

                logger.warning("Image generation timed out")
                return None

        except httpx.HTTPError as e:
            logger.error(f"Replicate API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in image generation: {str(e)}")
            return None


# Singleton instance
_replicate_client: Optional[ReplicateClient] = None


async def get_replicate_client() -> ReplicateClient:
    """Get or create Replicate client singleton."""
    global _replicate_client
    if _replicate_client is None:
        _replicate_client = ReplicateClient()
    return _replicate_client
