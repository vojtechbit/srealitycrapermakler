#!/usr/bin/env python3
"""
Očistí XLSX soubor s makléři od neaktivních inzerátů.
Zkontroluje, zda odkazy stále vedou na aktivní stránky.
"""

from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import pandas as pd
from openpyxl.styles import Alignment, Font
import requests
import time
import random
from urllib.parse import urlparse


class LinkCleaner:
    """Třída pro ověření a čištění odkazů."""

    def __init__(self, verbose: bool = True, delay_range: tuple = (1, 2)):
        self.verbose = verbose
        self.delay_range = delay_range
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
            'Referer': 'https://www.sreality.cz/',
        }

    def _delay(self):
        """Přidá náhodné zpoždění mezi requesty."""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)

    def check_url(self, url: str, retries: int = 2) -> bool:
        """
        Zkontroluje, zda URL vede na aktivní stránku.

        Args:
            url: URL k ověření
            retries: Počet pokusů při selhání

        Returns:
            True pokud je URL aktivní, False pokud ne
        """
        if not url or url == 'N/A':
            return False

        # Parsuj URL pro kontrolu formátu
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
        except Exception:
            return False

        for attempt in range(retries):
            try:
                headers = self._get_headers()
                # Použij HEAD request pro rychlejší kontrolu
                response = self.session.head(url, headers=headers, timeout=10, allow_redirects=True)

                # Pokud HEAD nefunguje, zkus GET
                if response.status_code == 405:  # Method Not Allowed
                    response = self.session.get(url, headers=headers, timeout=10, allow_redirects=True)

                # Kontrola status kódu
                if response.status_code == 200:
                    return True
                elif response.status_code == 404:
                    # Inzerát byl smazán
                    return False
                elif response.status_code == 410:  # Gone
                    return False
                elif response.status_code == 429:  # Rate limit
                    wait_time = (2 ** attempt) * 5
                    if self.verbose:
                        print(f"      ⚠️  Rate limit! Čekám {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Jiné chyby - zkus znovu
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return False

            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return False
            except Exception as e:
                if self.verbose and attempt == retries - 1:
                    print(f"      ❌ Chyba: {str(e)[:50]}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return False

        return False


def clean_xlsx_file(input_file: Path, output_dir: Path, check_links: bool = True) -> str:
    """
    Očistí XLSX soubor od neaktivních inzerátů.

    Args:
        input_file: Cesta ke vstupnímu XLSX souboru
        output_dir: Složka pro výstupní soubor
        check_links: Pokud True, zkontroluje každý odkaz (pomalé!)

    Returns:
        Cesta k výstupnímu souboru
    """
    print(f"\n{'='*60}")
    print(f"ČIŠTĚNÍ XLSX SOUBORU - OVĚŘENÍ AKTIVNÍCH INZERÁTŮ")
    print(f"{'='*60}\n")

    if not input_file.exists():
        print(f"❌ Soubor {input_file} neexistuje!")
        return ""

    print(f"📂 Vstupní soubor: {input_file.name}")
    print(f"🔍 Kontrola odkazů: {'Ano' if check_links else 'Ne (pouze deduplikace)'}\n")

    # Načti Excel
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"❌ Chyba při načítání souboru: {e}")
        return ""

    # Najdi sloupce
    def find_column(df, possible_names):
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    name_col = find_column(df, ['Jméno makléře', 'jmeno_maklere'])
    all_links_col = find_column(df, ['Všechny odkazy', 'vsechny_odkazy'])
    links_col = find_column(df, ['Odkazy', 'odkazy'])
    count_col = find_column(df, ['Počet inzerátů', 'pocet_inzeratu', 'Počet unikátních inzerátů'])

    if not name_col:
        print("❌ Chybí sloupec s jménem makléře!")
        return ""

    # Slovník pro statistiky
    stats = {
        'total_agents': len(df),
        'total_links_before': 0,
        'total_links_after': 0,
        'active_links': 0,
        'inactive_links': 0,
        'checked_links': 0,
    }

    cleaner = LinkCleaner(verbose=True) if check_links else None

    # Projdi všechny řádky
    cleaned_rows = []
    for idx, row in df.iterrows():
        agent_name = row[name_col] if name_col and pd.notna(row[name_col]) else "N/A"
        print(f"\n📋 [{idx+1}/{len(df)}] {agent_name}")

        # Načti odkazy
        links = set()

        # Prioritizuj "Všechny odkazy"
        if all_links_col and pd.notna(row[all_links_col]):
            links_str = str(row[all_links_col])
            links = set([link.strip() for link in links_str.split('|')
                        if link.strip() and link.strip() != 'N/A'])
        elif links_col and pd.notna(row[links_col]):
            links_str = str(row[links_col])
            links = set([link.strip() for link in links_str.split('\n')
                        if link.strip() and link.strip() != 'N/A'
                        and not link.strip().startswith('...')])

        stats['total_links_before'] += len(links)

        if not links:
            print("   ⚠️  Žádné odkazy k ověření")
            cleaned_rows.append(row.to_dict())
            continue

        print(f"   📊 Počet odkazů před čištěním: {len(links)}")

        # Pokud je zapnutá kontrola odkazů
        if check_links and cleaner:
            active_links = set()

            for link_idx, link in enumerate(sorted(links), 1):
                print(f"   🔗 [{link_idx}/{len(links)}] Kontroluji: {link[:60]}...", end=' ')

                is_active = cleaner.check_url(link)
                stats['checked_links'] += 1

                if is_active:
                    active_links.add(link)
                    stats['active_links'] += 1
                    print("✓ Aktivní")
                else:
                    stats['inactive_links'] += 1
                    print("✗ Neaktivní")

                # Přidej zpoždění mezi requesty
                if link_idx < len(links):
                    cleaner._delay()

            links = active_links
            stats['total_links_after'] += len(active_links)
            print(f"   ✓ Počet odkazů po čištění: {len(active_links)}")

        else:
            # Pouze deduplikace bez kontroly
            stats['total_links_after'] += len(links)
            print(f"   ✓ Deduplikováno: {len(links)} unikátních odkazů")

        # Aktualizuj řádek
        row_dict = row.to_dict()

        # Aktualizuj počet inzerátů
        if count_col:
            row_dict[count_col] = len(links)

        # Aktualizuj odkazy
        sorted_odkazy = sorted(links)
        odkazy_display = '\n'.join(sorted_odkazy[:20])
        if len(sorted_odkazy) > 20:
            odkazy_display += f'\n... (celkem {len(sorted_odkazy)} odkazů)'

        if links_col:
            row_dict[links_col] = odkazy_display if odkazy_display else 'N/A'

        if all_links_col:
            row_dict[all_links_col] = '|'.join(sorted_odkazy) if sorted_odkazy else 'N/A'

        cleaned_rows.append(row_dict)

    # Vytvoř DataFrame z očištěných dat
    df_cleaned = pd.DataFrame(cleaned_rows)

    # Vytvoř výstupní soubor
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"cleaned_{input_file.stem}_{timestamp}.xlsx"

    # Ulož do Excel
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_cleaned.to_excel(writer, index=False, sheet_name='Makléři')

            worksheet = writer.sheets['Makléři']

            # Najdi index sloupce "Odkazy"
            odkazy_col_idx = None
            for idx, col in enumerate(df_cleaned.columns):
                if col == 'Odkazy':
                    odkazy_col_idx = idx
                    break

            # Nastav šířky sloupců
            for idx, col in enumerate(df_cleaned.columns):
                max_length = max(
                    df_cleaned[col].astype(str).apply(lambda x: len(str(x).split('\n')[0])).max(),
                    len(col)
                ) + 2

                if col == 'Odkazy':
                    max_length = min(max_length, 80)
                elif col in ['Inzeráty', 'Všechny odkazy']:
                    max_length = min(max_length, 60)
                elif col == 'Email':
                    max_length = min(max_length, 35)
                else:
                    max_length = min(max_length, 30)

                worksheet.column_dimensions[chr(65 + idx)].width = max_length

            # Formátování buněk
            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2), start=2):
                for cell_idx, cell in enumerate(row):
                    cell.alignment = Alignment(wrap_text=True, vertical='top')

                    # Pokud je to sloupec "Odkazy" a obsahuje URL
                    if odkazy_col_idx is not None and cell_idx == odkazy_col_idx:
                        cell_value = str(cell.value) if cell.value else ""
                        if cell_value and cell_value != 'N/A':
                            urls = [url.strip() for url in cell_value.split('\n') if url.strip()]
                            if urls:
                                first_url = urls[0]
                                if first_url.startswith('http'):
                                    cell.hyperlink = first_url
                                    cell.value = first_url
                                    cell.font = Font(color="0563C1", underline="single")

                                if len(urls) > 1:
                                    all_urls_text = '\n'.join(urls)
                                    cell.value = all_urls_text

        print(f"\n{'='*60}")
        print(f"STATISTIKY")
        print(f"{'='*60}")
        print(f"📊 Celkem makléřů: {stats['total_agents']}")
        print(f"📊 Odkazů před čištěním: {stats['total_links_before']}")
        if check_links:
            print(f"✓ Aktivních odkazů: {stats['active_links']}")
            print(f"✗ Neaktivních odkazů: {stats['inactive_links']}")
        print(f"📊 Odkazů po čištění: {stats['total_links_after']}")
        print(f"💾 Uloženo: {output_file}")
        print(f"{'='*60}\n")

        return str(output_file)

    except Exception as e:
        print(f"\n❌ Chyba při ukládání souboru: {e}")
        return ""


def main():
    """Hlavní funkce pro čištění XLSX souborů."""
    base_dir = Path(__file__).parent

    print("""
╔═══════════════════════════════════════════════════════════╗
║        ČIŠTĚNÍ XLSX SOUBORŮ - OVĚŘENÍ INZERÁTŮ            ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Nabídni výběr mezi složkami
    data_dir = base_dir / "data"
    data_clean_dir = base_dir / "data_clean"

    print("Vyber zdrojovou složku:")
    print("  1. data/ (původní soubory)")
    print("  2. data_clean/ (již očištěné soubory)")
    print("  3. Vlastní cesta")

    choice = input("Volba [1]: ").strip() or "1"

    if choice == "1":
        input_dir = data_dir
    elif choice == "2":
        input_dir = data_clean_dir
    elif choice == "3":
        custom_path = input("Zadej cestu ke složce: ").strip()
        input_dir = Path(custom_path)
    else:
        print("❌ Neplatná volba!")
        return

    if not input_dir.exists():
        print(f"❌ Složka {input_dir} neexistuje!")
        return

    # Najdi všechny XLSX soubory
    xlsx_files = list(input_dir.glob("*.xlsx"))

    if not xlsx_files:
        print(f"❌ Ve složce {input_dir} nebyly nalezeny žádné XLSX soubory!")
        return

    print(f"\n📂 Nalezeno {len(xlsx_files)} XLSX souborů:")
    for idx, f in enumerate(xlsx_files, 1):
        print(f"   {idx}. {f.name}")

    # Vyber soubor
    if len(xlsx_files) == 1:
        file_idx = 0
    else:
        file_choice = input(f"\nVyber soubor [1]: ").strip() or "1"
        try:
            file_idx = int(file_choice) - 1
            if file_idx < 0 or file_idx >= len(xlsx_files):
                print("❌ Neplatná volba!")
                return
        except ValueError:
            print("❌ Neplatný vstup!")
            return

    input_file = xlsx_files[file_idx]

    # Výstupní složka
    output_dir = data_clean_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Zeptej se na kontrolu odkazů
    print("\n⚠️  DŮLEŽITÉ: Kontrola odkazů může trvat velmi dlouho!")
    print("   Pro 100 odkazů to může být 5-10 minut.")
    check_links = input("Zkontrolovat aktivitu odkazů? [y/N]: ").strip().lower() in ('y', 'yes', 'a', 'ano')

    print(f"\n📂 Výstupní složka: {output_dir}")
    print(f"🔍 Kontrola odkazů: {'Ano' if check_links else 'Ne (pouze deduplikace)'}")

    input("\nStiskni ENTER pro start... (nebo Ctrl+C pro zrušení)")

    # Spusť čištění
    result = clean_xlsx_file(input_file, output_dir, check_links=check_links)

    if result:
        print("\n✨ Hotovo!")
    else:
        print("\n❌ Čištění se nezdařilo.")


if __name__ == "__main__":
    main()
