"""Bezrealitky.cz scraper (informational stub)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class BezrealitkyScraper(BaseScraper):
    slug = "bezrealitky"
    name = "Bezrealitky.cz"
    description = "Moderní platforma; veřejné API není zdokumentováno, vyžaduje reverzní inženýrství."
    rate_limit_info = "Oficiální limity nezveřejňuje, doporučeno max. ~1 požadavek/sekundu s API tokenem."
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
            "Bezrealitky.cz vyžaduje autorizované API volání s dynamickými tokeny a reCAPTCHA. "
            "V této verzi je scraper pouze připraven v registru – je potřeba doplnit mechaniku přihlášení."
        )
        return result
