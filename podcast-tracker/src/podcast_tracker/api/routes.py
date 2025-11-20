"""FastAPI routes for the Podcast Tracker API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging
import math

from ..database import get_db_session, Podcast, Episode
from ..services import PodcastService
from .schemas import (
    PodcastSchema,
    EpisodeSchema,
    EpisodeUpdate,
    EpisodeListResponse,
    RefreshResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/podcasts", response_model=List[PodcastSchema])
def get_podcasts(db: Session = Depends(get_db_session)):
    """Get all podcasts."""
    podcasts = db.query(Podcast).all()
    return podcasts


@router.get("/api/episodes", response_model=EpisodeListResponse)
def get_episodes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    podcast_id: int = Query(None),
    db: Session = Depends(get_db_session)
):
    """Get episodes with pagination."""
    query = db.query(Episode).filter(Episode.listened == False)
    
    if podcast_id:
        query = query.filter(Episode.podcast_id == podcast_id)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    episodes = (
        query
        .order_by(Episode.pub_date.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
        .all()
    )
    
    # Load podcast relationship
    for episode in episodes:
        _ = episode.podcast  # Trigger lazy loading
    
    total_pages = math.ceil(total / page_size)
    
    return EpisodeListResponse(
        episodes=episodes,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/api/episodes/{episode_id}", response_model=EpisodeSchema)
def get_episode(episode_id: int, db: Session = Depends(get_db_session)):
    """Get a specific episode."""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    return episode


@router.patch("/api/episodes/{episode_id}/listened", response_model=EpisodeSchema)
def mark_episode_listened(
    episode_id: int,
    update: EpisodeUpdate,
    db: Session = Depends(get_db_session)
):
    """Mark an episode as listened or not listened."""
    service = PodcastService(db)
    
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    if update.listened is not None:
        episode.listened = update.listened
        db.commit()
        db.refresh(episode)
    
    return episode


@router.post("/api/podcasts/refresh", response_model=RefreshResponse)
def refresh_podcasts(db: Session = Depends(get_db_session)):
    """Manually trigger a refresh of all podcasts."""
    logger.info("Manual refresh triggered")
    
    service = PodcastService(db)
    new_episodes = service.refresh_all_podcasts()
    
    return RefreshResponse(
        message=f"Refresh complete. Found {new_episodes} new episodes.",
        new_episodes=new_episodes
    )
