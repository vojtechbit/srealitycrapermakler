"""UlovDomov.cz scraper (informational stub)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class UlovDomovScraper(BaseScraper):
    slug = "ulovdomov"
    name = "UlovDomov.cz"
    description = "Specialista na pronájmy; web renderovaný Vue.js, API chráněné tokenem."
    rate_limit_info = "Omezení není zveřejněno, doporučeno max. 1 požadavek/sekundu s validním tokenem."
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
            "UlovDomov.cz používá dynamická API volání s CSRF tokeny. Aktuálně není implementováno přihlášení ani parsování."
        )
        return result
