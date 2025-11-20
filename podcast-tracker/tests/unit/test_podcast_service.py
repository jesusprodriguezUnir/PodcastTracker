"""Unit tests for podcast service."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from podcast_tracker.services.podcast_service import PodcastService
from podcast_tracker.database.models import Podcast, Episode


@pytest.mark.unit
def test_add_podcast_success(test_db):
    """Test adding a new podcast."""
    mock_feed_data = {
        "title": "Test Podcast",
        "description": "Test Description",
        "artwork_url": "https://example.com/art.jpg",
        "episodes": []
    }
    
    with patch.object(PodcastService, '_add_episodes_from_feed', return_value=0):
        with patch('podcast_tracker.services.podcast_service.RSSParser.parse_feed', return_value=mock_feed_data):
            service = PodcastService(test_db)
            podcast = service.add_podcast(
                name="Test Podcast",
                rss_url="https://example.com/feed.xml",
                spotify_url="https://open.spotify.com/show/test"
            )
            
            assert podcast is not None
            assert podcast.name == "Test Podcast"
            assert podcast.rss_url == "https://example.com/feed.xml"


@pytest.mark.unit
def test_add_podcast_duplicate(test_db, sample_podcast_data):
    """Test adding duplicate podcast."""
    # Add first podcast
    podcast1 = Podcast(**sample_podcast_data)
    test_db.add(podcast1)
    test_db.commit()
    
    mock_feed_data = {
        "title": "Test Podcast",
        "description": "Test Description",
        "artwork_url": None,
        "episodes": []
    }
    
    with patch('podcast_tracker.services.podcast_service.RSSParser.parse_feed', return_value=mock_feed_data):
        service = PodcastService(test_db)
        podcast2 = service.add_podcast(
            name="Test Podcast",
            rss_url=sample_podcast_data["rss_url"]
        )
        
        # Should return existing podcast
        assert podcast2.id == podcast1.id


@pytest.mark.unit
def test_mark_as_listened(test_db, sample_podcast_data, sample_episode_data):
    """Test marking episode as listened."""
    # Create podcast and episode
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    episode = Episode(podcast_id=podcast.id, **sample_episode_data)
    test_db.add(episode)
    test_db.commit()
    test_db.refresh(episode)
    
    # Mark as listened
    service = PodcastService(test_db)
    result = service.mark_as_listened(episode.id)
    
    assert result == True
    
    # Verify
    test_db.refresh(episode)
    assert episode.listened == True


@pytest.mark.unit
def test_mark_as_listened_not_found(test_db):
    """Test marking non-existent episode as listened."""
    service = PodcastService(test_db)
    result = service.mark_as_listened(999)
    
    assert result == False


@pytest.mark.unit
def test_get_pending_episodes(test_db, sample_podcast_data):
    """Test getting pending episodes."""
    # Create podcast
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    # Create episodes
    for i in range(5):
        episode = Episode(
            podcast_id=podcast.id,
            title=f"Episode {i+1}",
            description=f"Description {i+1}",
            pub_date=datetime.utcnow(),
            episode_url=f"https://example.com/ep{i+1}.mp3",
            listened=(i < 2)  # First 2 are listened
        )
        test_db.add(episode)
    
    test_db.commit()
    
    # Get pending episodes
    service = PodcastService(test_db)
    pending = service.get_pending_episodes()
    
    assert len(pending) == 3


@pytest.mark.unit
def test_get_all_podcasts(test_db, sample_podcast_data):
    """Test getting all podcasts."""
    # Create podcasts
    for i in range(3):
        podcast = Podcast(
            name=f"Podcast {i+1}",
            rss_url=f"https://example.com/feed{i+1}.xml",
            description=f"Description {i+1}"
        )
        test_db.add(podcast)
    
    test_db.commit()
    
    # Get all podcasts
    service = PodcastService(test_db)
    podcasts = service.get_all_podcasts()
    
    assert len(podcasts) == 3


@pytest.mark.unit
def test_add_episodes_from_feed(test_db, sample_podcast_data):
    """Test adding episodes from feed data."""
    # Create podcast
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    # Prepare episode data
    episodes_data = [
        {
            "title": "Episode 1",
            "description": "Description 1",
            "pub_date": datetime.utcnow(),
            "episode_url": "https://example.com/ep1.mp3",
            "duration": "30:00"
        },
        {
            "title": "Episode 2",
            "description": "Description 2",
            "pub_date": datetime.utcnow(),
            "episode_url": "https://example.com/ep2.mp3",
            "duration": "45:00"
        }
    ]
    
    # Add episodes
    service = PodcastService(test_db)
    new_count = service._add_episodes_from_feed(podcast, episodes_data)
    
    assert new_count == 2
    
    # Verify episodes were added
    episodes = test_db.query(Episode).filter(Episode.podcast_id == podcast.id).all()
    assert len(episodes) == 2
