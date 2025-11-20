"""Business logic for podcast management."""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..database.models import Podcast, Episode
from .rss_parser import RSSParser

logger = logging.getLogger(__name__)


class PodcastService:
    """Service for managing podcasts and episodes."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.rss_parser = RSSParser()
    
    def add_podcast(self, name: str, rss_url: str, spotify_url: Optional[str] = None) -> Optional[Podcast]:
        """
        Add a new podcast to the database.
        
        Args:
            name: Podcast name
            rss_url: RSS feed URL
            spotify_url: Optional Spotify URL
            
        Returns:
            Created Podcast object or None if failed
        """
        try:
            # Check if podcast already exists
            existing = self.db.query(Podcast).filter(Podcast.rss_url == rss_url).first()
            if existing:
                logger.info(f"Podcast already exists: {name}")
                return existing
            
            # Parse RSS feed to get metadata
            feed_data = self.rss_parser.parse_feed(rss_url)
            if not feed_data:
                logger.error(f"Failed to parse RSS feed for: {name}")
                return None
            
            # Create podcast
            podcast = Podcast(
                name=name,
                rss_url=rss_url,
                spotify_url=spotify_url,
                description=feed_data.get("description", ""),
                artwork_url=feed_data.get("artwork_url")
            )
            
            self.db.add(podcast)
            self.db.commit()
            self.db.refresh(podcast)
            
            logger.info(f"Added podcast: {name}")
            
            # Add initial episodes
            self._add_episodes_from_feed(podcast, feed_data["episodes"])
            
            return podcast
            
        except Exception as e:
            logger.error(f"Error adding podcast {name}: {e}")
            self.db.rollback()
            return None
    
    def check_new_episodes(self, podcast: Podcast) -> int:
        """
        Check for new episodes for a podcast.
        
        Args:
            podcast: Podcast object
            
        Returns:
            Number of new episodes added
        """
        try:
            logger.info(f"Checking new episodes for: {podcast.name}")
            
            # Parse RSS feed
            feed_data = self.rss_parser.parse_feed(podcast.rss_url)
            if not feed_data:
                logger.error(f"Failed to parse RSS feed for: {podcast.name}")
                return 0
            
            # Add new episodes
            new_count = self._add_episodes_from_feed(podcast, feed_data["episodes"])
            
            logger.info(f"Added {new_count} new episodes for: {podcast.name}")
            return new_count
            
        except Exception as e:
            logger.error(f"Error checking new episodes for {podcast.name}: {e}")
            return 0
    
    def _add_episodes_from_feed(self, podcast: Podcast, episodes_data: List[dict]) -> int:
        """
        Add episodes from feed data to database.
        
        Args:
            podcast: Podcast object
            episodes_data: List of episode dictionaries
            
        Returns:
            Number of new episodes added
        """
        new_count = 0
        
        for ep_data in episodes_data:
            try:
                # Check if episode already exists
                existing = self.db.query(Episode).filter(
                    Episode.podcast_id == podcast.id,
                    Episode.title == ep_data["title"],
                    Episode.pub_date == ep_data["pub_date"]
                ).first()
                
                if existing:
                    continue
                
                # Create new episode
                episode = Episode(
                    podcast_id=podcast.id,
                    title=ep_data["title"],
                    description=ep_data.get("description", ""),
                    pub_date=ep_data["pub_date"],
                    duration=ep_data.get("duration"),
                    episode_url=ep_data["episode_url"],
                    spotify_url=podcast.spotify_url,  # Use podcast's Spotify URL
                    listened=False
                )
                
                self.db.add(episode)
                new_count += 1
                
            except Exception as e:
                logger.error(f"Error adding episode: {e}")
                continue
        
        if new_count > 0:
            self.db.commit()
        
        return new_count
    
    def mark_as_listened(self, episode_id: int) -> bool:
        """
        Mark an episode as listened.
        
        Args:
            episode_id: Episode ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            episode = self.db.query(Episode).filter(Episode.id == episode_id).first()
            if not episode:
                logger.warning(f"Episode not found: {episode_id}")
                return False
            
            episode.listened = True
            self.db.commit()
            
            logger.info(f"Marked episode as listened: {episode.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking episode as listened: {e}")
            self.db.rollback()
            return False
    
    def get_pending_episodes(self, limit: int = 50, offset: int = 0) -> List[Episode]:
        """
        Get pending (not listened) episodes.
        
        Args:
            limit: Maximum number of episodes to return
            offset: Offset for pagination
            
        Returns:
            List of Episode objects
        """
        return (
            self.db.query(Episode)
            .filter(Episode.listened == False)
            .order_by(Episode.pub_date.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_all_podcasts(self) -> List[Podcast]:
        """
        Get all podcasts.
        
        Returns:
            List of Podcast objects
        """
        return self.db.query(Podcast).all()
    
    def refresh_all_podcasts(self) -> int:
        """
        Refresh all podcasts and check for new episodes.
        
        Returns:
            Total number of new episodes added
        """
        podcasts = self.get_all_podcasts()
        total_new = 0
        
        for podcast in podcasts:
            new_count = self.check_new_episodes(podcast)
            total_new += new_count
        
        logger.info(f"Refresh complete. Added {total_new} new episodes total.")
        return total_new
