#!/usr/bin/env python3
"""
Vyčistí XLSX soubor s makléři od neaktivních inzerátů.
Kontroluje, zda odkazy na inzeráty stále existují (HTTP 200).
"""

from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import pandas as pd
from openpyxl.styles import Alignment, Font
import requests
import time
import random


def check_url_exists(url: str, timeout: int = 10, retries: int = 2) -> bool:
    """
    Zkontroluje, zda URL stále existuje.

    Args:
        url: URL k ověření
        timeout: Timeout v sekundách
        retries: Počet pokusů při chybě

    Returns:
        True pokud URL existuje (HTTP 2xx nebo 3xx), False jinak
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    for attempt in range(retries):
        try:
            response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            # 2xx a 3xx považujeme za aktivní
            if 200 <= response.status_code < 400:
                return True
            # 404 a 410 = určitě neexistuje
            elif response.status_code in (404, 410):
                return False
            # Pro ostatní chyby zkus GET (někdy HEAD nefunguje)
            else:
                response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                return 200 <= response.status_code < 400

        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return False
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return False

    return False


def clean_xlsx_file(input_file: Path, output_dir: Path, check_urls: bool = True) -> str:
    """
    Vyčistí XLSX soubor od neaktivních inzerátů.

    Args:
        input_file: Vstupní XLSX soubor
        output_dir: Složka pro výstupní soubor
        check_urls: Zda kontrolovat URL (pokud False, jen přepočítá statistiky)

    Returns:
        Cesta k výstupnímu souboru
    """
    print(f"\n{'='*60}")
    print(f"ČIŠTĚNÍ XLSX SOUBORU - MAKLÉŘI")
    print(f"{'='*60}\n")

    print(f"📂 Vstupní soubor: {input_file.name}")
    print(f"🔍 Kontrola URL: {'ANO' if check_urls else 'NE'}")
    print()

    # Načti data
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"❌ Chyba při načítání souboru: {str(e)}")
        return ""

    # Očekávané sloupce
    name_cols = ['Jméno makléře', 'jmeno_maklere', 'Jmeno maklere']
    phone_cols = ['Telefon', 'telefon']
    email_cols = ['Email', 'email']
    company_cols = ['Realitní kancelář', 'realitni_kancelar', 'Realitni kancelar']
    region_cols = ['Kraj', 'kraj']
    city_cols = ['Město', 'mesto', 'Mesto']
    types_cols = ['Typy nemovitostí', 'typy_nemovitosti', 'Typy nemovitosti']
    links_cols = ['Odkazy', 'odkazy', 'inzeraty_odkazy']
    listings_cols = ['Inzeráty', 'inzeraty', 'Inzeraty']

    # Najdi správné názvy sloupců
    def find_column(df, possible_names):
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    name_col = find_column(df, name_cols)
    phone_col = find_column(df, phone_cols)
    email_col = find_column(df, email_cols)
    company_col = find_column(df, company_cols)
    region_col = find_column(df, region_cols)
    city_col = find_column(df, city_cols)
    types_col = find_column(df, types_cols)
    links_col = find_column(df, links_cols)
    listings_col = find_column(df, listings_cols)

    if not name_col or not links_col:
        print(f"❌ Chybí povinné sloupce (Jméno makléře, Odkazy)")
        return ""

    print(f"📊 Načteno {len(df)} makléřů")

    # Slovník pro ukládání vyčištěných dat
    agents: Dict[tuple, Dict] = {}
    total_links_checked = 0
    total_links_active = 0
    total_links_inactive = 0

    # Projdi všechny řádky
    for idx, row in df.iterrows():
        agent_name = str(row[name_col]) if name_col and pd.notna(row[name_col]) else "N/A"
        agent_phone = str(row[phone_col]) if phone_col and pd.notna(row[phone_col]) else "N/A"
        agent_company = str(row[company_col]) if company_col and pd.notna(row[company_col]) else "N/A"

        agent_key = (agent_name, agent_phone, agent_company)

        print(f"🔍 {idx+1}/{len(df)}: {agent_name[:30]}...", end=' ')

        # Vytáhni odkazy
        links = []
        if links_col and pd.notna(row[links_col]):
            links_str = str(row[links_col])
            links = [link.strip() for link in links_str.split('\n')
                    if link.strip() and link.strip() != 'N/A' and link.strip().startswith('http')]

        # Vytáhni názvy inzerátů
        listings = []
        if listings_col and pd.notna(row[listings_col]):
            listings_str = str(row[listings_col])
            listings = [listing.strip() for listing in listings_str.split('\n')
                       if listing.strip() and listing.strip() != 'N/A' and listing.strip() != '...']

        # Kontroluj URL, pokud je to požadováno
        active_links = set()
        active_listings = set()

        if check_urls and links:
            print(f"({len(links)} odkazů)", end=' ')
            for i, link in enumerate(links):
                total_links_checked += 1

                # Zpoždění mezi požadavky
                if i > 0:
                    time.sleep(random.uniform(0.5, 1.5))

                if check_url_exists(link):
                    active_links.add(link)
                    total_links_active += 1
                    # Přidej i odpovídající inzerát, pokud existuje
                    if i < len(listings):
                        active_listings.add(listings[i])
                else:
                    total_links_inactive += 1

            print(f"✓ {len(active_links)} aktivních")
        else:
            # Bez kontroly - přidej všechny
            active_links.update(links)
            active_listings.update(listings)
            print("✓ (bez kontroly)")

        # Pokud makléř nemá žádné aktivní inzeráty, přeskoč ho
        if not active_links:
            continue

        # Přidej makléře do slovníku
        if agent_key not in agents:
            agents[agent_key] = {
                'jmeno_maklere': agent_name,
                'telefon': agent_phone,
                'email': str(row[email_col]) if email_col and pd.notna(row[email_col]) else "N/A",
                'realitni_kancelar': agent_company,
                'kraj': str(row[region_col]) if region_col and pd.notna(row[region_col]) else "N/A",
                'mesto': str(row[city_col]) if city_col and pd.notna(row[city_col]) else "N/A",
                'typy_nemovitosti': set(),
                'odkazy': set(),
                'inzeraty': set(),
            }

        agent = agents[agent_key]
        agent['odkazy'].update(active_links)
        agent['inzeraty'].update(active_listings)

        # Přidej typy nemovitostí
        if types_col and pd.notna(row[types_col]):
            types_str = str(row[types_col])
            types = [t.strip() for t in types_str.split(',') if t.strip() and t.strip() != 'N/A']
            agent['typy_nemovitosti'].update(types)

    if not agents:
        print("\n❌ Po vyčištění nezbyli žádní makléři s aktivními inzeráty!")
        return ""

    print(f"\n✓ Po vyčištění zůstalo {len(agents)} makléřů")

    if check_urls:
        print(f"📊 Statistiky URL:")
        print(f"   Zkontrolováno: {total_links_checked}")
        print(f"   Aktivních: {total_links_active}")
        print(f"   Neaktivních: {total_links_inactive}")
        print(f"   Úspěšnost: {100 * total_links_active / total_links_checked:.1f}%")

    # Vytvoř výstupní data
    results = []
    for agent_key, agent in agents.items():
        unique_listings_count = len(agent['odkazy']) if agent['odkazy'] else len(agent['inzeraty'])

        results.append({
            'Jméno makléře': agent['jmeno_maklere'],
            'Telefon': agent['telefon'],
            'Email': agent['email'],
            'Realitní kancelář': agent['realitni_kancelar'],
            'Kraj': agent['kraj'],
            'Město': agent['mesto'],
            'Počet aktivních inzerátů': unique_listings_count,
            'Typy nemovitostí': ', '.join(sorted(agent['typy_nemovitosti'])) if agent['typy_nemovitosti'] else 'N/A',
            'Odkazy': '\n'.join(sorted(agent['odkazy'])[:10]) + ('\n...' if len(agent['odkazy']) > 10 else ''),
            'Inzeráty': '\n'.join(sorted(agent['inzeraty'])[:10]) + ('\n...' if len(agent['inzeraty']) > 10 else ''),
        })

    # Seřaď podle počtu inzerátů
    results.sort(key=lambda x: x['Počet aktivních inzerátů'], reverse=True)

    # Vytvoř DataFrame
    df_clean = pd.DataFrame(results)

    # Vytvoř výstupní soubor
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"clean_{input_file.stem}_{timestamp}.xlsx"

    # Ulož do Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_clean.to_excel(writer, index=False, sheet_name='Makléři')

        worksheet = writer.sheets['Makléři']

        # Najdi index sloupce "Odkazy"
        odkazy_col_idx = None
        for idx, col in enumerate(df_clean.columns):
            if col == 'Odkazy':
                odkazy_col_idx = idx
                break

        # Nastav šířky sloupců
        for idx, col in enumerate(df_clean.columns):
            max_length = max(
                df_clean[col].astype(str).apply(lambda x: len(str(x).split('\n')[0])).max(),
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

    print(f"\n💾 Uloženo: {output_file}")
    print(f"📊 Počet makléřů: {len(results)}")
    print(f"📈 Celkem aktivních inzerátů: {sum(r['Počet aktivních inzerátů'] for r in results)}")
    print(f"\n{'='*60}\n")

    return str(output_file)


def main():
    """Hlavní funkce pro čištění XLSX souborů."""
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data_clean"
    output_dir = base_dir / "data"

    print("""
╔═══════════════════════════════════════════════════════════╗
║        ČIŠTĚNÍ XLSX SOUBORŮ - MAKLÉŘI                     ║
╚═══════════════════════════════════════════════════════════╝
    """)

    print(f"📂 Vstupní složka: {data_dir}")
    print(f"📂 Výstupní složka: {output_dir}")
    print()

    if not data_dir.exists():
        print(f"❌ Složka {data_dir} neexistuje!")
        print(f"   Vytvoř ji a vlož do ní XLSX soubor, který chceš vyčistit.")
        return

    # Najdi XLSX soubory
    xlsx_files = list(data_dir.glob("*.xlsx"))

    if not xlsx_files:
        print(f"❌ Ve složce {data_dir} nebyly nalezeny žádné XLSX soubory!")
        return

    print(f"📂 Nalezeno {len(xlsx_files)} XLSX souborů:")
    for i, f in enumerate(xlsx_files, 1):
        print(f"   {i}. {f.name}")
    print()

    # Vyber soubor
    if len(xlsx_files) == 1:
        input_file = xlsx_files[0]
        print(f"✓ Automaticky vybrán: {input_file.name}\n")
    else:
        while True:
            choice = input(f"Vyber soubor [1-{len(xlsx_files)}]: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(xlsx_files):
                input_file = xlsx_files[int(choice) - 1]
                break
            print("Neplatná volba, zkus to prosím znovu.")

    # Zeptej se, zda kontrolovat URL
    check_urls = input("\nKontrolovat, zda inzeráty stále existují? [Y/n]: ").strip().lower()
    check_urls = check_urls in ("", "y", "yes", "a", "ano")

    if check_urls:
        print("\n⚠️  POZOR: Kontrola URL může trvat dlouho (~ 1-2s na URL)!")
        input("Stiskni ENTER pro pokračování... (nebo Ctrl+C pro zrušení)\n")

    # Spusť čištění
    result = clean_xlsx_file(input_file, output_dir, check_urls)

    if result:
        print("✨ Hotovo!")
    else:
        print("❌ Čištění se nezdařilo.")


if __name__ == "__main__":
    main()
