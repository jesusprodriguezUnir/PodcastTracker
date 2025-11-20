"""Pydantic schemas for API validation."""

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


class PodcastBase(BaseModel):
    """Base podcast schema."""
    name: str = Field(..., max_length=255)
    rss_url: str = Field(..., max_length=500)
    spotify_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    artwork_url: Optional[str] = Field(None, max_length=500)


class PodcastCreate(PodcastBase):
    """Schema for creating a podcast."""
    pass


class PodcastSchema(PodcastBase):
    """Schema for podcast response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EpisodeBase(BaseModel):
    """Base episode schema."""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    pub_date: datetime
    duration: Optional[str] = Field(None, max_length=50)
    episode_url: str = Field(..., max_length=500)
    spotify_url: Optional[str] = Field(None, max_length=500)
    listened: bool = False


class EpisodeCreate(EpisodeBase):
    """Schema for creating an episode."""
    podcast_id: int


class EpisodeSchema(EpisodeBase):
    """Schema for episode response."""
    id: int
    podcast_id: int
    created_at: datetime
    podcast: Optional[PodcastSchema] = None
    
    class Config:
        from_attributes = True


class EpisodeUpdate(BaseModel):
    """Schema for updating an episode."""
    listened: Optional[bool] = None


class EpisodeListResponse(BaseModel):
    """Schema for paginated episode list."""
    episodes: list[EpisodeSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class RefreshResponse(BaseModel):
    """Schema for refresh response."""
    message: str
    new_episodes: int
