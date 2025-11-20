"""Unit tests for database models."""

import pytest
from datetime import datetime

from podcast_tracker.database.models import Podcast, Episode


@pytest.mark.unit
def test_create_podcast(test_db, sample_podcast_data):
    """Test creating a podcast."""
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    assert podcast.id is not None
    assert podcast.name == sample_podcast_data["name"]
    assert podcast.rss_url == sample_podcast_data["rss_url"]
    assert podcast.created_at is not None


@pytest.mark.unit
def test_create_episode(test_db, sample_podcast_data, sample_episode_data):
    """Test creating an episode."""
    # Create podcast first
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    # Create episode
    episode = Episode(podcast_id=podcast.id, **sample_episode_data)
    test_db.add(episode)
    test_db.commit()
    test_db.refresh(episode)
    
    assert episode.id is not None
    assert episode.podcast_id == podcast.id
    assert episode.title == sample_episode_data["title"]
    assert episode.listened == False


@pytest.mark.unit
def test_podcast_episode_relationship(test_db, sample_podcast_data, sample_episode_data):
    """Test relationship between podcast and episodes."""
    # Create podcast
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    # Create episodes
    for i in range(3):
        episode = Episode(
            podcast_id=podcast.id,
            title=f"Episode {i+1}",
            description=f"Description {i+1}",
            pub_date=datetime.utcnow(),
            episode_url=f"https://example.com/ep{i+1}.mp3",
            listened=False
        )
        test_db.add(episode)
    
    test_db.commit()
    
    # Refresh and check relationship
    test_db.refresh(podcast)
    assert len(podcast.episodes) == 3
    assert all(ep.podcast_id == podcast.id for ep in podcast.episodes)


@pytest.mark.unit
def test_podcast_unique_constraints(test_db, sample_podcast_data):
    """Test unique constraints on podcast."""
    # Create first podcast
    podcast1 = Podcast(**sample_podcast_data)
    test_db.add(podcast1)
    test_db.commit()
    
    # Try to create duplicate
    podcast2 = Podcast(**sample_podcast_data)
    test_db.add(podcast2)
    
    with pytest.raises(Exception):
        test_db.commit()


@pytest.mark.unit
def test_episode_listened_default(test_db, sample_podcast_data, sample_episode_data):
    """Test that episode listened defaults to False."""
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    episode_data = sample_episode_data.copy()
    del episode_data["listened"]  # Remove listened field
    
    episode = Episode(podcast_id=podcast.id, **episode_data)
    test_db.add(episode)
    test_db.commit()
    test_db.refresh(episode)
    
    assert episode.listened == False
