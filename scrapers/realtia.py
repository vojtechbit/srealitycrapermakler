"""Realtia.cz scraper (informational stub)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class RealtiaScraper(BaseScraper):
    slug = "realtia"
    name = "Realtia.cz"
    description = "Startupový projekt zaměřený na data; přístup k API pouze pro partnery."
    rate_limit_info = "Vyžaduje API klíč, dokumentace uvádí 120 požadavků/hod."
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
            "Realtia.cz poskytuje data jen autentizovaným partnerům. V této verzi chybí API klíč."
        )
        return result
