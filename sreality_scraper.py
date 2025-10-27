#!/usr/bin/env python3
"""
Sreality.cz Scraper - Lokální scraper pro stahování nabídek nemovitostí
Autor: Claude (Anthropic)
"""

import requests
import time
import random
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import json
import sys
from pathlib import Path

# Konfigurace
class Config:
    """Konfigurace scraperu"""
    
    # API endpoints
    BASE_URL = "https://www.sreality.cz"
    API_URL = f"{BASE_URL}/api/cs/v2/estates"
    
    # Výchozí parametry
    CATEGORY_MAIN = {
        1: "Byty",
        2: "Domy", 
        3: "Pozemky",
        4: "Komerční",
        5: "Ostatní"
    }
    
    CATEGORY_TYPE = {
        1: "Prodej",
        2: "Pronájem",
        3: "Dražby"
    }
    
    # Rate limiting
    MIN_DELAY = 2  # minimální delay mezi requesty (sekundy)
    MAX_DELAY = 5  # maximální delay
    
    # User agents pro rotaci
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # Output
    OUTPUT_DIR = Path(__file__).parent / "data"
    MAX_PAGES = 50  # maximum stránek k procházení


class SrealityScraper:
    """Hlavní třída scraperu"""
    
    def __init__(self, verbose: bool = True):
        self.config = Config()
        self.session = requests.Session()
        self.verbose = verbose
        self.results: List[Dict] = []
        
        # Vytvoření složky pro data
        self.config.OUTPUT_DIR.mkdir(exist_ok=True)
    
    def _get_headers(self) -> Dict[str, str]:
        """Generuje náhodné HTTP hlavičky"""
        return {
            'User-Agent': random.choice(self.config.USER_AGENTS),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.sreality.cz/',
        }
    
    def _delay(self):
        """Náhodná pauza mezi requesty"""
        delay = random.uniform(self.config.MIN_DELAY, self.config.MAX_DELAY)
        if self.verbose:
            print(f"  ⏳ Čekám {delay:.2f}s...", end='\r')
        time.sleep(delay)
    
    def _make_request(self, url: str, params: Dict, retries: int = 3) -> Optional[Dict]:
        """Provede HTTP request s retry logikou"""
        for attempt in range(retries):
            try:
                headers = self._get_headers()
                response = self.session.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit - počkáme déle
                    wait_time = (2 ** attempt) * 5
                    if self.verbose:
                        print(f"  ⚠️  Rate limit! Čekám {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    if self.verbose:
                        print(f"  ❌ Chyba {response.status_code}")
                    return None
                    
            except Exception as e:
                if self.verbose:
                    print(f"  ❌ Výjimka: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def scrape_listings(self, 
                       category_main: int = 1,  # 1=Byty
                       category_type: int = 1,  # 1=Prodej
                       locality_region_id: Optional[int] = None,  # např. 10=Praha
                       max_pages: Optional[int] = None) -> List[Dict]:
        """
        Stáhne nabídky z Sreality
        
        Args:
            category_main: Typ nemovitosti (1=Byty, 2=Domy, 3=Pozemky, 4=Komerční, 5=Ostatní)
            category_type: Typ inzerátu (1=Prodej, 2=Pronájem, 3=Dražby)
            locality_region_id: ID kraje (volitelné, např. 10=Praha, 14=Moravskoslezský)
            max_pages: Maximální počet stránek (None = vše)
        """
        
        if max_pages is None:
            max_pages = self.config.MAX_PAGES
        
        category_main_name = self.config.CATEGORY_MAIN.get(category_main, "Neznámé")
        category_type_name = self.config.CATEGORY_TYPE.get(category_type, "Neznámé")
        
        print(f"\n🏠 Sreality Scraper")
        print(f"=" * 60)
        print(f"📋 Typ: {category_main_name} - {category_type_name}")
        if locality_region_id:
            print(f"📍 Region ID: {locality_region_id}")
        print(f"📄 Max. stránek: {max_pages}")
        print(f"=" * 60 + "\n")
        
        page = 1
        total_scraped = 0
        
        while page <= max_pages:
            params = {
                'category_main_cb': category_main,
                'category_type_cb': category_type,
                'page': page,
                'per_page': 60,  # zvýšený počet pro rychlejší scraping
            }
            
            if locality_region_id:
                params['locality_region_id'] = locality_region_id
            
            if self.verbose:
                print(f"📄 Stránka {page}/{max_pages}...", end=' ')
            
            data = self._make_request(self.config.API_URL, params)
            
            if not data:
                print(f"  ❌ Chyba při stahování stránky {page}")
                break
            
            # Zpracování výsledků
            estates = data.get('_embedded', {}).get('estates', [])
            
            if not estates:
                print(f"  ℹ️  Žádné další nabídky")
                break
            
            for estate in estates:
                parsed = self._parse_estate(estate)
                if parsed:
                    self.results.append(parsed)
            
            total_scraped += len(estates)
            
            if self.verbose:
                print(f"✅ Staženo {len(estates)} nabídek (celkem: {total_scraped})")
            
            # Kontrola, jestli existuje další stránka
            result_size = data.get('result_size', 0)
            if page * 60 >= result_size:
                print(f"\n✅ Dosažen konec výsledků ({result_size} celkem)")
                break
            
            page += 1
            self._delay()
        
        print(f"\n✨ Scraping dokončen! Celkem nabídek: {len(self.results)}")
        return self.results
    
    def _parse_estate(self, estate: Dict) -> Optional[Dict]:
        """Parsuje data jedné nabídky"""
        try:
            # Základní informace
            parsed = {
                'hash_id': estate.get('hash_id'),
                'name': estate.get('name'),
                'locality': estate.get('locality'),
                'price': estate.get('price'),
                'price_czk': estate.get('price_czk', {}).get('value_raw'),
                'price_note': estate.get('price_note'),
            }
            
            # URL
            seo = estate.get('seo', {})
            parsed['url'] = f"{self.config.BASE_URL}{seo.get('href', '')}" if seo.get('href') else None
            
            # Detaily
            items = estate.get('_embedded', {}).get('favourite', {}).get('_embedded', {}).get('items', [])
            for item in items:
                item_name = item.get('name', '').lower()
                item_value = item.get('value')
                
                if 'podlaží' in item_name or 'floor' in item_name:
                    parsed['floor'] = item_value
                elif 'plocha' in item_name or 'area' in item_name:
                    parsed['area'] = item_value
                elif 'stavba' in item_name or 'building' in item_name:
                    parsed['building_type'] = item_value
                elif 'vlastnictví' in item_name or 'ownership' in item_name:
                    parsed['ownership'] = item_value
            
            # Získání plné adresy z locality
            if estate.get('locality'):
                parsed['full_address'] = estate.get('locality')
            
            # Datum přidání
            parsed['scraped_at'] = datetime.now().isoformat()
            
            return parsed
            
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Chyba při parsování: {str(e)}")
            return None
    
    def save_to_excel(self, filename: Optional[str] = None) -> str:
        """Uloží výsledky do Excel souboru"""
        if not self.results:
            print("⚠️  Žádná data k uložení!")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sreality_data_{timestamp}.xlsx"
        
        filepath = self.config.OUTPUT_DIR / filename
        
        # Vytvoření DataFrame
        df = pd.DataFrame(self.results)
        
        # Uložení do Excelu
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        print(f"\n💾 Data uložena do: {filepath}")
        print(f"📊 Počet záznamů: {len(self.results)}")
        print(f"📋 Sloupce: {', '.join(df.columns.tolist())}")
        
        return str(filepath)
    
    def save_to_csv(self, filename: Optional[str] = None) -> str:
        """Uloží výsledky do CSV souboru (alternativa k Excelu)"""
        if not self.results:
            print("⚠️  Žádná data k uložení!")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sreality_data_{timestamp}.csv"
        
        filepath = self.config.OUTPUT_DIR / filename
        
        df = pd.DataFrame(self.results)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 Data uložena do: {filepath}")
        return str(filepath)


def main():
    """Hlavní funkce - spouštění z příkazové řádky"""
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║           SREALITY.CZ SCRAPER                             ║
║           Lokální scraper pro stahování nabídek           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Vytvoření scraperu
    scraper = SrealityScraper(verbose=True)
    
    # Příklad použití - můžeš změnit parametry
    print("\n📝 Zadej parametry vyhledávání:")
    print("\nTyp nemovitosti:")
    print("  1 = Byty")
    print("  2 = Domy")
    print("  3 = Pozemky")
    print("  4 = Komerční")
    print("  5 = Ostatní")
    
    try:
        category_main = int(input("\nTyp nemovitosti (1-5) [1]: ") or "1")
    except ValueError:
        category_main = 1
    
    print("\nTyp inzerátu:")
    print("  1 = Prodej")
    print("  2 = Pronájem")
    print("  3 = Dražby")
    
    try:
        category_type = int(input("\nTyp inzerátu (1-3) [1]: ") or "1")
    except ValueError:
        category_type = 1
    
    print("\nKraj (nech prázdné pro celou ČR):")
    print("  10 = Praha")
    print("  11 = Středočeský")
    print("  12 = Jihočeský")
    print("  13 = Plzeňský")
    print("  14 = Moravskoslezský")
    print("  (a další...)")
    
    locality = input("\nID kraje [prázdné]: ").strip()
    locality_id = int(locality) if locality else None
    
    try:
        max_pages = int(input("\nMax. počet stránek [10]: ") or "10")
    except ValueError:
        max_pages = 10
    
    # Spuštění scrapingu
    scraper.scrape_listings(
        category_main=category_main,
        category_type=category_type,
        locality_region_id=locality_id,
        max_pages=max_pages
    )
    
    # Uložení do Excelu
    if scraper.results:
        scraper.save_to_excel()
        
        # Nabídka uložení i do CSV
        save_csv = input("\n❓ Uložit i do CSV? (y/n) [n]: ").lower()
        if save_csv == 'y':
            scraper.save_to_csv()
    
    print("\n✨ Hotovo! Můžeš zavřít okno.\n")


if __name__ == "__main__":
    main()
