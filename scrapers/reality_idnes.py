"""Reality.iDNES.cz scraper (informational stub)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class RealityIdnesScraper(BaseScraper):
    slug = "reality-idnes"
    name = "Reality.iDNES.cz"
    description = "Silný mediální portál, stránkování HTML, agresivní ochrany proti botům."
    rate_limit_info = "Doporučeno méně než 30 požadavků/min, kontrolují User-Agent a cookies."
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
            "Reality.iDNES.cz používá dynamický JavaScript a anti-bot prvky (Akami/Arkose). "
            "Scraper je zatím pouze definován, je nutné doplnit vykreslení přes prohlížeč nebo API."
        )
        return result
