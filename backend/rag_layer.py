"""
RAG (Retrieval-Augmented Generation) Layer for archetype blending.
Manages Supabase integration and intelligent archetype retrieval.
"""
import logging
from typing import List, Optional, Dict
from models import Archetype
from config import settings

logger = logging.getLogger(__name__)


# Built-in archetype dataset (can be synced with Supabase)
ARCHETYPE_DATASET = [
    {
        "id": "cyberpunk_poet",
        "aesthetic": "Cyberpunk Poet",
        "traits": ["Melancholic", "Tech-savvy", "Nocturnal", "Introspective"],
        "vibe_keywords": ["neon", "dystopian", "rebellious", "poetic"],
        "moodboard_prompts": [
            "neon skyline at midnight, rain reflecting lights",
            "vintage CRT monitor glowing in darkness",
            "punk jacket covered in flowers and tech",
            "holographic interface with poetry text",
            "dark city rooftop with stars visible through smog",
            "broken keyboard with moss growing",
            "cyberpunk femme fatale with sad eyes"
        ],
        "playlist_keywords": ["dark", "electronic", "melancholic", "cyberpunk"]
    },
    {
        "id": "cottagecore_romantic",
        "aesthetic": "Cottagecore Romantic",
        "traits": ["Whimsical", "Nature-loving", "Gentle", "Nostalgic"],
        "vibe_keywords": ["cottage", "pastoral", "vintage", "cottagecore"],
        "moodboard_prompts": [
            "overgrown garden cottage with wildflowers",
            "vintage tea set in morning sunlight",
            "handwritten journal surrounded by flowers",
            "forest path lined with mushrooms",
            "misty morning in a small village",
            "antique lace and dried herbs",
            "cozy fireplace with books and candles"
        ],
        "playlist_keywords": ["acoustic", "folk", "indie", "cottagecore"]
    },
    {
        "id": "cloudcore_dreamer",
        "aesthetic": "Cloudcore Catnapper",
        "traits": ["Dreamy", "Introspective", "Gentle", "Artistic"],
        "vibe_keywords": ["fluffy", "cloud", "pastel", "dreamy"],
        "moodboard_prompts": [
            "fluffy clouds against pink sky",
            "soft pastel sunrise through window",
            "cozy blankets and pillows in warm light",
            "cat sleeping among clouds",
            "cotton candy colored landscape",
            "soft focus photography aesthetic",
            "dreamy underwater or cloud realm"
        ],
        "playlist_keywords": ["lofi", "ambient", "calm", "dreamy"]
    },
    {
        "id": "dark_academia",
        "aesthetic": "Dark Academia Rebel",
        "traits": ["Intellectual", "Mysterious", "Ambitious", "Bookish"],
        "vibe_keywords": ["academia", "dark", "mysterious", "gothic"],
        "moodboard_prompts": [
            "old library with candlelit bookshelves",
            "leather-bound books and fountain pens",
            "gothic university architecture",
            "wine glasses and classical art",
            "mysterious figure in vintage school uniform",
            "ornate vintage textbooks",
            "candlelit study with autumn leaves"
        ],
        "playlist_keywords": ["classical", "dark", "mysterious", "indie"]
    },
    {
        "id": "maximalist_artist",
        "aesthetic": "Maximalist Creator",
        "traits": ["Expressive", "Colorful", "Bold", "Unapologetic"],
        "vibe_keywords": ["colorful", "bold", "artistic", "expressive"],
        "moodboard_prompts": [
            "vibrant art studio with exploding colors",
            "mixed media collage bursting with life",
            "bold makeup and clashing patterns",
            "graffiti walls and street art energy",
            "cluttered creative space filled with inspiration",
            "rainbow gradient aesthetic",
            "experimental fashion and art pieces"
        ],
        "playlist_keywords": ["experimental", "energetic", "bold", "electronic"]
    }
]


class RAGLayer:
    """Retrieval-Augmented Generation layer for intelligent archetype blending."""

    def __init__(self):
        self.archetypes = [Archetype(**a) for a in ARCHETYPE_DATASET]
        logger.info(f"Initialized RAG with {len(self.archetypes)} archetypes")

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from user input.
        
        Args:
            text: User input text
            
        Returns:
            List of extracted keywords
        """
        # Simple keyword extraction (can be enhanced with NLP)
        common_stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'am', 'are', 'was', 'were', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'i', 'me', 'my', 'you', 'your'
        }

        # Simple tokenization and filtering
        words = text.lower().split()
        keywords = [
            word.strip('.,!?;:') for word in words
            if word.lower() not in common_stop_words and len(word) > 3
        ]
        return keywords[:10]  # Return top 10 keywords

    def retrieve_archetypes(
        self,
        keywords: List[str],
        aesthetic_preference: Optional[str] = None,
        limit: int = 3
    ) -> List[Archetype]:
        """
        Retrieve relevant archetypes based on keywords and aesthetic preference.
        
        Args:
            keywords: Extracted keywords from user input
            aesthetic_preference: Optional aesthetic direction
            limit: Number of archetypes to return
            
        Returns:
            List of relevant archetypes
        """
        scored_archetypes: Dict[str, float] = {}

        for archetype in self.archetypes:
            score = 0.0

            # Match keywords with archetype attributes
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Check against vibe keywords
                if any(keyword_lower in vibe.lower() 
                       for vibe in archetype.vibe_keywords):
                    score += 2.0
                
                # Check against traits
                if any(keyword_lower in trait.lower() 
                       for trait in archetype.traits):
                    score += 1.5
                
                # Partial matches
                if keyword_lower in archetype.aesthetic.lower():
                    score += 1.0

            # Boost score if aesthetic preference matches
            if aesthetic_preference and aesthetic_preference.lower() in archetype.aesthetic.lower():
                score += 5.0

            if score > 0:
                scored_archetypes[archetype.id] = score

        # Sort by score and return top matches
        sorted_ids = sorted(
            scored_archetypes.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        result = [
            next(a for a in self.archetypes if a.id == arch_id)
            for arch_id, _ in sorted_ids[:limit]
        ]

        logger.info(f"Retrieved {len(result)} archetypes for keywords: {keywords[:5]}")
        return result

    def blend_archetypes(
        self,
        primary_archetype: Archetype,
        secondary_archetypes: List[Archetype]
    ) -> Dict:
        """
        Intelligently blend archetypes for unique persona generation.
        
        Args:
            primary_archetype: Main archetype
            secondary_archetypes: Supporting archetypes to blend
            
        Returns:
            Dict with blended attributes for prompt enhancement
        """
        blended = {
            "primary_aesthetic": primary_archetype.aesthetic,
            "blended_traits": list(set(
                primary_archetype.traits +
                [t for arch in secondary_archetypes for t in arch.traits]
            ))[:5],
            "combined_keywords": list(set(
                primary_archetype.vibe_keywords +
                [k for arch in secondary_archetypes for k in arch.vibe_keywords]
            ))[:8],
            "enhanced_prompts": (
                primary_archetype.moodboard_prompts +
                [p for arch in secondary_archetypes for p in arch.moodboard_prompts]
            )[:10]
        }

        logger.info(f"Blended archetypes: {blended['primary_aesthetic']}")
        return blended


# Singleton instance
_rag_layer: Optional[RAGLayer] = None


def get_rag_layer() -> RAGLayer:
    """Get or create RAG layer singleton."""
    global _rag_layer
    if _rag_layer is None:
        _rag_layer = RAGLayer()
    return _rag_layer
