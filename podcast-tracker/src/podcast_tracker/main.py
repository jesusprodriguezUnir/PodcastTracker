"""Main application entry point."""

import logging
import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from .config import settings
from .database import init_db, get_db
from .services import podcast_scheduler, PodcastService
from .api import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Podcast seed data
INITIAL_PODCASTS = [
    {
        "name": "Loop Infinito (by Xataka)",
        "rss_url": "https://feeds.ivoox.com/feed_fg_f1757774_filtro_1.xml",
        "spotify_url": "https://open.spotify.com/show/6FiLbVU0VqGLlOxfYQqYHy"
    },
    {
        "name": "El Test de Turing",
        "rss_url": "https://www.ivoox.com/test-turing_fg_f11955194_filtro_1.xml",
        "spotify_url": "https://open.spotify.com/show/5K3qJXqYqLxqLqLqLqLqLq"
    },
   {
        "name": "Monos Estocásticos",
        "rss_url": "https://cuonda.com/monos-estocasticos/feed",
        "spotify_url": "https://open.spotify.com/show/1LgQzOa79j7Dlsa9YF5x2b"
    },
    {
        "name": "Inteligencia Artificial con Jon Hernandez",
        "rss_url": "https://www.ivoox.com/podcast-inteligencia-artificial-jon-hernandez_fg_f12413741_filtro_1.xml",
        "spotify_url": "https://open.spotify.com/show/70kXF7VTC2fF5O3N9KYaXW"
    },
    {
        "name": "Inteligencia Artificial - Pocho Costa",
        "rss_url": "https://pochocosta.com/feed/podcast",
        "spotify_url": "https://open.spotify.com/show/4g7RlgQ9GJsV1dxWfs0O1I"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Skip full initialization if running tests, but still initialize DB
    if os.getenv("TESTING") == "true":
        # Initialize test database only
        init_db()
    else:
        # Full startup for production
        logger.info("Starting Podcast Tracker...")
        
        # Initialize database
        init_db()
        
        # Seed initial podcasts
        seed_podcasts()
        
        # Start scheduler
        podcast_scheduler.start()
        
        logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    if os.getenv("TESTING") != "true":
        logger.info("Shutting down...")
        podcast_scheduler.stop()
        logger.info("Application shutdown complete")


def seed_podcasts():
    """Seed initial podcasts into the database."""
    logger.info("Seeding initial podcasts...")
    
    with get_db() as db:
        service = PodcastService(db)
        
        for podcast_data in INITIAL_PODCASTS:
            try:
                service.add_podcast(
                    name=podcast_data["name"],
                    rss_url=podcast_data["rss_url"],
                    spotify_url=podcast_data.get("spotify_url")
                )
            except Exception as e:
                logger.error(f"Error seeding podcast {podcast_data['name']}: {e}")
    
    logger.info("Podcast seeding complete")


# Create FastAPI app
app = FastAPI(
    title="AI Podcast Tracker",
    description="Track Spanish AI podcasts automatically",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router)

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


def main():
    """Run the application."""
    uvicorn.run(
        "podcast_tracker.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )


if __name__ == "__main__":
    main()
