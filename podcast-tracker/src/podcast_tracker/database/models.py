"""Database models for Podcast Tracker."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Podcast(Base):
    """Podcast model."""
    
    __tablename__ = "podcasts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    rss_url = Column(String(500), nullable=False, unique=True)
    spotify_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    artwork_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    episodes = relationship("Episode", back_populates="podcast", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Podcast(id={self.id}, name='{self.name}')>"


class Episode(Base):
    """Episode model."""
    
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    pub_date = Column(DateTime, nullable=False)
    duration = Column(String(50), nullable=True)
    episode_url = Column(String(500), nullable=False)
    spotify_url = Column(String(500), nullable=True)
    listened = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    podcast = relationship("Podcast", back_populates="episodes")
    
    def __repr__(self):
        return f"<Episode(id={self.id}, title='{self.title}', listened={self.listened})>"
