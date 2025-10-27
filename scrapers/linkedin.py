"""LinkedIn scraper (informational - not functional without authentication)."""

from __future__ import annotations

from typing import Optional

from .base import BaseScraper, ScraperResult
from .registry import register


@register
class LinkedInScraper(BaseScraper):
    slug = "linkedin"
    name = "LinkedIn"
    description = "NEFUNKČNÍ - LinkedIn aktivně blokuje scraping. Vyžaduje API nebo manuální export."
    rate_limit_info = "Přísné – aktivně detekuje boty, vyžaduje OAuth API nebo Sales Navigator."
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
            "⚠️  LinkedIn aktivně BLOKUJE scraping a může zablokovat váš účet!"
        )
        result.warnings.append(
            "LinkedIn používá pokročilou anti-bot ochranu (Akamai, CAPTCHA, device fingerprinting)."
        )
        result.warnings.append(
            "\nDoporučené alternativy:"
        )
        result.warnings.append(
            "  1. LinkedIn API s OAuth autentizací (vyžaduje schválení od LinkedIn)"
        )
        result.warnings.append(
            "  2. LinkedIn Sales Navigator (placená verze s export funkcí)"
        )
        result.warnings.append(
            "  3. Manuální vyhledávání a export kontaktů přímo z LinkedIn"
        )
        result.warnings.append(
            "  4. LinkedIn Recruiter Lite pro recruiting účely"
        )
        result.warnings.append(
            "\nTechnické důvody, proč scraping nefunguje:"
        )
        result.warnings.append(
            "  • Vyžaduje přihlášení s 2FA"
        )
        result.warnings.append(
            "  • Detekuje automatizované nástroje (Selenium, Puppeteer)"
        )
        result.warnings.append(
            "  • Používá dynamický JavaScript (React) - data nejsou v HTML"
        )
        result.warnings.append(
            "  • Rate limiting a IP blacklisting"
        )
        result.warnings.append(
            "  • Porušení Terms of Service může vést k trvalému zablokování účtu"
        )
        return result
