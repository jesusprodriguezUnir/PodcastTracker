"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from podcast_tracker.database.models import Base
from podcast_tracker.database.database import get_db_session
from podcast_tracker.main import app


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_podcast_data():
    """Sample podcast data for testing."""
    return {
        "name": "Test Podcast",
        "rss_url": "https://example.com/feed.xml",
        "spotify_url": "https://open.spotify.com/show/test",
        "description": "A test podcast",
        "artwork_url": "https://example.com/artwork.jpg"
    }


@pytest.fixture
def sample_episode_data():
    """Sample episode data for testing."""
    from datetime import datetime
    return {
        "title": "Test Episode",
        "description": "A test episode",
        "pub_date": datetime.utcnow(),
        "duration": "30:00",
        "episode_url": "https://example.com/episode.mp3",
        "spotify_url": "https://open.spotify.com/episode/test",
        "listened": False
    }


@pytest.fixture
def mock_rss_feed():
    """Mock RSS feed data."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Podcast</title>
        <description>A test podcast</description>
        <item>
            <title>Episode 1</title>
            <description>First episode</description>
            <pubDate>Mon, 20 Nov 2023 10:00:00 GMT</pubDate>
            <link>https://example.com/episode1.mp3</link>
        </item>
    </channel>
</rss>"""
