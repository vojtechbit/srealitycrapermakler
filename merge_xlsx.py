#!/usr/bin/env python3
"""
Sloučí více XLSX souborů z různých běhů scraperu.
Deduplikuje inzeráty podle URL, protože jeden inzerát může být ve více skupinách.
"""

from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import pandas as pd
from openpyxl.styles import Alignment, Font


def merge_xlsx_files(input_dir: Path, output_dir: Path) -> str:
    """
    Sloučí všechny XLSX soubory ze zadané složky.

    Args:
        input_dir: Složka se vstupními XLSX soubory
        output_dir: Složka pro výstupní soubor

    Returns:
        Cesta k výstupnímu souboru
    """
    print(f"\n{'='*60}")
    print(f"SLOUČENÍ XLSX SOUBORŮ - MAKLÉŘI")
    print(f"{'='*60}\n")

    # Najdi všechny XLSX soubory
    xlsx_files = list(input_dir.glob("*.xlsx"))

    if not xlsx_files:
        print(f"❌ Ve složce {input_dir} nebyly nalezeny žádné XLSX soubory!")
        return ""

    print(f"📂 Nalezeno {len(xlsx_files)} XLSX souborů:")
    for f in xlsx_files:
        print(f"   - {f.name}")
    print()

    # Slovník pro ukládání dat makléřů
    # Klíč: (jméno, telefon, realitní kancelář) - unikátní identifikace makléře
    agents: Dict[tuple, Dict] = {}

    # Procházej všechny soubory
    for xlsx_file in xlsx_files:
        print(f"📖 Načítám: {xlsx_file.name}...", end=" ")

        try:
            df = pd.read_excel(xlsx_file)

            # Očekávané sloupce (může být česky nebo anglicky)
            name_cols = ['Jméno makléře', 'jmeno_maklere', 'Jmeno maklere']
            phone_cols = ['Telefon', 'telefon']
            email_cols = ['Email', 'email']
            company_cols = ['Realitní kancelář', 'realitni_kancelar', 'Realitni kancelar']
            region_cols = ['Kraj', 'kraj']
            city_cols = ['Město', 'mesto', 'Mesto']
            count_cols = ['Počet inzerátů', 'pocet_inzeratu', 'Pocet inzeratu']
            types_cols = ['Typy nemovitostí', 'typy_nemovitosti', 'Typy nemovitosti']
            # Priorita: "Všechny odkazy" obsahuje kompletní seznam, "Odkazy" jen zobrazené
            all_links_cols = ['Všechny odkazy', 'vsechny_odkazy']
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
            all_links_col = find_column(df, all_links_cols)  # Nový sloupec s VŠEMI odkazy
            links_col = find_column(df, links_cols)
            listings_col = find_column(df, listings_cols)

            if not name_col:
                print(f"⚠️  Přeskakuji - chybí sloupec s jménem makléře")
                continue

            # Projdi všechny řádky
            for _, row in df.iterrows():
                # Vytvoř unikátní klíč pro makléře
                agent_name = str(row[name_col]) if name_col and pd.notna(row[name_col]) else "N/A"
                agent_phone = str(row[phone_col]) if phone_col and pd.notna(row[phone_col]) else "N/A"
                agent_company = str(row[company_col]) if company_col and pd.notna(row[company_col]) else "N/A"

                agent_key = (agent_name, agent_phone, agent_company)

                # Pokud makléř ještě není v slovníku, přidej ho
                if agent_key not in agents:
                    agents[agent_key] = {
                        'jmeno_maklere': agent_name,
                        'telefon': agent_phone,
                        'email': str(row[email_col]) if email_col and pd.notna(row[email_col]) else "N/A",
                        'realitni_kancelar': agent_company,
                        'kraj': str(row[region_col]) if region_col and pd.notna(row[region_col]) else "N/A",
                        'mesto': str(row[city_col]) if city_col and pd.notna(row[city_col]) else "N/A",
                        'typy_nemovitosti': set(),
                        'odkazy': set(),  # Použij set pro automatickou deduplikaci
                        'inzeraty': set(),  # Použij set pro automatickou deduplikaci
                    }

                agent = agents[agent_key]

                # Přidej odkazy (deduplikace pomocí set)
                # Prioritizuj "Všechny odkazy" (oddělené |), pak fallback na "Odkazy" (oddělené \n)
                if all_links_col and pd.notna(row[all_links_col]):
                    links_str = str(row[all_links_col])
                    # Rozdělí podle | (nový formát)
                    links = [link.strip() for link in links_str.split('|') if link.strip() and link.strip() != 'N/A']
                    agent['odkazy'].update(links)
                elif links_col and pd.notna(row[links_col]):
                    links_str = str(row[links_col])
                    # Rozdělí podle nového řádku (starý formát)
                    links = [link.strip() for link in links_str.split('\n')
                            if link.strip() and link.strip() != 'N/A' and not link.strip().startswith('...')]
                    agent['odkazy'].update(links)

                # Přidej inzeráty
                if listings_col and pd.notna(row[listings_col]):
                    listings_str = str(row[listings_col])
                    listings = [listing.strip() for listing in listings_str.split('\n')
                               if listing.strip() and listing.strip() != 'N/A' and listing.strip() != '...']
                    agent['inzeraty'].update(listings)

                # Přidej typy nemovitostí
                if types_col and pd.notna(row[types_col]):
                    types_str = str(row[types_col])
                    types = [t.strip() for t in types_str.split(',') if t.strip() and t.strip() != 'N/A']
                    agent['typy_nemovitosti'].update(types)

            print(f"✓ {len(df)} řádků")

        except Exception as e:
            print(f"❌ Chyba: {str(e)}")
            continue

    if not agents:
        print("\n❌ Nebyly nalezeny žádné validní data!")
        return ""

    print(f"\n✓ Celkem nalezeno {len(agents)} unikátních makléřů")

    # Vytvoř výstupní data
    results = []
    for agent_key, agent in agents.items():
        # Spočítej unikátní inzeráty podle odkazů
        unique_listings_count = len(agent['odkazy']) if agent['odkazy'] else 0

        # Pokud nejsou odkazy, použij počet unikátních názvů inzerátů
        if unique_listings_count == 0:
            unique_listings_count = len(agent['inzeraty'])

        # Seřaď odkazy pro konzistentní výstup
        sorted_odkazy = sorted(agent['odkazy']) if agent['odkazy'] else []
        sorted_inzeraty = sorted(agent['inzeraty']) if agent['inzeraty'] else []

        # Pro Excel zobrazíme prvních 20 odkazů + info o celkovém počtu
        odkazy_display = '\n'.join(sorted_odkazy[:20])
        if len(sorted_odkazy) > 20:
            odkazy_display += f'\n... (celkem {len(sorted_odkazy)} odkazů)'

        inzeraty_display = '\n'.join(sorted_inzeraty[:20])
        if len(sorted_inzeraty) > 20:
            inzeraty_display += f'\n... (celkem {len(sorted_inzeraty)} inzerátů)'

        results.append({
            'Jméno makléře': agent['jmeno_maklere'],
            'Telefon': agent['telefon'],
            'Email': agent['email'],
            'Realitní kancelář': agent['realitni_kancelar'],
            'Kraj': agent['kraj'],
            'Město': agent['mesto'],
            'Počet unikátních inzerátů': unique_listings_count,
            'Typy nemovitostí': ', '.join(sorted(agent['typy_nemovitosti'])) if agent['typy_nemovitosti'] else 'N/A',
            'Odkazy': odkazy_display if odkazy_display else 'N/A',
            'Inzeráty': inzeraty_display if inzeraty_display else 'N/A',
            # Nový sloupec s VŠEMI odkazy pro případný další merge
            'Všechny odkazy': '|'.join(sorted_odkazy) if sorted_odkazy else 'N/A',
        })

    # Seřaď podle počtu inzerátů
    results.sort(key=lambda x: x['Počet unikátních inzerátů'], reverse=True)

    # Vytvoř DataFrame
    df = pd.DataFrame(results)

    # Vytvoř výstupní soubor
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"merged_agents_{timestamp}.xlsx"

    # Ulož do Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Makléři')

        worksheet = writer.sheets['Makléři']

        # Najdi index sloupce "Odkazy"
        odkazy_col_idx = None
        for idx, col in enumerate(df.columns):
            if col == 'Odkazy':
                odkazy_col_idx = idx
                break

        # Nastav šířky sloupců
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
    print(f"📈 Celkem unikátních inzerátů: {sum(r['Počet unikátních inzerátů'] for r in results)}")
    print(f"\n{'='*60}\n")

    return str(output_file)


def main():
    """Hlavní funkce pro sloučení XLSX souborů."""
    # Cesty
    base_dir = Path(__file__).parent
    input_dir = base_dir / "data_merge"
    output_dir = base_dir / "data"

    print("""
╔═══════════════════════════════════════════════════════════╗
║        SLOUČENÍ XLSX SOUBORŮ - MAKLÉŘI                    ║
╚═══════════════════════════════════════════════════════════╝
    """)

    print(f"📂 Vstupní složka: {input_dir}")
    print(f"📂 Výstupní složka: {output_dir}")
    print()

    if not input_dir.exists():
        print(f"❌ Složka {input_dir} neexistuje!")
        print(f"   Vytvoř ji a vlož do ní XLSX soubory, které chceš sloučit.")
        return

    # Spusť sloučení
    result = merge_xlsx_files(input_dir, output_dir)

    if result:
        print("✨ Hotovo!")
    else:
        print("❌ Sloučení se nezdařilo.")


if __name__ == "__main__":
    main()
