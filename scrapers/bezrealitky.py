"""Bezrealitky.cz scraper implementation."""

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
    api_url: str = "https://www.bezrealitky.cz/api/record/markers"
    detail_url_template: str = "https://www.bezrealitky.cz/nemovitosti-byty-domy/{uri}"
    min_delay: float = 1.0
    max_delay: float = 2.5
    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    )


@register
class BezrealitkyScraper(BaseScraper):
    slug = "bezrealitky"
    name = "Bezrealitky.cz"
    description = "Moderní platforma s GraphQL API, kontakty přímo v inzerátech."
    rate_limit_info = "Doporučeno max. ~1 požadavek/sekundu, respektovat náhodné prodlevy."
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
            max_pages = None

        records: Dict[str, Dict[str, object]] = {}
        result = ScraperResult()

        # Bezrealitky používá bbox (bounding box) pro vyhledávání
        # Pro celou ČR použijeme široký bbox
        bbox = "48.5,12.0,51.1,18.9"  # Přibližné souřadnice ČR

        try:
            # Získáme všechny markery v oblasti
            markers = self._fetch_markers(bbox)
            if not markers:
                result.warnings.append("Nepodařilo se načíst data z Bezrealitky API.")
                return result

            # Limitujeme počet zpracovaných inzerátů
            limit = (max_pages * 20) if max_pages else len(markers)
            markers = markers[:limit]

            for i, marker in enumerate(markers):
                if i > 0 and i % 10 == 0:
                    self._delay()

                agent_record = self._extract_agent(marker)
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
                        "jmeno_maklere": agent_record.get("jmeno_maklere") or "Neznámý prodejce",
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

        except Exception as e:
            result.errors.append(f"Chyba při scrapování Bezrealitky: {str(e)}")
            return result

        # Převod agregovaných dat na finální formát
        for aggregated in records.values():
            aggregated["specializace"] = ", ".join(sorted(aggregated["specializace"])) or None
            aggregated["detailni_informace"] = " | ".join(aggregated["detailni_informace"]) or None
            aggregated["odkazy"] = ", ".join(dict.fromkeys(filter(None, aggregated["odkazy"]))) or None

        result.records = BaseScraper.normalise_records(records.values())
        result.metadata.update(
            {
                "platforma": self.name,
                "cas_exportu": datetime.utcnow().isoformat(),
                "celkem_prodejcu": str(len(result.records)),
            }
        )
        return result

    def _fetch_markers(self, bbox: str) -> List[Dict]:
        """Načte markery nemovitostí z API."""
        try:
            params = {
                "offerType": "prodej",  # nebo "pronajem"
                "estateType": "byt",    # byt, dum, pozemek
                "boundary": bbox,
                "includeBoundary": "false",
            }
            headers = {
                "User-Agent": random.choice(self._config.user_agents),
                "Accept": "application/json",
                "Accept-Language": "cs-CZ,cs;q=0.9",
                "Referer": "https://www.bezrealitky.cz/",
            }

            response = self._session.get(
                self._config.api_url,
                params=params,
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except Exception:
            return []

    def _extract_agent(self, marker: Dict) -> Optional[Record]:
        """Extrahuje informace o makléři/prodejci z markeru."""
        # Bezrealitky používá různé struktury, zkusíme extrahovat dostupné info
        name = marker.get("advertiserName") or marker.get("name")
        phone = marker.get("phone") or marker.get("advertiserPhone")
        email = marker.get("email") or marker.get("advertiserEmail")

        # URL inzerátu
        uri = marker.get("uri")
        url = self._config.detail_url_template.format(uri=uri) if uri else None

        # Lokace
        location = marker.get("location", {}) if isinstance(marker.get("location"), dict) else {}
        city = location.get("city") or marker.get("city")
        region = location.get("region") or marker.get("region")

        # Typ nemovitosti
        estate_type = marker.get("estateType") or marker.get("type")
        offer_type = marker.get("offerType", "prodej")

        price = marker.get("price")
        description = f"{offer_type} - {estate_type}" + (f" - {price} Kč" if price else "")

        return {
            "zdroj": self.name,
            "jmeno_maklere": name,
            "telefon": phone,
            "email": email,
            "realitni_kancelar": marker.get("company"),
            "kraj": region,
            "mesto": city,
            "specializace": f"{offer_type} {estate_type}",
            "detailni_informace": description,
            "odkazy": [url] if url else [],
        }

    def _delay(self) -> None:
        time.sleep(random.uniform(self._config.min_delay, self._config.max_delay))
