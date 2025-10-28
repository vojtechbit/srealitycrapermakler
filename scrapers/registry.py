"""Registry of supported scrapers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Type

from .base import BaseScraper


_SCRAPERS: Dict[str, Type[BaseScraper]] = {}


def register(scraper_cls: Type[BaseScraper]) -> Type[BaseScraper]:
    """Class decorator registering scraper implementations."""

    if scraper_cls.slug in _SCRAPERS:
        raise ValueError(f"Scraper '{scraper_cls.slug}' is already registered")
    _SCRAPERS[scraper_cls.slug] = scraper_cls
    return scraper_cls


def get_scraper(slug: str) -> BaseScraper:
    try:
        return _SCRAPERS[slug]()
    except KeyError as exc:
        raise KeyError(f"Neznámá platforma: {slug}") from exc


def list_scrapers() -> List[BaseScraper]:
    return [cls() for cls in _SCRAPERS.values()]


# Import side effects registering concrete scrapers.
from . import sreality  # noqa: E402,F401

# Ostatní scrapery jsou dočasně skryté - pro budoucí použití odkomentuj níže:
# from . import bezrealitky, reality_idnes, reality_cz, realtia, ulovdomov, linkedin, registr_osvc  # noqa: E402,F401
