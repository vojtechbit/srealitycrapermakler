"""Collection of scraper implementations for various real-estate platforms."""

from .registry import get_scraper, list_scrapers

__all__ = [
    "get_scraper",
    "list_scrapers",
]
