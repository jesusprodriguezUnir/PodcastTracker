"""Unit tests for RSS parser."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from podcast_tracker.services.rss_parser import RSSParser


@pytest.mark.unit
def test_parse_feed_success():
    """Test successful RSS feed parsing."""
    mock_feed = MagicMock()
    mock_feed.bozo = False
    # Use a dict-like object for feed that supports .get() method
    mock_feed.feed = {
        "title": "Test Podcast",
        "description": "Test Description"
    }
    
    # Create a proper mock entry with get() support
    mock_entry = MagicMock()
    mock_entry.published = "Mon, 20 Nov 2023 10:00:00 GMT"
    mock_entry.get.side_effect = lambda key, default="": {
        "title": "Episode 1",
        "summary": "Episode description",
        "link": "https://example.com/episode1.mp3"
    }.get(key, default)
    mock_entry.enclosures = []
    
    mock_feed.entries = [mock_entry]
    
    with patch('feedparser.parse', return_value=mock_feed):
        parser = RSSParser()
        result = parser.parse_feed("https://example.com/feed.xml")
        
        assert result is not None
        assert result["title"] == "Test Podcast"
        assert result["description"] == "Test Description"
        assert len(result["episodes"]) == 1
        assert result["episodes"][0]["title"] == "Episode 1"


@pytest.mark.unit
def test_parse_feed_invalid():
    """Test parsing invalid RSS feed."""
    mock_feed = MagicMock()
    mock_feed.bozo = True
    delattr(mock_feed, 'feed')
    
    with patch('feedparser.parse', return_value=mock_feed):
        parser = RSSParser()
        result = parser.parse_feed("https://example.com/invalid.xml")
        
        assert result is None


@pytest.mark.unit
def test_parse_episode_with_duration():
    """Test parsing episode with duration."""
    mock_entry = MagicMock()
    mock_entry.title = "Episode with duration"
    mock_entry.summary = "Description"
    mock_entry.published = "Mon, 20 Nov 2023 10:00:00 GMT"
    mock_entry.link = "https://example.com/episode.mp3"
    mock_entry.itunes_duration = "45:30"
    mock_entry.enclosures = []
    
    parser = RSSParser()
    result = parser._parse_episode(mock_entry)
    
    assert result is not None
    assert result["duration"] == "45:30"


@pytest.mark.unit
def test_parse_episode_without_pub_date():
    """Test parsing episode without publication date."""
    mock_entry = MagicMock()
    mock_entry.title = "Episode"
    mock_entry.summary = "Description"
    mock_entry.link = "https://example.com/episode.mp3"
    mock_entry.enclosures = []
    
    # Remove published and updated attributes
    delattr(mock_entry, 'published')
    delattr(mock_entry, 'updated')
    
    parser = RSSParser()
    result = parser._parse_episode(mock_entry)
    
    assert result is not None
    assert isinstance(result["pub_date"], datetime)


@pytest.mark.unit
def test_extract_artwork():
    """Test artwork extraction."""
    mock_feed = MagicMock()
    mock_feed.image = {"href": "https://example.com/artwork.jpg"}
    
    parser = RSSParser()
    artwork = parser._extract_artwork(mock_feed)
    
    assert artwork == "https://example.com/artwork.jpg"


@pytest.mark.unit
def test_extract_artwork_none():
    """Test artwork extraction when none available."""
    mock_feed = MagicMock()
    delattr(mock_feed, 'image')
    
    parser = RSSParser()
    artwork = parser._extract_artwork(mock_feed)
    
    assert artwork is None
