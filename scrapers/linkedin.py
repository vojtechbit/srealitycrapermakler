"""LinkedIn scraper (informational stub)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class LinkedInScraper(BaseScraper):
    slug = "linkedin"
    name = "LinkedIn"
    description = "Vyhledávání profesionálů, ale proti scrapingu aktivně zasahuje."
    rate_limit_info = "Přísné – vyžaduje oficiální API (s OAuth) nebo Sales Navigator."
    supports_full_scan = False

    def scrape(  # type: ignore[override]
        self,
        *,
        max_pages: Optional[int] = None,
        full_scan: bool = False,
        **_: object,
    ) -> ScraperResult:
        result = ScraperResult()
        result.warnings.append(
            "LinkedIn má přísné podmínky a vyžaduje autentizaci. Doporučeno použít oficiální API nebo manuální export."
        )
        return result
