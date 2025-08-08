from __future__ import annotations

import types
from app.services.news_feed import fetch_abc_feed


class DummyEntry:
    def __init__(self, title: str, link: str, published: str, summary: str):
        self.title = title
        self.link = link
        self.published = published
        self.summary = summary


def test_fetch_abc_feed_parses_entries(monkeypatch):
    # Arrange a fake feedparser.parse
    dummy_result = types.SimpleNamespace(entries=[
        DummyEntry("Title 1", "https://example.org/a1", "2025-01-01", "<p>Summary</p>"),
        DummyEntry("Title 2", "https://example.org/a2", "2025-01-02", "<p>Summary2</p>"),
    ])

    def fake_parse(url: str):  # noqa: ARG001
        return dummy_result

    monkeypatch.setattr("app.services.news_feed.feedparser.parse", fake_parse)

    # Act
    articles = fetch_abc_feed(feed_name="top_stories", full_text=False)

    # Assert
    assert len(articles) == 2
    assert articles[0].title == "Title 1"
    assert articles[0].link.startswith("https://example.org/")
    assert "Summary" in articles[0].summary


def test_invalid_feed_name_raises():
    try:
        fetch_abc_feed(feed_name="nope", full_text=False)
        assert False, "Expected ValueError"
    except ValueError:
        pass
