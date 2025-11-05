#!/usr/bin/env python3
"""
Scraper pro profily makléřů ze Sreality.cz

Umožňuje získat všechny inzeráty a kontakty na konkrétní makléře
na základě jejich profilových URL nebo user_id.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from scrapers.sreality import SrealityScraper


def print_banner():
    """Vytiskne úvodní banner."""
    print("=" * 80)
    print("🔍 Sreality.cz - Scraper profilů makléřů")
    print("=" * 80)
    print()


def read_agent_urls_from_file(file_path: str) -> list[str]:
    """
    Načte URL nebo ID makléřů ze souboru.

    Args:
        file_path: Cesta k textovému souboru s URL/ID (jeden na řádek)

    Returns:
        Seznam URL nebo ID
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
            return lines
    except FileNotFoundError:
        print(f"❌ Soubor nenalezen: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Chyba při čtení souboru: {e}")
        sys.exit(1)


def save_to_excel(records: list, output_path: str) -> None:
    """
    Uloží záznamy do Excel souboru.

    Args:
        records: Seznam záznamů (dict)
        output_path: Cesta k výstupnímu souboru
    """
    if not records:
        print("⚠️  Žádné záznamy k uložení.")
        return

    # Vytvoř složku, pokud neexistuje
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Převeď na DataFrame
    df = pd.DataFrame(records)

    # Seřaď podle počtu inzerátů
    if "pocet_inzeratu" in df.columns:
        df = df.sort_values(by="pocet_inzeratu", ascending=False)

    # Ulož do Excelu
    df.to_excel(output_path, index=False, engine="openpyxl")

    print(f"\n✅ Data uložena do: {output_path}")
    print(f"📊 Celkem makléřů: {len(df)}")

    if "pocet_inzeratu" in df.columns:
        total_listings = df["pocet_inzeratu"].sum()
        print(f"🏠 Celkem inzerátů: {total_listings}")


def main():
    """Hlavní funkce."""
    parser = argparse.ArgumentParser(
        description="Scraper profilů makléřů ze Sreality.cz",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Příklady použití:

  # Scrape jednoho makléře podle URL
  python3 scrape_agent_profiles.py -u "https://www.sreality.cz/makler/12345"

  # Scrape více makléřů
  python3 scrape_agent_profiles.py -u "https://www.sreality.cz/makler/12345" "https://www.sreality.cz/makler/67890"

  # Scrape podle user_id
  python3 scrape_agent_profiles.py -u 12345 67890

  # Načti URL ze souboru
  python3 scrape_agent_profiles.py -f makleri.txt

  # Ulož do vlastního souboru
  python3 scrape_agent_profiles.py -u 12345 -o muj_export.xlsx

  # Bez stahování detailů (rychlejší)
  python3 scrape_agent_profiles.py -u 12345 --no-details

Formát souboru s URL (jeden na řádek):
  https://www.sreality.cz/makler/12345
  https://www.sreality.cz/makler/67890
  123456
  # Toto je komentář a bude ignorován
        """,
    )

    parser.add_argument(
        "-u", "--urls",
        nargs="+",
        help="URL nebo user_id makléřů (oddělené mezerou)",
    )

    parser.add_argument(
        "-f", "--file",
        help="Soubor s URL nebo user_id makléřů (jeden na řádek)",
    )

    parser.add_argument(
        "-o", "--output",
        help="Cesta k výstupnímu Excel souboru (výchozí: data/makleri_profily_TIMESTAMP.xlsx)",
    )

    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Nestahovat detaily inzerátů (rychlejší, ale méně přesné kontakty)",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Zobrazit podrobnější výstup",
    )

    args = parser.parse_args()

    # Validace vstupů
    if not args.urls and not args.file:
        parser.error("Musíš zadat buď -u/--urls nebo -f/--file")

    print_banner()

    # Získej seznam URL
    agent_urls = []

    if args.urls:
        agent_urls.extend(args.urls)

    if args.file:
        file_urls = read_agent_urls_from_file(args.file)
        agent_urls.extend(file_urls)
        print(f"📁 Načteno {len(file_urls)} URL ze souboru: {args.file}")

    if not agent_urls:
        print("❌ Žádné URL k zpracování.")
        sys.exit(1)

    print(f"🔍 Celkem makléřů k zpracování: {len(agent_urls)}\n")

    # Vytvoř scraper
    scraper = SrealityScraper()

    # Spusť scraping
    print("⏳ Stahuji data...")
    print("⚠️  Toto může trvat několik minut v závislosti na počtu inzerátů.\n")

    try:
        result = scraper.scrape_agent_profiles(
            agent_urls=agent_urls,
            fetch_details=not args.no_details,
        )

        # Zobraz chyby, pokud nějaké jsou
        if result.errors:
            print("\n⚠️  Chyby při zpracování:")
            for error in result.errors:
                print(f"   • {error}")
            print()

        # Zobraz výsledky
        if result.records:
            print(f"✅ Úspěšně načteno {len(result.records)} makléřů\n")

            # Zobraz přehled
            if args.verbose:
                print("📋 Přehled makléřů:")
                print("-" * 80)
                for i, record in enumerate(result.records[:10], 1):
                    print(f"{i}. {record.get('jmeno_maklere', 'Neznámý')}")
                    print(f"   Realitní kancelář: {record.get('realitni_kancelar', '-')}")
                    print(f"   Telefon: {record.get('telefon', '-')}")
                    print(f"   Email: {record.get('email', '-')}")
                    print(f"   Počet inzerátů: {record.get('pocet_inzeratu', 0)}")
                    print(f"   Profil: {record.get('profil_url', '-')}")
                    print()

                if len(result.records) > 10:
                    print(f"... a dalších {len(result.records) - 10} makléřů\n")

            # Ulož do Excelu
            if args.output:
                output_path = args.output
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"data/makleri_profily_{timestamp}.xlsx"

            save_to_excel(result.records, output_path)

        else:
            print("⚠️  Nepodařilo se získat žádná data.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Přerušeno uživatelem (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Chyba při scrapování: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 80)
    print("✅ Hotovo!")
    print("=" * 80)


if __name__ == "__main__":
    main()
