"""Realtia.cz scraper implementation (requires API key)."""

from __future__ import annotations

import os
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
    api_url: str = "https://api.realtia.cz/v1/properties"
    min_delay: float = 0.5
    max_delay: float = 1.5
    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )


@register
class RealtiaScraper(BaseScraper):
    slug = "realtia"
    name = "Realtia.cz"
    description = "Datová platforma s partnerským API (vyžaduje API klíč)."
    rate_limit_info = "Vyžaduje API klíč, limit 120 požadavků/hod."
    supports_full_scan = False

    def __init__(self) -> None:
        self._session = requests.Session()
        self._config = _Config()
        self._api_key = os.environ.get("REALTIA_API_KEY")

    def scrape(  # type: ignore[override]
        self,
        *,
        max_pages: Optional[int] = None,
        full_scan: bool = False,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> ScraperResult:
        # Použij klíč z parametru nebo z environment
        api_key = api_key or self._api_key

        result = ScraperResult()

        if not api_key:
            result.warnings.append(
                "Realtia.cz vyžaduje API klíč. Nastavte proměnnou prostředí REALTIA_API_KEY "
                "nebo předejte api_key jako parametr. Pro získání API klíče kontaktujte Realtia.cz."
            )
            return result

        max_pages = max_pages or 3

        records: Dict[str, Dict[str, object]] = {}

        try:
            offset = 0
            limit = 50

            for page in range(max_pages):
                properties = self._fetch_properties(api_key, offset, limit)
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

                offset += limit
                self._delay()

        except Exception as e:
            result.errors.append(f"Chyba při scrapování Realtia.cz: {str(e)}")

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
        return result

    def _fetch_properties(self, api_key: str, offset: int, limit: int) -> List[Dict]:
        """Načte nemovitosti z API."""
        try:
            params = {
                "offset": offset,
                "limit": limit,
                "type": "sale",  # sale, rent
            }

            headers = {
                "User-Agent": random.choice(self._config.user_agents),
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
                "X-API-Key": api_key,
            }

            response = self._session.get(
                self._config.api_url,
                params=params,
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", []) if isinstance(data, dict) else []
            else:
                return []

        except Exception:
            return []

    def _extract_agent(self, prop: Dict) -> Optional[Record]:
        """Extrahuje informace o makléři."""
        # Informace o makléři/agentovi
        agent = prop.get("agent", {}) if isinstance(prop.get("agent"), dict) else {}
        contact = prop.get("contact", {}) if isinstance(prop.get("contact"), dict) else {}

        name = agent.get("name") or contact.get("name")
        phone = contact.get("phone") or agent.get("phone")
        email = contact.get("email") or agent.get("email")
        company = agent.get("agency") or prop.get("agency")

        # Lokace
        location = prop.get("location", {}) if isinstance(prop.get("location"), dict) else {}
        city = location.get("city")
        region = location.get("region")

        # URL nemovitosti
        prop_id = prop.get("id")
        url = f"https://www.realtia.cz/nemovitost/{prop_id}" if prop_id else None

        # Detaily
        property_type = prop.get("type", "nemovitost")
        price = prop.get("price")
        description = f"Prodej {property_type}"
        if price:
            description += f" - {price} Kč"

        return {
            "zdroj": self.name,
            "jmeno_maklere": name,
            "telefon": phone,
            "email": email,
            "realitni_kancelar": company,
            "kraj": region,
            "mesto": city,
            "specializace": f"Prodej {property_type}",
            "detailni_informace": description,
            "odkazy": [url] if url else [],
        }

    def _delay(self) -> None:
        time.sleep(random.uniform(self._config.min_delay, self._config.max_delay))
