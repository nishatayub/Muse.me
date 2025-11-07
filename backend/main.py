"""
Main FastAPI application with all endpoints and middleware.
"""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import settings
from models import GeneratePersonaRequest, GeneratePersonaResponse, AestheticResponse
from llm_engine import get_llm_engine, close_llm_engine
from rag_layer import get_rag_layer
from spotify_client import get_spotify_client
from card_generator import IdentityCardGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("🌸 Muse.me Backend Starting...")
    yield
    logger.info("🌸 Muse.me Backend Shutting Down...")
    await close_llm_engine()


# Create FastAPI app
app = FastAPI(
    title="Muse.me API",
    description="Transform your mundane life into aesthetic alter egos",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Muse.me API",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/generate", response_model=GeneratePersonaResponse)
async def generate_persona(request: GeneratePersonaRequest):
    """
    Generate an aesthetic persona from user input.
    
    This endpoint:
    1. Extracts keywords from user input
    2. Retrieves relevant archetypes via RAG
    3. Generates structured persona response using LLM
    4. Optionally generates moodboard and playlist
    
    Args:
        request: GeneratePersonaRequest with user_input and optional aesthetic_preference
        
    Returns:
        GeneratePersonaResponse with complete persona data
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        # Validate input
        if len(request.user_input) > settings.max_input_length:
            raise ValueError(f"Input exceeds maximum length of {settings.max_input_length}")
        if len(request.user_input) < 10:
            raise ValueError("Input must be at least 10 characters")
        
        logger.info(f"Received persona generation request. Input length: {len(request.user_input)}")

        # Get services
        llm_engine = await get_llm_engine()
        rag_layer = get_rag_layer()
        spotify_client = await get_spotify_client()

        # Step 1: Extract keywords and retrieve archetypes
        keywords = rag_layer.extract_keywords(request.user_input)
        logger.info(f"Extracted keywords: {keywords[:5]}")

        retrieved_archetypes = rag_layer.retrieve_archetypes(
            keywords=keywords,
            aesthetic_preference=request.aesthetic_preference,
            limit=2
        )

        # Step 2: Generate persona using LLM
        persona = await llm_engine.generate_persona(
            user_input=request.user_input,
            aesthetic_preference=request.aesthetic_preference
        )
        logger.info(f"Generated persona: {persona.aesthetic_identity}")

        # Step 3: Generate Spotify recommendation
        spotify_info = await spotify_client.create_playlist_recommendation(
            playlist_name=persona.spotify_playlist,
            vibe_keywords=persona.vibe_description.split()[:3]
        )
        spotify_link = spotify_info.get("spotify_search_link")

        # Step 4: Generate identity card
        card_svg = IdentityCardGenerator.generate_card_svg(persona)

        # Create response
        response = GeneratePersonaResponse(
            id=f"persona_{int(datetime.now().timestamp())}",
            persona=persona,
            spotify_link=spotify_link,
            card_url="data:image/svg+xml;base64," + __import__("base64").b64encode(card_svg.encode()).decode(),
            created_at=datetime.now()
        )

        logger.info(f"Successfully generated persona response for ID: {response.id}")
        return response

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in persona generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate persona. Please try again.")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Muse.me API",
        "description": "Transform your mundane life into aesthetic alter egos",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)",
            "docs": "/docs"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
