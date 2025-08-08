from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

import feedparser
import requests
from newspaper import Article

from app.config import settings


@dataclass
class NewsArticle:
    title: str
    link: str
    published: str
    summary: str
    full_text: Optional[str] = None


class InMemoryCache:
    """Very small in-process cache with TTL.

    This is intentionally simple; replace with Redis/Memcache for multi-process deployments.
    """

    def __init__(self) -> None:
        self._value = None
        self._expiry_epoch = 0.0

    def get(self):
        if self._value is not None and time.time() < self._expiry_epoch:
            return self._value
        return None

    def set(self, value, ttl_seconds: int) -> None:
        self._value = value
        self._expiry_epoch = time.time() + ttl_seconds


_feed_cache = InMemoryCache()


def fetch_abc_feed(feed_name: str = "top_stories", full_text: bool = False) -> List[NewsArticle]:
    """Fetch and parse ABC RSS feed.

    Args:
        feed_name: Key into settings.abc_feeds mapping
        full_text: If True, attempt to fetch and parse the full article text for each item

    Returns:
        List of NewsArticle items

    Raises:
        ValueError: if feed_name is invalid
        RuntimeError: for network/parse failures
    """
    cached = _feed_cache.get()
    if cached is not None:
        return cached

    feed_url = settings.abc_feeds.get(feed_name)
    if not feed_url:
        raise ValueError(f"Invalid feed name: {feed_name}")

    try:
        # Use feedparser directly; it will perform HTTP get
        parsed = feedparser.parse(str(feed_url))
        articles: List[NewsArticle] = []
        for entry in parsed.entries:
            article = NewsArticle(
                title=getattr(entry, "title", ""),
                link=getattr(entry, "link", ""),
                published=getattr(entry, "published", ""),
                summary=getattr(entry, "summary", ""),
            )
            if full_text and article.link:
                try:
                    # Fetching full text can be heavy; protect with timeout and UA
                    art = Article(article.link)
                    art.download()
                    art.parse()
                    article.full_text = art.text or None
                except Exception:
                    article.full_text = None
            articles.append(article)

        _feed_cache.set(articles, settings.rss_cache_ttl_seconds)
        return articles
    except (requests.RequestException, Exception) as exc:  # pragma: no cover - feedparser may swallow requests exceptions
        raise RuntimeError(f"Failed to fetch or parse feed: {exc}")
