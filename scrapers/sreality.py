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
    def scrape_active_agents_full_profiles(
        self,
        *,
        category_main: int = 1,
        category_type: int = 1,
        locality_region_id: Optional[int] = None,
        max_pages: Optional[int] = None,
        full_scan: bool = False,
        fetch_details: bool = True,
    ) -> ScraperResult:
        """
        EFEKTIVNÍ METODA: Najde aktivní makléře a získá jejich kompletní profily.

        1. Projde inzeráty podle kategorie/kraje
        2. Identifikuje aktivní makléře (user_id)
        3. Pro každého makléře získá VŠECHNY jeho inzeráty
        4. Vrátí kompletní profily s přesným počtem inzerátů

        Args:
            category_main: Typ nemovitosti (1=Byty, 2=Domy, atd.)
            category_type: Typ inzerátu (1=Prodej, 2=Pronájem, atd.)
            locality_region_id: ID kraje (10=Praha, atd.) nebo None pro celou ČR
            max_pages: Maximální počet stránek k procházení
            full_scan: Projít všechny stránky
            fetch_details: Stahovat detaily inzerátů pro přesnější kontakty

        Returns:
            ScraperResult s kompletními profily aktivních makléřů
        """
        print("🔍 Fáze 1: Hledám aktivní makléře...")

        if full_scan:
            max_pages = None

        limit = max_pages if max_pages is not None else None

        # Fáze 1: Najdi aktivní makléře
        active_user_ids = set()
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
                break

            estates = payload.get("_embedded", {}).get("estates", [])
            if not estates:
                break

            # Projdi inzeráty a získej user_id
            for estate in estates:
                if fetch_details:
                    detail = self._fetch_detail(estate)
                else:
                    detail = estate

                if detail:
                    embedded = detail.get("_embedded", {})
                    seller = embedded.get("seller", {})
                    broker = embedded.get("broker", {})

                    user_id = (
                        seller.get("user_id")
                        or seller.get("id")
                        or broker.get("user_id")
                        or broker.get("id")
                    )

                    if user_id:
                        active_user_ids.add(str(user_id))

            result_size = payload.get("result_size", 0)
            if (page * 60) >= result_size:
                break

            page += 1
            self._delay()

        print(f"✅ Nalezeno {len(active_user_ids)} aktivních makléřů")

        # Fáze 2: Získej kompletní profily
        print(f"\n🔍 Fáze 2: Získávám kompletní profily...")

        result = self.scrape_agent_profiles(
            agent_urls=list(active_user_ids),
            fetch_details=fetch_details,
        )

        result.metadata.update({
            "metoda": "Aktivní makléři s kompletními profily",
            "kategorie": self._config.category_main.get(category_main, "Neznámé"),
            "typ": self._config.category_type.get(category_type, "Neznámé"),
        })

        return result

    def scrape_agent_profiles(
        self,
        *,
        agent_urls: list[str],
        fetch_details: bool = True,
    ) -> ScraperResult:
        """
        Scrape agent profiles from Sreality.cz.

        Args:
            agent_urls: List of agent profile URLs or user IDs
            fetch_details: Whether to fetch detailed listing info

        Returns:
            ScraperResult with agent data
        """
        records: Dict[str, Dict[str, object]] = {}
        result = ScraperResult()

        for agent_url in agent_urls:
            # Extract user_id from URL or use directly if it's an ID
            user_id = self._extract_user_id(agent_url)

            if not user_id:
                result.errors.append(f"Nelze extrahovat user_id z: {agent_url}")
                continue

            # Get all listings from this agent
            agent_data = self._fetch_agent_listings(user_id, fetch_details)

            if not agent_data:
                result.errors.append(f"Nepodařilo se načíst data pro user_id: {user_id}")
                continue

            # Process agent data
            agent_record = self._process_agent_data(agent_data, user_id)

            if agent_record:
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
                        "profil_url": agent_record.get("profil_url"),
                        "pocet_inzeratu": agent_record.get("pocet_inzeratu", 0),
                    },
                )

                if agent_record.get("specializace"):
                    aggregated["specializace"].update(agent_record["specializace"])
                if agent_record.get("detailni_informace"):
                    aggregated["detailni_informace"].extend(agent_record["detailni_informace"])
                if agent_record.get("odkazy"):
                    aggregated["odkazy"].extend(agent_record["odkazy"])

        # Finalize records
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
                "typ_scrapovani": "Profily makléřů",
            }
        )
        return result

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
                        "profil_maklere": agent_record.get("profil_maklere"),
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
    # Internals - Agent Profile Methods
    # ------------------------------------------------------------------
    def _extract_user_id(self, agent_input: str) -> Optional[str]:
        """Extract user_id from URL or return the ID directly."""
        if not agent_input:
            return None

        # If it's just a number, return it
        if agent_input.isdigit():
            return agent_input

        # Try to extract from URL patterns:
        # https://www.sreality.cz/makler/12345
        # https://www.sreality.cz/en/makler/12345
        # /makler/12345
        patterns = [
            r'/makler/(\d+)',
            r'/realtor/(\d+)',
            r'/agent/(\d+)',
            r'user_id[=:](\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, agent_input)
            if match:
                return match.group(1)

        return None

    def _fetch_agent_listings(self, user_id: str, fetch_details: bool = True) -> Optional[Dict]:
        """Fetch all listings for a specific agent."""
        all_listings = []
        agent_info = {}
        page = 1

        while True:
            params = {
                "user_id": user_id,
                "page": page,
                "per_page": 60,
            }

            payload = self._request(self._config.api_url, params=params)

            if not payload:
                break

            estates = payload.get("_embedded", {}).get("estates", [])

            if not estates:
                break

            for estate in estates:
                if fetch_details:
                    detail = self._fetch_detail(estate)
                else:
                    detail = estate

                if detail:
                    all_listings.append(detail)
                    # Extract agent info from first listing if we don't have it yet
                    if not agent_info and detail.get("_embedded"):
                        embedded = detail.get("_embedded", {})
                        agent_info = {
                            "seller": embedded.get("seller", {}),
                            "broker": embedded.get("broker", {}),
                            "company": embedded.get("company", {}),
                        }

            result_size = payload.get("result_size", 0)
            if (page * 60) >= result_size:
                break

            page += 1
            self._delay()

        return {
            "user_id": user_id,
            "listings": all_listings,
            "agent_info": agent_info,
            "total_count": len(all_listings),
        }

    def _process_agent_data(self, agent_data: Dict, user_id: str) -> Optional[Record]:
        """Process agent data and extract contact information with aggregated stats."""
        if not agent_data or not agent_data.get("listings"):
            return None

        listings = agent_data["listings"]
        agent_info = agent_data.get("agent_info", {})

        # Extract agent information from agent_info or first listing
        seller = agent_info.get("seller", {})
        broker = agent_info.get("broker", {})
        company = agent_info.get("company", {})

        agent_name = (
            seller.get("user_name")
            or seller.get("name")
            or broker.get("user_name")
            or broker.get("name")
        )

        company_name = (
            seller.get("company_name")
            or company.get("name")
            or company.get("company_name")
        )

        # Try to get phone and email from first listing
        phone = None
        email = None
        for listing in listings[:3]:  # Check first 3 listings
            if not phone:
                phone = self._first_phone(listing)
            if not email:
                email = self._first_email(listing)
            if phone and email:
                break

        # Agreguj statistiky podle typu inzerátu
        # Kategorie: 1=Byty, 2=Domy, 3=Pozemky, 4=Komerční, 5=Ostatní
        # Typ: 1=Prodej, 2=Pronájem, 3=Dražby
        stats = {}
        localities = []

        for listing in listings:
            # Získej kategorii a typ z API dat
            seo = listing.get("seo", {}) if isinstance(listing.get("seo"), dict) else {}
            category_main = seo.get("category_main_cb")
            category_type = seo.get("category_type_cb")

            if category_main and category_type:
                key = (category_main, category_type)
                stats[key] = stats.get(key, 0) + 1

            # Locality
            locality = listing.get("locality", "")
            if locality:
                localities.append(locality)

        # Převeď statistiky na čitelný text
        category_names = {1: "Byty", 2: "Domy", 3: "Pozemky", 4: "Komerční", 5: "Ostatní"}
        type_names = {1: "Prodej", 2: "Pronájem", 3: "Dražby"}

        breakdown = []
        for (cat, typ), count in sorted(stats.items(), key=lambda x: -x[1]):
            cat_name = category_names.get(cat, f"Kategorie {cat}")
            typ_name = type_names.get(typ, f"Typ {typ}")
            breakdown.append(f"{cat_name}/{typ_name}: {count}")

        breakdown_text = ", ".join(breakdown) if breakdown else "Neznámé"

        # Get most common locality
        region = None
        city = None
        if localities:
            # Use the first locality
            region = self._extract_region(localities[0])
            city = self._extract_city(localities[0])

        profile_url = f"https://www.sreality.cz/makler/{user_id}"

        return {
            "zdroj": self.name,
            "jmeno_maklere": agent_name or "Neznámý makléř",
            "telefon": phone,
            "email": email,
            "realitni_kancelar": company_name,
            "kraj": region,
            "mesto": city,
            "profil_url": profile_url,
            "pocet_inzeratu": len(listings),
            "rozlozeni_inzeratu": breakdown_text,
        }

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

        # Získej URL profilu makléře
        profile_url = self._extract_agent_profile_url(seller, broker, company, agent_name, locality)

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
            "profil_maklere": profile_url,
        }

    def _extract_agent_profile_url(
        self,
        seller: Dict,
        broker: Dict,
        company: Dict,
        agent_name: Optional[str],
        locality: Optional[str]
    ) -> Optional[str]:
        """
        Vytvoří URL profilu makléře.
        Formát: https://www.sreality.cz/adresar/{slug}/{company_id}/makleri/{user_id}
        """
        # Získej user_id
        user_id = (
            seller.get("user_id")
            or seller.get("id")
            or broker.get("user_id")
            or broker.get("id")
        )

        if not user_id:
            return None

        # Získej company_id
        company_id = (
            company.get("id")
            or seller.get("company_id")
            or seller.get("company", {}).get("id")
        )

        if not company_id:
            return None

        # Vytvoř slug z jména a lokality
        slug_parts = []

        if agent_name:
            slug_parts.append(agent_name)

        if locality:
            # Vezmi první část lokality (město)
            city = locality.split(",")[0].strip()
            if city:
                slug_parts.append(city)

        if not slug_parts:
            return None

        # Slugify
        slug_text = "-".join(slug_parts)
        slug = _slugify_locality(slug_text)

        if not slug:
            return None

        # Sestav URL
        profile_url = f"{self._config.base_url}/adresar/{slug}/{company_id}/makleri/{user_id}"

        return profile_url

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

        # Extrahuj ID inzerátu
        seo = data.get("seo") if isinstance(data.get("seo"), dict) else {}
        hash_id = data.get("hash_id") or data.get("hashId") or seo.get("seoId") or seo.get("seo_id")

        if not hash_id:
            return None

        # Pokus se sestavit URL z SEO parametrů (category_type_cb, category_main_cb, category_sub_cb)
        category_type_cb = seo.get("category_type_cb") if isinstance(seo, dict) else None
        category_main_cb = seo.get("category_main_cb") if isinstance(seo, dict) else None
        category_sub_cb = seo.get("category_sub_cb") if isinstance(seo, dict) else None

        # Mapování kódů na text
        type_map = {1: "prodej", 2: "pronajem", 3: "drazby"}
        main_map = {1: "byt", 2: "dum", 3: "pozemek", 4: "komercni", 5: "ostatni"}

        # Podkategorie - pro byty jsou to dispozice, pro domy typy
        # Pokud máme category_sub_cb, pokusíme se najít text v názvu inzerátu
        sub_text = None
        name = data.get("name", "") or ""

        # Pro byty hledej dispozici (např. "2+kk", "3+1")
        if category_main_cb == 1:
            import re
            match = re.search(r'\d\+(?:kk|\d)', name, re.IGNORECASE)
            if match:
                sub_text = match.group(0).lower()

        # Lokaliita
        locality = seo.get("locality") if isinstance(seo, dict) else None
        if not locality:
            locality = _slugify_locality(data.get("locality", ""))

        # Pokud máme categoryUrl a localityUrl, použij je (starý způsob)
        category_url = seo.get("categoryUrl") or seo.get("category_url") if isinstance(seo, dict) else None
        locality_url = seo.get("localityUrl") or seo.get("locality_url") if isinstance(seo, dict) else None

        # Pokud existuje categoryUrl, použij starý způsob
        if isinstance(category_url, str) and category_url.strip():
            segments = ["detail"]
            segments.extend(part for part in category_url.strip("/").split("/") if part)

            if isinstance(locality_url, str) and locality_url.strip():
                segments.extend(part for part in locality_url.strip("/").split("/") if part)
            elif locality:
                segments.append(locality)

            segments.append(str(hash_id))
            cleaned_segments = [segment for segment in segments if isinstance(segment, str) and segment]
            if len(cleaned_segments) >= 2:
                path = "/".join(cleaned_segments)
                url = urljoin(self._config.base_url + "/", path)
                return _normalise_url(url)

        # Nový způsob - sestavení z category_type_cb, category_main_cb atd.
        if category_type_cb and category_main_cb:
            segments = ["detail"]

            type_text = type_map.get(category_type_cb)
            if type_text:
                segments.append(type_text)

            main_text = main_map.get(category_main_cb)
            if main_text:
                segments.append(main_text)

            if sub_text:
                segments.append(sub_text)

            if locality:
                segments.append(locality)

            segments.append(str(hash_id))

            cleaned_segments = [segment for segment in segments if isinstance(segment, str) and segment]
            if len(cleaned_segments) >= 4:  # Minimálně: detail, typ, kategorie, ID
                path = "/".join(cleaned_segments)
                url = urljoin(self._config.base_url + "/", path)
                return _normalise_url(url)

        # Fallback - jen ID
        return urljoin(self._config.base_url + "/", f"detail/{hash_id}")

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
