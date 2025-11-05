#!/usr/bin/env python3
"""
Příklady použití scraperu profilů makléřů (programové použití)

Tento soubor ukazuje, jak použít scraper profilů makléřů
přímo z Pythonu (bez CLI).
"""

from scrapers.sreality import SrealityScraper
import pandas as pd
from datetime import datetime


def example_1_single_agent():
    """
    Příklad 1: Scraping jednoho makléře podle URL
    """
    print("=" * 80)
    print("PŘÍKLAD 1: Jeden makléř podle URL")
    print("=" * 80)

    scraper = SrealityScraper()

    # URL profilu makléře ze Sreality.cz
    agent_url = "https://www.sreality.cz/makler/123456"

    print(f"Scraping makléře: {agent_url}")

    result = scraper.scrape_agent_profiles(
        agent_urls=[agent_url],
        fetch_details=True,  # Stáhnout detaily pro přesnější kontakty
    )

    if result.records:
        agent = result.records[0]
        print(f"\n✅ Makléř: {agent['jmeno_maklere']}")
        print(f"   Telefon: {agent.get('telefon', '-')}")
        print(f"   Email: {agent.get('email', '-')}")
        print(f"   Počet inzerátů: {agent.get('pocet_inzeratu', 0)}")

        # Uložení do Excelu
        df = pd.DataFrame(result.records)
        output_file = f"data/example_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"\n📁 Uloženo do: {output_file}")
    else:
        print("⚠️ Nepodařilo se získat data")

    print()


def example_2_multiple_agents():
    """
    Příklad 2: Scraping více makléřů najednou
    """
    print("=" * 80)
    print("PŘÍKLAD 2: Více makléřů najednou")
    print("=" * 80)

    scraper = SrealityScraper()

    # Seznam URL nebo user_id
    agent_urls = [
        "https://www.sreality.cz/makler/123456",
        "https://www.sreality.cz/makler/789012",
        "345678",  # Můžeš použít jen ID
    ]

    print(f"Scraping {len(agent_urls)} makléřů...")

    result = scraper.scrape_agent_profiles(
        agent_urls=agent_urls,
        fetch_details=False,  # Bez detailů = rychlejší
    )

    print(f"\n✅ Získáno {len(result.records)} makléřů")

    if result.records:
        # Zobraz přehled
        for i, agent in enumerate(result.records, 1):
            print(f"{i}. {agent['jmeno_maklere']} - {agent.get('pocet_inzeratu', 0)} inzerátů")

        # Uložení do Excelu
        df = pd.DataFrame(result.records)
        output_file = f"data/example_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"\n📁 Uloženo do: {output_file}")

    if result.errors:
        print("\n⚠️ Chyby:")
        for error in result.errors:
            print(f"   • {error}")

    print()


def example_3_from_file():
    """
    Příklad 3: Načtení makléřů ze souboru
    """
    print("=" * 80)
    print("PŘÍKLAD 3: Načtení ze souboru")
    print("=" * 80)

    # Nejdřív vytvoř testovací soubor
    test_file = "data/test_agents.txt"

    with open(test_file, "w", encoding="utf-8") as f:
        f.write("# Testovací seznam makléřů\n")
        f.write("https://www.sreality.cz/makler/123456\n")
        f.write("789012\n")
        f.write("# Další makléř\n")
        f.write("345678\n")

    print(f"Vytvořen testovací soubor: {test_file}")

    # Načti URL ze souboru
    agent_urls = []
    with open(test_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                agent_urls.append(line)

    print(f"Načteno {len(agent_urls)} URL")

    # Scraping
    scraper = SrealityScraper()

    result = scraper.scrape_agent_profiles(
        agent_urls=agent_urls,
        fetch_details=True,
    )

    print(f"\n✅ Získáno {len(result.records)} makléřů")

    if result.records:
        df = pd.DataFrame(result.records)
        output_file = f"data/example_3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"📁 Uloženo do: {output_file}")

    print()


def example_4_custom_processing():
    """
    Příklad 4: Vlastní zpracování dat
    """
    print("=" * 80)
    print("PŘÍKLAD 4: Vlastní zpracování dat")
    print("=" * 80)

    scraper = SrealityScraper()

    agent_urls = ["123456", "789012"]

    result = scraper.scrape_agent_profiles(
        agent_urls=agent_urls,
        fetch_details=True,
    )

    if result.records:
        print(f"\n✅ Získáno {len(result.records)} makléřů\n")

        # Vlastní analýza
        print("📊 ANALÝZA:")
        print("-" * 80)

        for agent in result.records:
            print(f"\n👤 {agent['jmeno_maklere']}")
            print(f"   Společnost: {agent.get('realitni_kancelar', '-')}")
            print(f"   Region: {agent.get('kraj', '-')}")
            print(f"   Kontakty:")
            print(f"      • Telefon: {agent.get('telefon', '-')}")
            print(f"      • Email: {agent.get('email', '-')}")
            print(f"   Aktivita:")
            print(f"      • Počet inzerátů: {agent.get('pocet_inzeratu', 0)}")
            print(f"      • Specializace: {agent.get('specializace', '-')}")
            print(f"   Profil: {agent.get('profil_url', '-')}")

        # Export do CSV (místo Excelu)
        df = pd.DataFrame(result.records)

        # Vlastní úpravy
        df = df.sort_values(by="pocet_inzeratu", ascending=False)

        # Ulož jako CSV
        output_file = f"data/example_4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n📁 Uloženo do: {output_file}")

    print()


if __name__ == "__main__":
    print("\n🔍 PŘÍKLADY POUŽITÍ SCRAPERU PROFILŮ MAKLÉŘŮ\n")

    # Vyber, který příklad chceš spustit
    print("Dostupné příklady:")
    print("  1 - Jeden makléř podle URL")
    print("  2 - Více makléřů najednou")
    print("  3 - Načtení ze souboru")
    print("  4 - Vlastní zpracování dat")
    print()

    # Pro demo účely zavolej příklad 1 (v praxi by uživatel vybral)
    print("⚠️  POZNÁMKA: Tyto příklady používají testovací URL!")
    print("⚠️  Před spuštěním nahraď URL skutečnými profily makléřů.\n")

    # Odkomentuj příklad, který chceš spustit:
    # example_1_single_agent()
    # example_2_multiple_agents()
    # example_3_from_file()
    # example_4_custom_processing()

    print("✅ Pro spuštění příkladů odkomentuj volání funkcí na konci souboru.")
