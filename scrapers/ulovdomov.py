"""UlovDomov.cz scraper implementation."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import requests

from .base import BaseScraper, Record, ScraperResult
from .registry import register


@dataclass
class _Config:
    api_url: str = "https://www.ulovdomov.cz/api/v1/properties/search"
    base_url: str = "https://www.ulovdomov.cz"
    min_delay: float = 1.0
    max_delay: float = 2.0
    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    )


@register
class UlovDomovScraper(BaseScraper):
    slug = "ulovdomov"
    name = "UlovDomov.cz"
    description = "Specialista na pronájmy, API pro vyhledávání nemovitostí."
    rate_limit_info = "Doporučeno max. 1 požadavek/sekundu."
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
            max_pages = 10

        max_pages = max_pages or 3

        records: Dict[str, Dict[str, object]] = {}
        result = ScraperResult()

        try:
            offset = 0
            limit = 20

            for page in range(max_pages):
                properties = self._fetch_properties(offset, limit)
                if not properties:
                    break

                for prop in properties:
                    agent_record = self._extract_agent(prop)
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
                            "jmeno_maklere": agent_record.get("jmeno_maklere") or "Neznámý pronajímatel",
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

                offset += limit
                self._delay()

        except Exception as e:
            result.errors.append(f"Chyba při scrapování UlovDomov.cz: {str(e)}")

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
                "celkem_pronajímatelu": str(len(result.records)),
            }
        )
        return result

    def _fetch_properties(self, offset: int, limit: int) -> List[Dict]:
        """Načte nemovitosti z API."""
        try:
            payload = {
                "filters": {
                    "propertyType": "flat",  # flat, house, room
                    "offerType": "rent",     # rent, sale
                },
                "offset": offset,
                "limit": limit,
            }

            headers = {
                "User-Agent": random.choice(self._config.user_agents),
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Accept-Language": "cs-CZ,cs;q=0.9",
            }

            response = self._session.post(
                self._config.api_url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("properties", []) if isinstance(data, dict) else []
            else:
                return []

        except Exception:
            return []

    def _extract_agent(self, prop: Dict) -> Optional[Record]:
        """Extrahuje informace o pronajímateli."""
        # Informace o vlastníkovi/pronajímateli
        owner = prop.get("owner", {}) if isinstance(prop.get("owner"), dict) else {}
        contact = prop.get("contact", {}) if isinstance(prop.get("contact"), dict) else {}

        name = owner.get("name") or contact.get("name")
        phone = contact.get("phone") or owner.get("phone")
        email = contact.get("email") or owner.get("email")
        company = owner.get("company")

        # Lokace
        location = prop.get("location", {}) if isinstance(prop.get("location"), dict) else {}
        city = location.get("city") or prop.get("city")
        region = location.get("region") or prop.get("region")

        # URL nemovitosti
        prop_id = prop.get("id") or prop.get("propertyId")
        url = f"{self._config.base_url}/nemovitost/{prop_id}" if prop_id else None

        # Detaily
        property_type = prop.get("propertyType", "flat")
        price = prop.get("price")
        title = prop.get("title") or prop.get("name")
        description = f"Pronájem {property_type}"
        if price:
            description += f" - {price} Kč/měsíc"
        if title:
            description += f" - {title}"

        return {
            "zdroj": self.name,
            "jmeno_maklere": name,
            "telefon": phone,
            "email": email,
            "realitni_kancelar": company,
            "kraj": region,
            "mesto": city,
            "specializace": f"Pronájem {property_type}",
            "detailni_informace": description,
            "odkazy": [url] if url else [],
        }

    def _delay(self) -> None:
        time.sleep(random.uniform(self._config.min_delay, self._config.max_delay))
