from __future__ import annotations

import pytest
import types
from unittest.mock import Mock, patch
from app.services.news_feed import fetch_abc_feed, NewsArticle


class DummyEntry:
    """Mock RSS feed entry for testing"""
    def __init__(self, title: str, link: str, published: str, summary: str):
        self.title = title
        self.link = link
        self.published = published
        self.summary = summary


@pytest.mark.unit
class TestNewsFeed:
    """Test suite for news feed functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.dummy_entries = [
            DummyEntry(
                "Test Article 1", 
                "https://example.org/a1", 
                "2025-01-01", 
                "<p>This is a test summary for article 1</p>"
            ),
            DummyEntry(
                "Test Article 2", 
                "https://example.org/a2", 
                "2025-01-02", 
                "<p>This is a test summary for article 2</p>"
            ),
        ]
    
    def test_fetch_abc_feed_parses_entries(self, monkeypatch):
        """Test that feed parsing works correctly"""
        # Arrange a fake feedparser.parse
        dummy_result = types.SimpleNamespace(entries=self.dummy_entries)

        def fake_parse(url: str):  # noqa: ARG001
            return dummy_result

        monkeypatch.setattr("app.services.news_feed.feedparser.parse", fake_parse)

        # Act
        articles = fetch_abc_feed(feed_name="top_stories", full_text=False)

        # Assert
        assert len(articles) == 2
        assert articles[0].title == "Test Article 1"
        assert articles[0].link.startswith("https://example.org/")
        assert "test summary" in articles[0].summary.lower()
        assert articles[1].title == "Test Article 2"
    
    def test_fetch_abc_feed_with_full_text(self, monkeypatch):
        """Test fetching feed with full text extraction"""
        # Mock the Article class
        mock_article = Mock()
        mock_article.text = "This is the full article text content."
        
        with patch('app.services.news_feed.Article', return_value=mock_article):
            # Arrange
            dummy_result = types.SimpleNamespace(entries=self.dummy_entries)
            
            def fake_parse(url: str):  # noqa: ARG001
                return dummy_result
            
            monkeypatch.setattr("app.services.news_feed.feedparser.parse", fake_parse)
            
            # Act
            articles = fetch_abc_feed(feed_name="top_stories", full_text=True)
            
            # Assert
            assert len(articles) == 2
            assert articles[0].full_text == "This is the full article text content."
            assert articles[1].full_text == "This is the full article text content."
    
    def test_fetch_abc_feed_full_text_failure(self, monkeypatch):
        """Test handling of full text extraction failure"""
        # Mock the Article class to raise an exception
        with patch('app.services.news_feed.Article', side_effect=Exception("Download failed")):
            # Arrange
            dummy_result = types.SimpleNamespace(entries=self.dummy_entries)
            
            def fake_parse(url: str):  # noqa: ARG001
                return dummy_result
            
            monkeypatch.setattr("app.services.news_feed.feedparser.parse", fake_parse)
            
            # Act
            articles = fetch_abc_feed(feed_name="top_stories", full_text=True)
            
            # Assert
            assert len(articles) == 2
            assert articles[0].full_text is None
            assert articles[1].full_text is None
    
    def test_invalid_feed_name_raises_value_error(self):
        """Test that invalid feed names raise ValueError"""
        with pytest.raises(ValueError, match="Invalid feed name"):
            fetch_abc_feed(feed_name="invalid_feed_name", full_text=False)
    
    def test_valid_feed_names(self):
        """Test that valid feed names are accepted"""
        valid_feeds = ["top_stories", "australia", "just_in"]
        
        for feed_name in valid_feeds:
            # This will fail due to network issues, but should not raise ValueError
            try:
                fetch_abc_feed(feed_name=feed_name, full_text=False)
            except Exception as e:
                # Should not be ValueError for valid feed names
                assert not isinstance(e, ValueError)
    
    def test_article_structure(self, monkeypatch):
        """Test that articles have the correct structure"""
        # Arrange
        dummy_result = types.SimpleNamespace(entries=self.dummy_entries)
        
        def fake_parse(url: str):  # noqa: ARG001
            return dummy_result
        
        monkeypatch.setattr("app.services.news_feed.feedparser.parse", fake_parse)
        
        # Act
        articles = fetch_abc_feed(feed_name="top_stories", full_text=False)
        
        # Assert
        assert len(articles) > 0
        for article in articles:
            assert isinstance(article, NewsArticle)
            assert hasattr(article, 'title')
            assert hasattr(article, 'link')
            assert hasattr(article, 'published')
            assert hasattr(article, 'summary')
            assert hasattr(article, 'full_text')
            assert isinstance(article.title, str)
            assert isinstance(article.link, str)
            assert len(article.title) > 0
    
    def test_empty_feed_handling(self, monkeypatch):
        """Test handling of empty RSS feeds"""
        # Arrange empty feed
        dummy_result = types.SimpleNamespace(entries=[])
        
        def fake_parse(url: str):  # noqa: ARG001
            return dummy_result
        
        monkeypatch.setattr("app.services.news_feed.feedparser.parse", fake_parse)
        
        # Act
        articles = fetch_abc_feed(feed_name="top_stories", full_text=False)
        
        # Assert
        assert len(articles) == 0
        assert isinstance(articles, list)
    
    def test_missing_optional_fields(self, monkeypatch):
        """Test handling of entries with missing optional fields"""
        # Create entries with missing optional fields
        incomplete_entries = [
            DummyEntry("Title Only", "https://example.org/t1", "", ""),
            DummyEntry("No Published Date", "https://example.org/t2", "", "Summary here"),
        ]
        
        dummy_result = types.SimpleNamespace(entries=incomplete_entries)
        
        def fake_parse(url: str):  # noqa: ARG001
            return dummy_result
        
        monkeypatch.setattr("app.services.news_feed.feedparser.parse", fake_parse)
        
        # Act
        articles = fetch_abc_feed(feed_name="top_stories", full_text=False)
        
        # Assert
        assert len(articles) == 2
        assert articles[0].title == "Title Only"
        assert articles[0].published == ""
        assert articles[0].summary == ""
        assert articles[1].title == "No Published Date"
        assert articles[1].published == ""
        assert articles[1].summary == "Summary here"
