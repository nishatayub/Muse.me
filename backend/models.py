"""
Pydantic models for structured data validation and API responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PersonaRoutineStep(BaseModel):
    """Individual step in daily routine."""
    step: str = Field(..., description="Description of routine step")
    time: Optional[str] = Field(None, description="Suggested time of day")


class AestheticResponse(BaseModel):
    """Main structured response for aesthetic persona generation."""
    aesthetic_identity: str = Field(
        ..., 
        description="Poetic identity name for the alter ego"
    )
    routine: List[str] = Field(
        ..., 
        description="3-5 steps of fictional daily routine",
        min_items=3,
        max_items=5
    )
    traits: List[str] = Field(
        ..., 
        description="3-5 personality traits",
        min_items=3,
        max_items=5
    )
    vibe_description: str = Field(
        ..., 
        description="Poetic vibe/aesthetic description"
    )
    moodboard_prompts: List[str] = Field(
        ..., 
        description="5-7 prompts for image generation",
        min_items=5,
        max_items=7
    )
    spotify_playlist: str = Field(
        ..., 
        description="Curated Spotify playlist name matching the persona"
    )


class GeneratePersonaRequest(BaseModel):
    """Request model for persona generation."""
    user_input: str = Field(
        ..., 
        description="User's description (journal entry, bio, routine, etc.)",
        min_length=10,
        max_length=1000
    )
    aesthetic_preference: Optional[str] = Field(
        None,
        description="Optional aesthetic direction (cyberpunk, cottagecore, etc.)"
    )


class GeneratePersonaResponse(BaseModel):
    """Response model for persona generation endpoint."""
    id: Optional[str] = None
    persona: AestheticResponse
    moodboard_url: Optional[str] = None
    spotify_link: Optional[str] = None
    card_url: Optional[str] = None
    created_at: datetime


class Archetype(BaseModel):
    """Archetype data structure for RAG layer."""
    id: str
    aesthetic: str
    traits: List[str]
    vibe_keywords: List[str]
    moodboard_prompts: List[str]
    playlist_keywords: List[str]


class PersonaCard(BaseModel):
    """Data model for downloadable identity card."""
    persona: AestheticResponse
    image_url: Optional[str] = None
    export_format: str = Field(default="svg", description="svg or png")
