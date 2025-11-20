"""Integration tests for API endpoints."""

import pytest
from datetime import datetime

from podcast_tracker.database.models import Podcast, Episode


@pytest.mark.integration
def test_get_podcasts_empty(client):
    """Test getting podcasts when database is empty."""
    response = client.get("/api/podcasts")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
def test_get_podcasts(client, test_db, sample_podcast_data):
    """Test getting all podcasts."""
    # Add podcasts
    for i in range(3):
        podcast = Podcast(
            name=f"Podcast {i+1}",
            rss_url=f"https://example.com/feed{i+1}.xml",
            description=f"Description {i+1}"
        )
        test_db.add(podcast)
    
    test_db.commit()
    
    response = client.get("/api/podcasts")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.integration
def test_get_episodes_pagination(client, test_db, sample_podcast_data):
    """Test getting episodes with pagination."""
    # Create podcast
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    # Create episodes
    for i in range(25):
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
    
    # Get first page
    response = client.get("/api/episodes?page=1&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["episodes"]) == 10
    assert data["total"] == 25
    assert data["page"] == 1
    assert data["total_pages"] == 3


@pytest.mark.integration
def test_get_episode_by_id(client, test_db, sample_podcast_data, sample_episode_data):
    """Test getting a specific episode."""
    # Create podcast and episode
    podcast = Podcast(**sample_podcast_data)
    test_db.add(podcast)
    test_db.commit()
    test_db.refresh(podcast)
    
    episode = Episode(podcast_id=podcast.id, **sample_episode_data)
    test_db.add(episode)
    test_db.commit()
    test_db.refresh(episode)
    
    response = client.get(f"/api/episodes/{episode.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == episode.id
    assert data["title"] == episode.title


@pytest.mark.integration
def test_get_episode_not_found(client):
    """Test getting non-existent episode."""
    response = client.get("/api/episodes/999")
    
    assert response.status_code == 404


@pytest.mark.integration
def test_mark_episode_listened(client, test_db, sample_podcast_data, sample_episode_data):
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
    
    response = client.patch(
        f"/api/episodes/{episode.id}/listened",
        json={"listened": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["listened"] == True


@pytest.mark.integration
def test_filter_episodes_by_podcast(client, test_db, sample_podcast_data):
    """Test filtering episodes by podcast."""
    # Create two podcasts
    podcast1 = Podcast(**sample_podcast_data)
    test_db.add(podcast1)
    test_db.commit()
    test_db.refresh(podcast1)
    
    podcast2 = Podcast(
        name="Podcast 2",
        rss_url="https://example.com/feed2.xml",
        description="Description 2"
    )
    test_db.add(podcast2)
    test_db.commit()
    test_db.refresh(podcast2)
    
    # Create episodes for each
    for i in range(3):
        episode1 = Episode(
            podcast_id=podcast1.id,
            title=f"P1 Episode {i+1}",
            description=f"Description {i+1}",
            pub_date=datetime.utcnow(),
            episode_url=f"https://example.com/p1ep{i+1}.mp3",
            listened=False
        )
        test_db.add(episode1)
        
        episode2 = Episode(
            podcast_id=podcast2.id,
            title=f"P2 Episode {i+1}",
            description=f"Description {i+1}",
            pub_date=datetime.utcnow(),
            episode_url=f"https://example.com/p2ep{i+1}.mp3",
            listened=False
        )
        test_db.add(episode2)
    
    test_db.commit()
    
    # Filter by podcast1
    response = client.get(f"/api/episodes?podcast_id={podcast1.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert all("P1" in ep["title"] for ep in data["episodes"])
