"""RSS feed parser for podcasts."""

import feedparser
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class RSSParser:
    """Parser for podcast RSS feeds."""
    
    @staticmethod
    def parse_feed(rss_url: str) -> Optional[Dict[str, Any]]:
        """
        Parse RSS feed and extract podcast information.
        
        Args:
            rss_url: URL of the RSS feed
            
        Returns:
            Dictionary with podcast info or None if parsing fails
        """
        try:
            logger.info(f"Parsing RSS feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has errors: {rss_url}")
            
            if not hasattr(feed, 'feed'):
                logger.error(f"Invalid RSS feed: {rss_url}")
                return None
            
            # Extract podcast metadata
            podcast_info = {
                "title": feed.feed.get("title", "Unknown Podcast"),
                "description": feed.feed.get("description", ""),
                "artwork_url": RSSParser._extract_artwork(feed.feed),
                "episodes": []
            }
            
            # Extract episodes
            for entry in feed.entries:
                episode = RSSParser._parse_episode(entry)
                if episode:
                    podcast_info["episodes"].append(episode)
            
            logger.info(f"Parsed {len(podcast_info['episodes'])} episodes from {rss_url}")
            return podcast_info
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_url}: {e}")
            return None
    
    @staticmethod
    def _parse_episode(entry: Any) -> Optional[Dict[str, Any]]:
        """
        Parse a single episode from RSS entry.
        
        Args:
            entry: feedparser entry object
            
        Returns:
            Dictionary with episode info or None if parsing fails
        """
        try:
            # Parse publication date
            pub_date = None
            if hasattr(entry, 'published'):
                try:
                    pub_date = date_parser.parse(entry.published)
                except Exception:
                    pass
            
            if not pub_date and hasattr(entry, 'updated'):
                try:
                    pub_date = date_parser.parse(entry.updated)
                except Exception:
                    pass
            
            if not pub_date:
                pub_date = datetime.utcnow()
            
            # Extract episode URL
            episode_url = entry.get("link", "")
            if not episode_url and hasattr(entry, "enclosures") and entry.enclosures:
                episode_url = entry.enclosures[0].get("href", "")
            
            # Extract duration
            duration = None
            if hasattr(entry, "itunes_duration"):
                duration = entry.itunes_duration
            
            episode = {
                "title": entry.get("title", "Untitled Episode"),
                "description": entry.get("summary", ""),
                "pub_date": pub_date,
                "episode_url": episode_url,
                "duration": duration,
            }
            
            return episode
            
        except Exception as e:
            logger.error(f"Error parsing episode: {e}")
            return None
    
    @staticmethod
    def _extract_artwork(feed_data: Any) -> Optional[str]:
        """
        Extract artwork URL from feed data.
        
        Args:
            feed_data: feedparser feed object
            
        Returns:
            Artwork URL or None
        """
        # Try iTunes image
        if hasattr(feed_data, "image"):
            if isinstance(feed_data.image, dict):
                return feed_data.image.get("href")
        
        # Try standard image tag
        if hasattr(feed_data, "image") and hasattr(feed_data.image, "href"):
            return feed_data.image.href
        
        return None
