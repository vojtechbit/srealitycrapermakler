#!/usr/bin/env python3
import requests
import time
import random
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
import json
from pathlib import Path
from collections import defaultdict
from urllib.parse import urljoin

class Config:
    BASE_URL = "https://www.sreality.cz"
    API_URL = f"{BASE_URL}/api/cs/v2/estates"

    CATEGORY_MAIN = {1: "Byty", 2: "Domy", 3: "Pozemky", 4: "Komerční", 5: "Ostatní"}
    CATEGORY_TYPE = {1: "Prodej", 2: "Pronájem", 3: "Dražby"}

    MIN_DELAY = 1
    MAX_DELAY = 3

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]

    OUTPUT_DIR = Path(__file__).parent / "data"
    MAX_PAGES = 50

class AgentScraper:
    def __init__(self, verbose: bool = True):
        self.config = Config()
        self.session = requests.Session()
        self.verbose = verbose
        self.agents: Dict[str, Dict] = {}
        self.config.OUTPUT_DIR.mkdir(exist_ok=True)

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': random.choice(self.config.USER_AGENTS),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
            'Referer': 'https://www.sreality.cz/',
        }

    def _delay(self):
        delay = random.uniform(self.config.MIN_DELAY, self.config.MAX_DELAY)
        time.sleep(delay)

    def _make_request(self, url: str, params: Dict = None, retries: int = 3) -> Optional[Dict]:
        for attempt in range(retries):
            try:
                headers = self._get_headers()
                response = self.session.get(url, params=params, headers=headers, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    wait_time = (2 ** attempt) * 5
                    if self.verbose:
                        print(f"  ⚠️  Rate limit! Čekám {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    if self.verbose:
                        print(f"  ❌ HTTP {response.status_code}")
                    return None

            except Exception as e:
                if self.verbose and attempt == retries - 1:
                    print(f"  ❌ {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

        return None

    def scrape_agents(self,
                     category_main: int = 1,
                     category_type: int = 1,
                     locality_region_id: Optional[int] = None,
                     max_pages: Optional[int] = None,
                     fetch_details: bool = True) -> List[Dict]:

        unlimited = max_pages is None
        if max_pages is None:
            max_pages = 999999

        category_main_name = self.config.CATEGORY_MAIN.get(category_main, "Neznámé")
        category_type_name = self.config.CATEGORY_TYPE.get(category_type, "Neznámé")

        print(f"\n🏢 Sreality - Scraper makléřů")
        print(f"=" * 60)
        print(f"📋 Inzeráty: {category_main_name} - {category_type_name}")
        if locality_region_id:
            print(f"📍 Region ID: {locality_region_id}")
        if unlimited:
            print(f"📄 Režim: NEOMEZENÝ (všechny stránky)")
        else:
            print(f"📄 Max. stránek: {max_pages}")
        print(f"=" * 60 + "\n")

        page = 1
        total_listings = 0

        while page <= max_pages:
            params = {
                'category_main_cb': category_main,
                'category_type_cb': category_type,
                'page': page,
                'per_page': 60,
            }

            if locality_region_id:
                params['locality_region_id'] = locality_region_id

            if self.verbose:
                if unlimited:
                    print(f"📄 Stránka {page}...", end=' ')
                else:
                    print(f"📄 Stránka {page}/{max_pages}...", end=' ')

            data = self._make_request(self.config.API_URL, params)

            if not data:
                print(f"❌ CHYBA! Pravděpodobně Cloudflare blokace.")
                print(f"   Zkus to znovu za chvíli, nebo z jiné sítě.")
                break

            estates = data.get('_embedded', {}).get('estates', [])

            if not estates:
                print(f"✓ Konec")
                break

            for estate in estates:
                if fetch_details:
                    self._process_estate_detail(estate)
                else:
                    self._process_estate_basic(estate)

            total_listings += len(estates)

            if self.verbose:
                print(f"✓ {len(estates)} inzerátů | {len(self.agents)} makléřů")

            result_size = data.get('result_size', 0)
            if page * 60 >= result_size:
                print(f"\n✓ Konec výsledků ({result_size} celkem)")
                break

            page += 1
            self._delay()

        print(f"\n✨ Dokončeno! {len(self.agents)} makléřů z {total_listings} inzerátů")
        return list(self.agents.values())

    def _process_estate_detail(self, estate: Dict):
        hash_id = estate.get('hash_id')
        if not hash_id:
            return

        detail_url = f"{self.config.BASE_URL}/api/cs/v2/estates/{hash_id}"
        detail = self._make_request(detail_url)

        if not detail:
            return

        self._extract_agent_info(detail, estate)
        self._delay()

    def _process_estate_basic(self, estate: Dict):
        self._extract_agent_info(estate, estate)

    def _extract_agent_info(self, detail: Dict, estate: Dict):
        try:
            embedded = detail.get('_embedded', {})

            agent_name = None
            agent_phone = None
            agent_email = None
            company_name = None

            seller = embedded.get('seller')
            company = embedded.get('company')
            broker = embedded.get('broker')

            if seller:
                agent_name = seller.get('user_name') or seller.get('name')
                company_name = (
                    seller.get('company_name')
                    or seller.get('company', {}).get('name')
                    or seller.get('organization', {}).get('name')
                )

            if company and not company_name:
                company_name = company.get('name') or company.get('company_name')

            if broker and not agent_name:
                agent_name = broker.get('user_name') or broker.get('name')

            if not company_name:
                company_name = (
                    self._find_company_name(detail)
                    or self._find_company_name(estate)
                )

            agent_phone = agent_phone or self._find_first_phone(detail)
            if not agent_phone:
                agent_phone = self._find_first_phone(estate)

            agent_email = agent_email or self._find_first_email(detail)
            if not agent_email:
                agent_email = self._find_first_email(estate)

            if not agent_name and not agent_phone and not agent_email:
                agent_name = "Neznámý makléř"

            agent_key = f"{agent_name}_{company_name}_{agent_phone}"

            estate_url = self._build_estate_url(detail, estate)
            estate_name = estate.get('name', 'N/A')
            locality = estate.get('locality', 'N/A')
            price = estate.get('price_czk', {}).get('value_raw') or estate.get('price')

            region = self._extract_region(locality)
            city = self._extract_city(locality)

            if agent_key not in self.agents:
                self.agents[agent_key] = {
                    'jmeno_maklere': agent_name or 'N/A',
                    'telefon': agent_phone or 'N/A',
                    'email': agent_email or 'N/A',
                    'realitni_kancelar': company_name or 'N/A',
                    'kraj': region,
                    'mesto': city,
                    'pocet_inzeratu': 0,
                    'inzeraty': [],
                    'inzeraty_odkazy': [],
                    'typy_nemovitosti': set(),
                }

            agent = self.agents[agent_key]
            agent['pocet_inzeratu'] += 1
            agent['inzeraty'].append(estate_name)
            if estate_url:
                agent['inzeraty_odkazy'].append(estate_url)

            estate_type = self._get_estate_type(estate)
            if estate_type:
                agent['typy_nemovitosti'].add(estate_type)

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Chyba: {str(e)}")

    def _build_estate_url(self, detail: Optional[Dict], estate: Optional[Dict]) -> Optional[str]:
        """
        Připraví veřejný (ne-API) odkaz na inzerát.

        API vrací celou řadu odkazů v různých strukturách. Preferujeme URL,
        které vede na veřejnou stránku (typicky obsahující "/detail/").
        V některých případech je ukryta v sekci `seo`, jindy ve `_links`,
        nebo mezi share odkazy. Pokud žádná varianta není k dispozici,
        spadneme na poslední možnost s použitím `hash_id`.
        """

        base_url = self.config.BASE_URL.rstrip('/') + '/'

        def normalize_url(value: Optional[str]) -> Optional[str]:
            if not value or not isinstance(value, str):
                return None

            candidate = value.strip()
            if not candidate:
                return None

            if candidate.startswith('//'):
                candidate = f"https:{candidate}"

            if candidate.startswith('detail/'):
                candidate = f"/{candidate}"

            if candidate.startswith('/'):
                candidate = urljoin(base_url, candidate.lstrip('/'))

            if not candidate.startswith('http'):
                return None

            if '/api/' in candidate or '/cs/v2/estates' in candidate:
                return None

            if '/detail/' not in candidate:
                return None

            return candidate

        def extract_from_links(links: Any) -> Optional[str]:
            if isinstance(links, dict):
                for key, value in links.items():
                    if isinstance(value, dict):
                        href = normalize_url(value.get('href') or value.get('url'))
                        if href:
                            return href
                        nested = extract_from_links(value)
                        if nested:
                            return nested
                    elif isinstance(value, list):
                        for item in value:
                            nested = extract_from_links(item)
                            if nested:
                                return nested
                    elif isinstance(value, str):
                        href = normalize_url(value)
                        if href:
                            return href
            elif isinstance(links, list):
                for item in links:
                    nested = extract_from_links(item)
                    if nested:
                        return nested
            return None

        def extract_from_seo(seo: Any) -> Optional[str]:
            if not isinstance(seo, dict):
                return None

            for key in (
                'canonical', 'canonical_url', 'canonicalUrl', 'canonical_path',
                'url', 'href', 'detail_url', 'detailUrl'
            ):
                href = normalize_url(seo.get(key))
                if href:
                    return href

            href = extract_from_links(seo.get('links'))
            if href:
                return href

            # Některé položky mají seznam SEO URL
            seo_urls = seo.get('seo_urls') or seo.get('urls')
            href = extract_from_links(seo_urls)
            if href:
                return href

            return None

        def extract_generic(data: Any) -> Optional[str]:
            if isinstance(data, dict):
                for key in (
                    'url', 'detail_url', 'detailUrl', 'public_url', 'publicUrl',
                    'share_url', 'shareUrl', 'browser_url', 'browserUrl', 'href',
                    'canonical', 'canonical_url', 'canonicalUrl', 'permalink',
                    'link'
                ):
                    if key in data:
                        value = data[key]
                        if isinstance(value, str):
                            href = normalize_url(value)
                            if href:
                                return href
                        else:
                            href = extract_from_links(value)
                            if href:
                                return href

                href = extract_from_links(data.get('_links'))
                if href:
                    return href

                href = extract_from_links(data.get('links'))
                if href:
                    return href

                for value in data.values():
                    nested = extract_generic(value)
                    if nested:
                        return nested

            elif isinstance(data, list):
                for item in data:
                    nested = extract_generic(item)
                    if nested:
                        return nested
            elif isinstance(data, str):
                href = normalize_url(data)
                if href:
                    return href

            return None

        def slugify(value: Optional[str]) -> Optional[str]:
            if not value or not isinstance(value, str):
                return None
            cleaned = value.strip().lower()
            if not cleaned:
                return None
            return cleaned.replace(' ', '-').replace('_', '-').replace('--', '-').strip('-')

        def extract_slug(seo_dict: Dict, key: str) -> Optional[str]:
            if not isinstance(seo_dict, dict):
                return None
            value = seo_dict.get(key)
            if isinstance(value, dict):
                for inner_key in ('value', 'seo_value', 'slug', 'code', 'id', 'key'):
                    slug = slugify(value.get(inner_key))
                    if slug:
                        return slug
                slug = slugify(value.get('name'))
                if slug:
                    return slug
            elif isinstance(value, (str, int)):
                slug = slugify(str(value))
                if slug:
                    return slug
            return None

        for source in (detail, estate):
            if not isinstance(source, dict):
                continue

            href = extract_from_seo(source.get('seo'))
            if href:
                return href

            href = extract_generic(source)
            if href:
                return href

        def manual_from_seo(source: Optional[Dict], hash_id: Optional[str]) -> Optional[str]:
            if not isinstance(source, dict) or not hash_id:
                return None

            seo = source.get('seo')
            if not isinstance(seo, dict):
                return None

            category_type = extract_slug(seo, 'category_type') or extract_slug(seo, 'category_type_cb')
            category_main = extract_slug(seo, 'category_main') or extract_slug(seo, 'category_main_cb')
            category_sub = extract_slug(seo, 'category_sub') or extract_slug(seo, 'category_sub_cb')
            locality_slug = extract_slug(seo, 'locality') or extract_slug(seo, 'locality_value')

            parts = [category_type, category_main]
            if category_sub:
                parts.append(category_sub)
            if locality_slug:
                parts.append(locality_slug)

            if len(parts) < 3:  # potřebujeme alespoň typ, kategorii a lokalitu
                return None

            parts.append(str(hash_id))
            path = '/'.join(filter(None, parts))
            return urljoin(base_url, f"detail/{path}")

        # Poslední pokus: složíme URL z hash_id, pokud žádné lepší není
        hash_id = None
        for source in (detail, estate):
            if isinstance(source, dict):
                hash_id = source.get('hash_id') or hash_id
                if hash_id:
                    break

        manual = manual_from_seo(detail or estate, hash_id)
        if manual:
            return manual

        if hash_id:
            return urljoin(base_url, f"detail/{hash_id}")

        return None

    def _find_company_name(self, data: Any) -> Optional[str]:
        return self._find_first_match(
            data,
            search_keys=("company", "organization", "organisation", "agency"),
            extractor=self._extract_company_value
        )

    def _extract_company_value(self, value: Any) -> Optional[str]:
        if isinstance(value, dict):
            for key in ("name", "company_name", "title"):
                if key in value:
                    extracted = self._extract_company_value(value[key])
                    if extracted:
                        return extracted
        elif isinstance(value, list):
            for item in value:
                extracted = self._extract_company_value(item)
                if extracted:
                    return extracted
        elif isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
        return None

    def _find_first_phone(self, data: Any) -> Optional[str]:
        return self._find_first_match(
            data,
            search_keys=("phone", "phones", "mobile", "telefon", "tel"),
            extractor=self._extract_phone_value
        )

    def _find_first_email(self, data: Any) -> Optional[str]:
        return self._find_first_match(
            data,
            search_keys=("email", "mail"),
            extractor=self._extract_email_value
        )

    def _find_first_match(
        self,
        data: Any,
        search_keys: tuple,
        extractor: Callable[[Any], Optional[str]]
    ) -> Optional[str]:
        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = str(key).lower()
                if any(search_key in key_lower for search_key in search_keys):
                    extracted = extractor(value)
                    if extracted:
                        return extracted
                nested = self._find_first_match(value, search_keys, extractor)
                if nested:
                    return nested
        elif isinstance(data, list):
            for item in data:
                nested = self._find_first_match(item, search_keys, extractor)
                if nested:
                    return nested
        return None

    def _extract_phone_value(self, value: Any) -> Optional[str]:
        if isinstance(value, dict):
            for key in ("number", "value", "formatted", "phone"):
                if key in value:
                    extracted = self._extract_phone_value(value[key])
                    if extracted:
                        return extracted
        elif isinstance(value, list):
            for item in value:
                extracted = self._extract_phone_value(item)
                if extracted:
                    return extracted
        elif isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
        return None

    def _extract_email_value(self, value: Any) -> Optional[str]:
        if isinstance(value, dict):
            for key in ("email", "value"):
                if key in value:
                    extracted = self._extract_email_value(value[key])
                    if extracted:
                        return extracted
        elif isinstance(value, list):
            for item in value:
                extracted = self._extract_email_value(item)
                if extracted:
                    return extracted
        elif isinstance(value, str):
            cleaned = value.strip()
            if cleaned and "@" in cleaned:
                return cleaned
        return None

    def _extract_region(self, locality: str) -> str:
        if not locality:
            return 'N/A'

        regions = {
            'Praha': 'Praha',
            'Středočeský': 'Středočeský',
            'Jihočeský': 'Jihočeský',
            'Plzeňský': 'Plzeňský',
            'Karlovarský': 'Karlovarský',
            'Ústecký': 'Ústecký',
            'Liberecký': 'Liberecký',
            'Královéhradecký': 'Královéhradecký',
            'Pardubický': 'Pardubický',
            'Vysočina': 'Vysočina',
            'Jihomoravský': 'Jihomoravský',
            'Olomoucký': 'Olomoucký',
            'Zlínský': 'Zlínský',
            'Moravskoslezský': 'Moravskoslezský',
        }

        for region in regions:
            if region.lower() in locality.lower():
                return regions[region]

        return locality.split(',')[-1].strip() if ',' in locality else 'N/A'

    def _extract_city(self, locality: str) -> str:
        if not locality:
            return 'N/A'
        parts = locality.split(',')
        return parts[0].strip() if parts else 'N/A'

    def _get_estate_type(self, estate: Dict) -> str:
        name = estate.get('name', '').lower()

        if 'byt' in name:
            return 'Byt'
        elif 'dům' in name or 'rodinný dům' in name:
            return 'Dům'
        elif 'pozemek' in name:
            return 'Pozemek'
        elif 'kancelář' in name or 'komerční' in name:
            return 'Komerční'
        else:
            return 'Ostatní'

    def save_to_excel(self, filename: Optional[str] = None) -> str:
        if not self.agents:
            print("⚠️  Žádná data!")
            return ""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"makleri_{timestamp}.xlsx"

        filepath = self.config.OUTPUT_DIR / filename

        results = []
        for agent in self.agents.values():
            results.append({
                'Jméno makléře': agent['jmeno_maklere'],
                'Telefon': agent['telefon'],
                'Email': agent['email'],
                'Realitní kancelář': agent['realitni_kancelar'],
                'Kraj': agent['kraj'],
                'Město': agent['mesto'],
                'Počet inzerátů': agent['pocet_inzeratu'],
                'Typy nemovitostí': ', '.join(sorted(agent['typy_nemovitosti'])) if agent['typy_nemovitosti'] else 'N/A',
                'Odkazy': '\n'.join(agent['inzeraty_odkazy'][:5]),
                'Inzeráty': '\n'.join(agent['inzeraty'][:5]) + ('\n...' if len(agent['inzeraty']) > 5 else ''),
            })

        df = pd.DataFrame(results)
        df = df.sort_values('Počet inzerátů', ascending=False)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Makléři')

            worksheet = writer.sheets['Makléři']

            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(lambda x: len(str(x).split('\n')[0])).max(),
                    len(col)
                ) + 2

                if col == 'Odkazy':
                    max_length = min(max_length, 80)
                elif col == 'Inzeráty':
                    max_length = min(max_length, 60)
                elif col == 'Email':
                    max_length = min(max_length, 35)
                else:
                    max_length = min(max_length, 30)

                worksheet.column_dimensions[chr(65 + idx)].width = max_length

            from openpyxl.styles import Alignment
            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical='top')

        print(f"\n💾 Uloženo: {filepath}")
        print(f"📊 Počet makléřů: {len(results)}")

        return str(filepath)

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║           SREALITY - SCRAPER MAKLÉŘŮ                      ║
╚═══════════════════════════════════════════════════════════╝
    """)

    scraper = AgentScraper(verbose=True)

    print("Typ nemovitosti:")
    print("  1=Byty  2=Domy  3=Pozemky  4=Komerční  5=Ostatní")
    category_main = int(input("Typ [1]: ") or "1")

    print("\nTyp inzerátu:")
    print("  1=Prodej  2=Pronájem  3=Dražby")
    category_type = int(input("Typ [1]: ") or "1")

    print("\nKraj (prázdné = celá ČR):")
    print("  10=Praha  11=Středočeský  12=Jihočeský  13=Plzeňský")
    print("  14=Karlovarský  15=Ústecký  16=Liberecký")
    print("  17=Královéhradecký  18=Pardubický  19=Vysočina")
    print("  20=Jihomoravský  21=Olomoucký  22=Zlínský  23=Moravskoslezský")
    locality = input("Kraj [celá ČR]: ").strip()
    locality_id = int(locality) if locality else None

    print("\nMax. počet stránek (0 = všechny stránky, může trvat hodiny!):")
    max_pages_input = input("Max. stránek [10]: ").strip() or "10"
    max_pages = None if max_pages_input == "0" else int(max_pages_input)

    fetch_details = input("\nStahovat detaily? (pomalejší, ale přesnější) [y/n]: ").lower() == 'y'

    print("\n" + "="*60)
    if max_pages is None:
        print("⚠️  POZOR: Projdu VŠECHNY stránky - může trvat velmi dlouho!")
    print(f"📂 Excel se uloží do: {scraper.config.OUTPUT_DIR}")
    print("="*60 + "\n")

    input("Stiskni ENTER pro start... (nebo Ctrl+C pro zrušení)")

    scraper.scrape_agents(
        category_main=category_main,
        category_type=category_type,
        locality_region_id=locality_id,
        max_pages=max_pages,
        fetch_details=fetch_details
    )

    if scraper.agents:
        filepath = scraper.save_to_excel()
        print(f"\n📂 Excel soubor: {filepath}")

    print("\n✨ Hotovo! Můžeš zavřít Terminal.\n")

if __name__ == "__main__":
    main()
