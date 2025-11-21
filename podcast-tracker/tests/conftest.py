"""Pytest configuration and fixtures."""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set TESTING environment variable BEFORE importing app modules
os.environ["TESTING"] = "true"

# Import modules to monkeypatch
import podcast_tracker.database.database as db_module
from podcast_tracker.database.models import Base
from podcast_tracker.database.database import get_db_session
from podcast_tracker.main import app


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine and tables."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """Create a test database session."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    db_session = TestSessionLocal()
    
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(scope="function")
def client(test_db_engine):
    """Create a test client with in-memory database."""
    # Create session factory with test engine
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    
    def override_get_db_session():
        """Override the get_db_session dependency."""
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Apply the override
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    # Create test client with lif espan disabled via TESTING env var
    test_client = TestClient(app)
    
    yield test_client
    
    # Clear overrides after test
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
