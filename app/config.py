from __future__ import annotations

from datetime import timedelta
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or defaults.

    This centralizes configuration for maintainability and testability.
    """

    app_name: str = "NLP Portfolio API"

    # Networking and timeouts
    http_timeout_seconds: int = 10
    http_user_agent: str = (
        "nlp-portfolio/1.0 (+https://github.com/tommywood81/nlp_project)"
    )

    # RSS Feeds (ABC Australia)
    abc_feeds: Dict[str, AnyHttpUrl] = Field(
        default={
            "top_stories": "https://www.abc.net.au/news/feed/51120/rss.xml",
            "australia": "https://www.abc.net.au/news/feed/51892/rss.xml",
            "just_in": "https://www.abc.net.au/news/feed/52498/rss.xml",
        }
    )

    # Cache TTL for feed results (seconds)
    rss_cache_ttl_seconds: int = 600  # 10 minutes

    @property
    def rss_cache_ttl(self) -> timedelta:
        return timedelta(seconds=self.rss_cache_ttl_seconds)


settings = Settings()
