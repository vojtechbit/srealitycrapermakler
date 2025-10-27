"""Registr OSVČ scraper (public register stub)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class RegistrOsvcScraper(BaseScraper):
    slug = "registr-osvc"
    name = "Registr živnostenského podnikání"
    description = "Státní registr OSVČ – ověření živnostníků v oboru realitní zprostředkovatel."
    rate_limit_info = "Veřejné API umožňuje ~100 požadavků/min, ale doporučeno je méně kvůli stabilitě."
    supports_full_scan = False

    def scrape(  # type: ignore[override]
        self,
        *,
        query: Optional[str] = None,
        ico: Optional[str] = None,
        max_pages: Optional[int] = None,
        full_scan: bool = False,
        **_: object,
    ) -> ScraperResult:
        result = ScraperResult()
        if not query and not ico:
            result.warnings.append(
                "Registr živnostenského podnikání vyžaduje konkrétní dotaz (jméno nebo IČO). "
                "Předejte parametr 'query' nebo 'ico'."
            )
            return result

        result.warnings.append(
            "Implementace dotazu na RŽP chybí – API vrací XML, je potřeba doplnit SOAP klienta."
        )
        return result
