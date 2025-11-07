"""
Spotify API integration for playlist matching and generation.
"""
import base64
import httpx
import logging
from typing import Optional, List
from config import settings

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Client for Spotify API integration."""

    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.api_url = "https://api.spotify.com/v1"
        self.access_token: Optional[str] = None

    async def get_access_token(self) -> str:
        """
        Get Spotify API access token using client credentials.
        
        Returns:
            Access token string
        """
        if self.access_token:
            return self.access_token

        try:
            # Create authorization header
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

            headers = {
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {"grant_type": "client_credentials"}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.auth_url,
                    headers=headers,
                    data=data
                )
                response.raise_for_status()

                result = response.json()
                self.access_token = result["access_token"]
                logger.info("Successfully authenticated with Spotify API")
                return self.access_token

        except httpx.HTTPError as e:
            logger.error(f"Failed to authenticate with Spotify: {str(e)}")
            raise

    async def search_tracks(
        self,
        query: str,
        limit: int = 5
    ) -> List[dict]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of track information
        """
        try:
            token = await self.get_access_token()
            headers = {"Authorization": f"Bearer {token}"}

            params = {
                "q": query,
                "type": "track",
                "limit": limit
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()

                result = response.json()
                tracks = result.get("tracks", {}).get("items", [])
                logger.info(f"Found {len(tracks)} tracks for query: {query}")
                return tracks

        except httpx.HTTPError as e:
            logger.error(f"Spotify search failed: {str(e)}")
            return []

    async def create_playlist_recommendation(
        self,
        playlist_name: str,
        vibe_keywords: List[str]
    ) -> dict:
        """
        Generate playlist recommendation based on vibe keywords.
        
        Args:
            playlist_name: Name of the playlist
            vibe_keywords: Keywords describing the vibe
            
        Returns:
            Playlist recommendation with search links
        """
        try:
            # Construct search query from keywords
            search_query = " ".join(vibe_keywords[:3])
            tracks = await self.search_tracks(search_query)

            if tracks:
                first_track = tracks[0]
                spotify_link = first_track.get("external_urls", {}).get("spotify", "")
                
                recommendation = {
                    "playlist_name": playlist_name,
                    "vibe_keywords": vibe_keywords,
                    "sample_tracks": [
                        {
                            "name": track.get("name"),
                            "artist": ", ".join(
                                [a.get("name") for a in track.get("artists", [])]
                            ),
                            "link": track.get("external_urls", {}).get("spotify")
                        }
                        for track in tracks[:3]
                    ],
                    "spotify_search_link": f"https://open.spotify.com/search/{playlist_name.replace(' ', '%20')}"
                }
                
                logger.info(f"Generated playlist recommendation: {playlist_name}")
                return recommendation
            else:
                return {
                    "playlist_name": playlist_name,
                    "vibe_keywords": vibe_keywords,
                    "spotify_search_link": f"https://open.spotify.com/search/{playlist_name.replace(' ', '%20')}"
                }

        except Exception as e:
            logger.error(f"Failed to create playlist recommendation: {str(e)}")
            return {
                "playlist_name": playlist_name,
                "vibe_keywords": vibe_keywords,
                "spotify_search_link": f"https://open.spotify.com/search/{playlist_name.replace(' ', '%20')}"
            }


# Singleton instance
_spotify_client: Optional[SpotifyClient] = None


async def get_spotify_client() -> SpotifyClient:
    """Get or create Spotify client singleton."""
    global _spotify_client
    if _spotify_client is None:
        _spotify_client = SpotifyClient()
    return _spotify_client
