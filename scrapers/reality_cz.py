"""Reality.cz scraper (informational stub)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class RealityCzScraper(BaseScraper):
    slug = "reality-cz"
    name = "Reality.cz"
    description = "Tradiční agregátor s HTML výpisy, různé formáty detailů makléřů."
    rate_limit_info = "Bez oficiálních limitů; z praxe bezpečné ~1 požadavek/2s, respektovat robots.txt."
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
            "Reality.cz vrací data v HTML bez konzistentních selektorů. "
            "Implementace vyžaduje robustní parser (BeautifulSoup) a řešení blokací."
        )
        return result
