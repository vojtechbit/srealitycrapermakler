"""Sreality.cz scraper implementation."""

from __future__ import annotations

import random
import re
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse

import requests

from .base import BaseScraper, Record, ScraperResult
from .registry import register


@dataclass
class _Config:
    base_url: str = "https://www.sreality.cz"
    api_url: str = f"{base_url}/api/cs/v2/estates"
    min_delay: float = 1.0
    max_delay: float = 3.0
    category_main = {1: "Byty", 2: "Domy", 3: "Pozemky", 4: "Komerční", 5: "Ostatní"}
    category_type = {1: "Prodej", 2: "Pronájem", 3: "Dražby"}
    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    )


def _normalise_url(value: Optional[str]) -> Optional[str]:
    if not value or not isinstance(value, str):
        return None

    candidate = value.strip()
    if not candidate:
        return None

    if candidate.startswith("//"):
        candidate = f"https:{candidate}"

    if candidate.startswith("detail/"):
        candidate = f"/{candidate}"

    if candidate.startswith("/"):
        candidate = urljoin(_Config.base_url + "/", candidate.lstrip("/"))

    if not candidate.startswith("http"):
        return None

    parsed = urlparse(candidate)
    if not parsed.netloc or not parsed.netloc.endswith("sreality.cz"):
        return None

    if "/api/" in candidate or "/cs/v2/estates" in candidate:
        return None

    if "/detail/" not in candidate:
        return None

    return candidate


def _slugify_locality(value: Optional[str]) -> Optional[str]:
    if not value or not isinstance(value, str):
        return None

    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.lower()
    ascii_value = re.sub(r"[^a-z0-9]+", "-", ascii_value)
    ascii_value = re.sub(r"-+", "-", ascii_value)
    ascii_value = ascii_value.strip("-")
    return ascii_value or None


@register
class SrealityScraper(BaseScraper):
    slug = "sreality"
    name = "Sreality.cz"
    description = "Oficiální API, detailní kontakty, vyžaduje pomalé tempo požadavků."
    rate_limit_info = "~60 detailů/min, respektovat náhodné prodlevy a reagovat na HTTP 429."
    supports_full_scan = True

    def __init__(self) -> None:
        self._session = requests.Session()
        self._config = _Config()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def scrape(  # type: ignore[override]
        self,
        *,
        category_main: int = 1,
        category_type: int = 1,
        locality_region_id: Optional[int] = None,
        max_pages: Optional[int] = None,
        full_scan: bool = False,
        fetch_details: bool = True,
    ) -> ScraperResult:
        if full_scan:
            max_pages = None

        limit = max_pages if max_pages is not None else None
        records: Dict[str, Dict[str, object]] = {}
        result = ScraperResult()

        page = 1
        while True:
            if limit is not None and page > limit:
                break

            params = {
                "category_main_cb": category_main,
                "category_type_cb": category_type,
                "page": page,
                "per_page": 60,
            }

            if locality_region_id is not None:
                params["locality_region_id"] = locality_region_id

            payload = self._request(self._config.api_url, params=params)
            if not payload:
                result.errors.append("Chyba při komunikaci se Sreality API (možná blokace).")
                break

            estates = payload.get("_embedded", {}).get("estates", [])
            if not estates:
                break

            for estate in estates:
                if fetch_details:
                    detail = self._fetch_detail(estate)
                else:
                    detail = estate

                if not detail:
                    continue

                agent_record = self._extract_agent(detail, estate)
                if not agent_record:
                    continue

                key = agent_record["jmeno_maklere"], agent_record.get("telefon"), agent_record.get("email"), agent_record.get("realitni_kancelar")
                key_str = "|".join(value or "" for value in key)

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

            result_size = payload.get("result_size", 0)
            if (page * 60) >= result_size:
                break

            page += 1
            self._delay()

        for aggregated in records.values():
            aggregated["specializace"] = ", ".join(sorted(aggregated["specializace"])) or None
            aggregated["detailni_informace"] = " | ".join(aggregated["detailni_informace"]) or None
            aggregated["odkazy"] = ", ".join(dict.fromkeys(filter(None, aggregated["odkazy"])) or []) or None

        result.records = BaseScraper.normalise_records(records.values())
        result.metadata.update(
            {
                "platforma": self.name,
                "cas_exportu": datetime.utcnow().isoformat(),
                "celkem_makleru": str(len(result.records)),
                "kategorie": self._config.category_main.get(category_main, "Neznámé"),
                "typ": self._config.category_type.get(category_type, "Neznámé"),
            }
        )
        return result

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _request(self, url: str, *, params: Optional[Dict[str, object]] = None, retries: int = 3) -> Optional[Dict]:
        for attempt in range(retries):
            try:
                headers = {
                    "User-Agent": random.choice(self._config.user_agents),
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
                    "Referer": "https://www.sreality.cz/",
                }
                response = self._session.get(url, params=params, headers=headers, timeout=30)
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 429:
                    wait_time = (2 ** attempt) * 5
                    time.sleep(wait_time)
                    continue
            except Exception:
                if attempt == retries - 1:
                    return None
                time.sleep(2 ** attempt)
        return None

    def _delay(self) -> None:
        time.sleep(random.uniform(self._config.min_delay, self._config.max_delay))

    def _fetch_detail(self, estate: Dict) -> Optional[Dict]:
        hash_id = estate.get("hash_id")
        if not hash_id:
            return estate
        detail_url = f"{self._config.base_url}/api/cs/v2/estates/{hash_id}"
        detail = self._request(detail_url)
        if detail:
            self._delay()
        return detail or estate

    def _extract_agent(self, detail: Dict, estate: Dict) -> Optional[Record]:
        embedded = detail.get("_embedded", {})
        seller = embedded.get("seller") or {}
        company = embedded.get("company") or {}
        broker = embedded.get("broker") or {}

        agent_name = (
            seller.get("user_name")
            or seller.get("name")
            or broker.get("user_name")
            or broker.get("name")
        )

        company_name = (
            seller.get("company_name")
            or seller.get("company", {}).get("name")
            or seller.get("organization", {}).get("name")
            or company.get("name")
            or company.get("company_name")
        )

        phone = self._first_phone(detail) or self._first_phone(estate)
        email = self._first_email(detail) or self._first_email(estate)

        estate_url = self._extract_url(detail) or self._extract_url(estate)
        estate_name = estate.get("name")
        locality = estate.get("locality", "") or ""

        return {
            "zdroj": self.name,
            "jmeno_maklere": agent_name or "Neznámý makléř",
            "telefon": phone,
            "email": email,
            "realitni_kancelar": company_name,
            "kraj": self._extract_region(locality),
            "mesto": self._extract_city(locality),
            "specializace": self._estate_type(estate),
            "detailni_informace": estate_name,
            "odkazy": [estate_url] if estate_url else [],
        }

    @staticmethod
    def _first_phone(data: Dict) -> Optional[str]:
        phones = data.get("_embedded", {}).get("phones") or data.get("phones") or []
        if isinstance(phones, list) and phones:
            for item in phones:
                if isinstance(item, dict):
                    phone = item.get("number") or item.get("value")
                else:
                    phone = str(item)
                if phone:
                    return phone
        if isinstance(phones, dict):
            return phones.get("number") or phones.get("value")
        return None

    @staticmethod
    def _first_email(data: Dict) -> Optional[str]:
        emails = data.get("_embedded", {}).get("emails") or data.get("emails") or []
        if isinstance(emails, list) and emails:
            for item in emails:
                if isinstance(item, dict):
                    email = item.get("value") or item.get("email")
                else:
                    email = str(item)
                if email:
                    return email
        if isinstance(emails, dict):
            return emails.get("value")
        return None

    def _extract_url(self, data: Dict) -> Optional[str]:
        if not isinstance(data, dict):
            return None

        def find_url(value: object) -> Optional[str]:
            if isinstance(value, str):
                return _normalise_url(value)
            if isinstance(value, dict):
                for nested in value.values():
                    url = find_url(nested)
                    if url:
                        return url
            if isinstance(value, list):
                for item in value:
                    url = find_url(item)
                    if url:
                        return url
            return None

        priority_keys = (
            "canonical",
            "url",
            "detail_url",
            "detailUrl",
            "permalink",
            "public_url",
            "publicUrl",
            "canonicalUrl",
            "canonical_url",
        )
        for key in priority_keys:
            candidate = data.get(key)
            url = find_url(candidate)
            if url:
                return url

        nested_keys = (
            "seo",
            "_links",
            "links",
            "share",
            "share_links",
            "shareLinks",
            "social_sharing",
            "socialSharing",
        )
        for key in nested_keys:
            candidate = data.get(key)
            url = find_url(candidate)
            if url:
                return url

        fallback_url = find_url(data)
        if fallback_url:
            return fallback_url

        seo = data.get("seo") if isinstance(data.get("seo"), dict) else None
        seo_id = None
        if isinstance(seo, dict):
            seo_id = seo.get("seoId") or seo.get("seo_id")
        if not seo_id:
            seo_id = data.get("seoId") or data.get("seo_id") or data.get("hash_id") or data.get("hashId")

        if not seo_id:
            return None

        seo_dict = seo or {}
        category_url = (
            seo_dict.get("categoryUrl")
            or seo_dict.get("category_url")
            or data.get("categoryUrl")
            or data.get("category_url")
        )
        locality_url = (
            seo_dict.get("localityUrl")
            or seo_dict.get("locality_url")
            or data.get("localityUrl")
            or data.get("locality_url")
        )

        if not isinstance(category_url, str) or not category_url.strip():
            return None

        segments = ["detail"]
        segments.extend(part for part in category_url.strip("/").split("/") if part)

        if isinstance(locality_url, str) and locality_url.strip():
            segments.extend(part for part in locality_url.strip("/").split("/") if part)
        else:
            locality_text = seo.get("locality") or data.get("locality")
            locality_slug = _slugify_locality(locality_text)
            if locality_slug:
                segments.append(locality_slug)

        segments.append(str(seo_id))
        cleaned_segments = [segment for segment in segments if isinstance(segment, str) and segment]
        if len(cleaned_segments) < 2:
            return None

        path = "/".join(cleaned_segments)
        url = urljoin(self._config.base_url + "/", path)
        return _normalise_url(url)

    @staticmethod
    def _extract_region(locality: str) -> Optional[str]:
        parts = [part.strip() for part in locality.split(",") if part.strip()]
        if not parts:
            return None
        return parts[-1] if len(parts) > 1 else None

    @staticmethod
    def _extract_city(locality: str) -> Optional[str]:
        parts = [part.strip() for part in locality.split(",") if part.strip()]
        if not parts:
            return None
        return parts[0]

    @staticmethod
    def _estate_type(estate: Dict) -> Optional[str]:
        estate_type = estate.get("name_disposition") or estate.get("name")
        return estate_type
