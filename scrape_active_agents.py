#!/usr/bin/env python3
"""
🎯 EFEKTIVNÍ SCRAPER: Aktivní makléři s kompletními profily

Tento scraper kombinuje oba přístupy:
1. Najde aktivní makléře podle kategorie/kraje (rychlé)
2. Pro každého získá VŠECHNY inzeráty a kompletní profil (přesné)

Výsledek: Aktivní makléři s přesným počtem inzerátů a správnými URL profilu.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from scrapers.sreality import SrealityScraper


def save_to_excel_with_formatting(records: list, output_path: str) -> None:
    """Uloží data do Excelu s hyperlinky a formátováním."""
    if not records:
        print("⚠️  Žádné záznamy k uložení.")
        return

    # Vytvoř složku
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Převeď na DataFrame a seřaď
    df = pd.DataFrame(records)
    if "pocet_inzeratu" in df.columns:
        df = df.sort_values(by="pocet_inzeratu", ascending=False)

    # Ulož do Excelu
    df.to_excel(output_path, index=False, engine="openpyxl")

    # Přidej hyperlinky a formátování
    wb = load_workbook(output_path)
    ws = wb.active

    # Najdi sloupce s linky
    headers = [cell.value for cell in ws[1]]
    link_columns = []

    for idx, header in enumerate(headers, 1):
        if header in ["profil_url"]:
            link_columns.append((idx, header))

    # Přidej hyperlinky
    for row_idx in range(2, ws.max_row + 1):
        for col_idx, col_name in link_columns:
            cell = ws.cell(row=row_idx, column=col_idx)
            url = cell.value

            if url and isinstance(url, str) and url.startswith("http"):
                cell.hyperlink = url
                cell.value = "Profil makléře"
                cell.font = Font(color="0000FF", underline="single")

    # Automatická šířka sloupců
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)

        for cell in column:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except:
                pass

        adjusted_width = min(max_length + 2, 60)
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(output_path)

    print(f"\n✅ Data uložena do: {output_path}")
    print(f"📊 Celkem makléřů: {len(df)}")

    if "pocet_inzeratu" in df.columns:
        total_listings = df["pocet_inzeratu"].sum()
        print(f"🏠 Celkem inzerátů: {total_listings}")


def main():
    """Hlavní funkce."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--category-main",
        type=int,
        default=1,
        help="Typ nemovitosti (1=Byty, 2=Domy, 3=Pozemky, 4=Komerční, 5=Ostatní) [výchozí: 1]",
    )

    parser.add_argument(
        "--category-type",
        type=int,
        default=1,
        help="Typ inzerátu (1=Prodej, 2=Pronájem, 3=Dražby) [výchozí: 1]",
    )

    parser.add_argument(
        "--locality",
        type=int,
        help="ID kraje (10=Praha, 11=Středočeský, ..., 23=Moravskoslezský) [výchozí: celá ČR]",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximální počet stránek pro hledání makléřů [výchozí: 5]",
    )

    parser.add_argument(
        "--full-scan",
        action="store_true",
        help="Projít VŠECHNY stránky (může trvat hodiny)",
    )

    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Nestahovat detaily inzerátů (rychlejší, ale méně přesné kontakty)",
    )

    parser.add_argument(
        "-o", "--output",
        help="Cesta k výstupnímu souboru [výchozí: data/active_agents_TIMESTAMP.xlsx]",
    )

    args = parser.parse_args()

    print("="*80)
    print("🎯 SCRAPER AKTIVNÍCH MAKLÉŘŮ S KOMPLETNÍMI PROFILY")
    print("="*80)
    print()
    print("💡 První použití? Přečti si README_ACTIVE_AGENTS.md")
    print("   nebo spusť: cat README_ACTIVE_AGENTS.md")
    print()

    category_names = {1: "Byty", 2: "Domy", 3: "Pozemky", 4: "Komerční", 5: "Ostatní"}
    type_names = {1: "Prodej", 2: "Pronájem", 3: "Dražby"}
    region_names = {
        10: "Praha", 11: "Středočeský", 12: "Jihočeský", 13: "Plzeňský",
        14: "Karlovarský", 15: "Ústecký", 16: "Liberecký", 17: "Královéhradecký",
        18: "Pardubický", 19: "Vysočina", 20: "Jihomoravský", 21: "Olomoucký",
        22: "Zlínský", 23: "Moravskoslezský"
    }

    print("📋 Parametry:")
    print(f"   • Typ nemovitosti: {category_names.get(args.category_main, 'Neznámý')}")
    print(f"   • Typ inzerátu: {type_names.get(args.category_type, 'Neznámý')}")
    print(f"   • Kraj: {region_names.get(args.locality, 'Celá ČR')}")
    print(f"   • Max. stránek: {'VŠECHNY' if args.full_scan else args.max_pages}")
    print(f"   • Detaily: {'Ne' if args.no_details else 'Ano'}")
    print()

    print("⏳ Spouštím scraping...")
    print("   Fáze 1: Najdu aktivní makléře podle kategorie")
    print("   Fáze 2: Pro každého získám všechny inzeráty a profil")
    print()

    try:
        scraper = SrealityScraper()

        result = scraper.scrape_active_agents_full_profiles(
            category_main=args.category_main,
            category_type=args.category_type,
            locality_region_id=args.locality,
            max_pages=args.max_pages,
            full_scan=args.full_scan,
            fetch_details=not args.no_details,
        )

        if result.errors:
            print("\n⚠️  Chyby:")
            for error in result.errors:
                print(f"   • {error}")

        if result.records:
            print(f"\n✅ Úspěšně načteno {len(result.records)} aktivních makléřů")

            # Výstupní soubor
            if args.output:
                output_path = args.output
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"data/active_agents_{timestamp}.xlsx"

            save_to_excel_with_formatting(result.records, output_path)

        else:
            print("\n⚠️  Nepodařilo se získat žádná data.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Přerušeno uživatelem (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Chyba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "="*80)
    print("✅ Hotovo!")
    print("="*80)


if __name__ == "__main__":
    main()
