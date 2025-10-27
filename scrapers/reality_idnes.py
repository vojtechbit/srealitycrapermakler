"""Reality.iDNES.cz scraper implementation."""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, Record, ScraperResult
from .registry import register


@dataclass
class _Config:
    base_url: str = "https://reality.idnes.cz"
    search_url: str = f"{base_url}/s/prodej/byty"
    min_delay: float = 2.0
    max_delay: float = 4.0
    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    )


@register
class RealityIdnesScraper(BaseScraper):
    slug = "reality-idnes"
    name = "Reality.iDNES.cz"
    description = "Mediální portál iDNES, HTML parsing s anti-bot ochranou."
    rate_limit_info = "Doporučeno méně než 30 požadavků/min, respektovat User-Agent."
    supports_full_scan = True

    def __init__(self) -> None:
        self._session = requests.Session()
        self._config = _Config()

    def scrape(  # type: ignore[override]
        self,
        *,
        max_pages: Optional[int] = None,
        full_scan: bool = False,
        **kwargs,
    ) -> ScraperResult:
        if full_scan:
            max_pages = 5  # Omezíme kvůli anti-bot ochraně

        max_pages = max_pages or 2

        records: Dict[str, Dict[str, object]] = {}
        result = ScraperResult()

        try:
            for page in range(1, max_pages + 1):
                listings = self._fetch_page(page)
                if not listings:
                    break

                for listing in listings:
                    agent_record = self._extract_agent(listing)
                    if not agent_record:
                        continue

                    # Klíč pro deduplicitu
                    key = (
                        agent_record.get("jmeno_maklere"),
                        agent_record.get("telefon"),
                        agent_record.get("email"),
                        agent_record.get("realitni_kancelar"),
                    )
                    key_str = "|".join(str(v) if v else "" for v in key)

                    aggregated = records.setdefault(
                        key_str,
                        {
                            "zdroj": self.name,
                            "jmeno_maklere": agent_record.get("jmeno_maklere") or "Neznámý makléř",
                            "telefon": agent_record.get("telefon"),
                            "email": agent_record.get("email"),
                            "realitni_kancelar": agent_record.get("realitni_kancelar"),
                            "kraj": agent_record.get("kraj"),
                            "mesto": agent_record.get("mesto"),
                            "specializace": set(),
                            "detailni_informace": [],
                            "odkazy": [],
                        },
                    )

                    if agent_record.get("specializace"):
                        aggregated["specializace"].add(agent_record["specializace"])
                    if agent_record.get("detailni_informace"):
                        aggregated["detailni_informace"].append(agent_record["detailni_informace"])
                    if agent_record.get("odkazy"):
                        aggregated["odkazy"].extend(agent_record["odkazy"])

                self._delay()

        except Exception as e:
            result.errors.append(f"Chyba při scrapování Reality.iDNES.cz: {str(e)}")

        # Převod agregovaných dat
        for aggregated in records.values():
            aggregated["specializace"] = ", ".join(sorted(aggregated["specializace"])) or None
            aggregated["detailni_informace"] = " | ".join(aggregated["detailni_informace"]) or None
            aggregated["odkazy"] = ", ".join(dict.fromkeys(filter(None, aggregated["odkazy"]))) or None

        result.records = BaseScraper.normalise_records(records.values())
        result.metadata.update(
            {
                "platforma": self.name,
                "cas_exportu": datetime.utcnow().isoformat(),
                "celkem_makleru": str(len(result.records)),
            }
        )

        if not result.records:
            result.warnings.append(
                "Nepodařilo se získat žádné záznamy. Reality.iDNES.cz může používat "
                "pokročilou anti-bot ochranu nebo se změnila struktura stránky."
            )

        return result

    def _fetch_page(self, page: int) -> List[Dict]:
        """Načte stránku s výsledky."""
        try:
            url = f"{self._config.search_url}?page={page}"
            headers = {
                "User-Agent": random.choice(self._config.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "cs-CZ,cs;q=0.9",
                "Referer": self._config.base_url,
            }

            response = self._session.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, "html.parser")
            listings = []

            # Reality.iDNES používá různé struktury - hledáme různé varianty
            # Hledáme článkové elementy nebo div elementy s inzeráty
            selectors = [
                {"name": ["article"], "class_": re.compile(r"(c-products|product|listing|item)", re.I)},
                {"name": ["div"], "class_": re.compile(r"(c-products__item|product-item|listing-item)", re.I)},
            ]

            for selector in selectors:
                items = soup.find_all(**selector)
                if items:
                    for item in items:
                        listing_data = self._parse_listing_item(item)
                        if listing_data:
                            listings.append(listing_data)
                    break

            return listings

        except Exception:
            return []

    def _parse_listing_item(self, item) -> Optional[Dict]:
        """Parsuje jednotlivý inzerát."""
        try:
            listing_data = {}

            # Název/titulek
            title_elem = item.find(["h2", "h3"], class_=re.compile(r"(title|heading|name)", re.I))
            if not title_elem:
                title_elem = item.find("a", class_=re.compile(r"(title|heading)", re.I))
            if title_elem:
                listing_data["title"] = title_elem.get_text(strip=True)

            # Odkaz
            link_elem = item.find("a", href=True)
            if link_elem and link_elem.get("href"):
                listing_data["url"] = urljoin(self._config.base_url, link_elem["href"])

            # Lokace
            location_elem = item.find(class_=re.compile(r"(locality|location|address)", re.I))
            if location_elem:
                listing_data["location"] = location_elem.get_text(strip=True)

            # Makléř/RK
            agent_elem = item.find(class_=re.compile(r"(seller|agency|broker|realtor)", re.I))
            if agent_elem:
                listing_data["agent"] = agent_elem.get_text(strip=True)

            # Kontakty - telefon
            phone_elem = item.find(class_=re.compile(r"(phone|tel)", re.I))
            if phone_elem:
                listing_data["phone"] = self._clean_phone(phone_elem.get_text(strip=True))

            # Email
            email_elem = item.find("a", href=re.compile(r"^mailto:", re.I))
            if email_elem:
                listing_data["email"] = email_elem["href"].replace("mailto:", "")

            return listing_data if listing_data else None

        except Exception:
            return None

    def _extract_agent(self, listing: Dict) -> Optional[Record]:
        """Extrahuje informace o makléři z inzerátu."""
        # Parsování lokace
        location = listing.get("location", "")
        parts = [p.strip() for p in location.split(",") if p.strip()]
        city = parts[0] if parts else None
        region = parts[-1] if len(parts) > 1 else None

        return {
            "zdroj": self.name,
            "jmeno_maklere": listing.get("agent"),
            "telefon": listing.get("phone"),
            "email": listing.get("email"),
            "realitni_kancelar": None,
            "kraj": region,
            "mesto": city,
            "specializace": "Prodej nemovitostí",
            "detailni_informace": listing.get("title"),
            "odkazy": [listing.get("url")] if listing.get("url") else [],
        }

    def _clean_phone(self, phone: str) -> Optional[str]:
        """Vyčistí telefonní číslo."""
        if not phone:
            return None
        cleaned = re.sub(r"[^\d+\s]", "", phone)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned if cleaned else None

    def _delay(self) -> None:
        time.sleep(random.uniform(self._config.min_delay, self._config.max_delay))
