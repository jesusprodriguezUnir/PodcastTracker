"""Scheduler for automatic podcast updates."""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from ..database import get_db
from .podcast_service import PodcastService
from ..config import settings

logger = logging.getLogger(__name__)


class PodcastScheduler:
    """Scheduler for checking new podcast episodes."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Add job to check for new episodes
        self.scheduler.add_job(
            func=self._check_new_episodes_job,
            trigger=IntervalTrigger(hours=settings.check_interval_hours),
            id="check_new_episodes",
            name="Check for new podcast episodes",
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately on start
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info(f"Scheduler started. Checking for new episodes every {settings.check_interval_hours} hour(s)")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        
        logger.info("Scheduler stopped")
    
    def _check_new_episodes_job(self):
        """Job to check for new episodes in all podcasts."""
        logger.info("Running scheduled check for new episodes...")
        
        try:
            with get_db() as db:
                service = PodcastService(db)
                new_episodes = service.refresh_all_podcasts()
                logger.info(f"Scheduled check complete. Found {new_episodes} new episodes.")
        except Exception as e:
            logger.error(f"Error in scheduled check: {e}")


# Global scheduler instance
podcast_scheduler = PodcastScheduler()
