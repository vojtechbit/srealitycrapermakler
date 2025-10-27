#!/usr/bin/env python3
"""Unified CLI for scraping real-estate agent contacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd

from scrapers import get_scraper, list_scrapers
from scrapers.base import BaseScraper, ScraperResult, merge_results


def _available_slugs() -> List[str]:
    return sorted(scraper.slug for scraper in list_scrapers())


def _prompt_for_platform() -> List[str]:
    scrapers = sorted(list_scrapers(), key=lambda s: s.slug)

    print("\n" + "="*60)
    print("DOSTUPNÉ PLATFORMY:")
    print("="*60)
    for idx, scraper in enumerate(scrapers, start=1):
        print(f"  {idx:>2}. {scraper.name:25s} ({scraper.slug})")
    print(f"   0. VŠECHNY PLATFORMY")
    print("="*60)

    print("\nMůžeš vybrat:")
    print("  • Jedno číslo (např. '1' pro první platformu)")
    print("  • Více čísel oddělených čárkou (např. '1,2,3')")
    print("  • Slug platformy (např. 'sreality')")
    print("  • Více slugů oddělených čárkou (např. 'sreality,bezrealitky')")
    print("  • '0' nebo 'all' pro všechny platformy")

    while True:
        selected = input("\nVyber platformy [1]: ").strip()

        # Defaultně Sreality
        if not selected:
            return ["sreality"]

        # Všechny platformy
        if selected in ("0", "all", "všechny", "vsechny"):
            return [s.slug for s in scrapers]

        # Parsování výběru
        slugs = []
        parts = [p.strip() for p in selected.split(",") if p.strip()]

        for part in parts:
            # Číslo platformy
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(scrapers):
                    slugs.append(scrapers[idx - 1].slug)
                else:
                    print(f"⚠️  Neplatné číslo: {idx}")
                    slugs = []
                    break
            # Slug platformy
            else:
                matching = [s for s in scrapers if s.slug == part.lower()]
                if matching:
                    slugs.append(matching[0].slug)
                else:
                    print(f"⚠️  Neznámá platforma: {part}")
                    slugs = []
                    break

        if slugs:
            return slugs

        print("Zkus to prosím znovu.\n")


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--platform",
        "-p",
        action="append",
        dest="platforms",
        help="Vybrané platformy (slug). Lze zadat vícekrát.",
    )
    parser.add_argument(
        "--all-platforms",
        action="store_true",
        help="Spustí scraping na všech dostupných platformách.",
    )
    parser.add_argument(
        "--full-scan",
        action="store_true",
        help="Pokud platforma podporuje, projde všechny stránky (může trvat hodiny).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Maximální počet stránek pro platformy, které stránkují výsledky.",
    )
    parser.add_argument(
        "--category-main",
        type=int,
        default=1,
        help="Kategorie nemovitostí pro Sreality (1=Byty, 2=Domy, 3=Pozemky, 4=Komerční, 5=Ostatní).",
    )
    parser.add_argument(
        "--category-type",
        type=int,
        default=1,
        help="Typ nabídky pro Sreality (1=Prodej, 2=Pronájem, 3=Dražby).",
    )
    parser.add_argument(
        "--locality",
        type=int,
        help="ID regionu pro Sreality (např. 10 = Praha).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Cílový soubor (Excel .xlsx). Bez zadání se jen vypíše souhrn.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Pouze vypíše dostupné platformy a skončí.",
    )
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Interaktivně se zeptá na výběr platforem (můžeš vybrat více najednou).",
    )
    return parser.parse_args(argv)


def _validate_platforms(platforms: Iterable[str]) -> List[str]:
    available = set(_available_slugs())
    invalid = [slug for slug in platforms if slug not in available]
    if invalid:
        raise SystemExit(f"Neznámé platformy: {', '.join(invalid)}")
    return list(dict.fromkeys(platforms))


def _save_to_excel(result: ScraperResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(result.records)
    df.to_excel(output, index=False)


def _prompt_for_scraping_params(platforms: List[str]) -> dict:
    """Interaktivně se ptá na parametry scrapování."""
    params = {}

    # Jestli některá platforma potřebuje Sreality-specifické parametry
    needs_sreality_params = "sreality" in platforms

    if needs_sreality_params:
        print("\n" + "="*60)
        print("PARAMETRY PRO SREALITY:")
        print("="*60)

        print("\nTyp nemovitosti:")
        print("  1=Byty  2=Domy  3=Pozemky  4=Komerční  5=Ostatní")
        category_main = input("Vyber typ [1]: ").strip() or "1"
        params["category_main"] = int(category_main)

        print("\nTyp inzerátu:")
        print("  1=Prodej  2=Pronájem  3=Dražby")
        category_type = input("Vyber typ [1]: ").strip() or "1"
        params["category_type"] = int(category_type)

        print("\nKraj (prázdné = celá ČR):")
        print("  10=Praha  11=Středočeský  12=Jihočeský  13=Plzeňský")
        print("  14=Karlovarský  15=Ústecký  16=Liberecký")
        print("  17=Královéhradecký  18=Pardubický  19=Vysočina")
        print("  20=Jihomoravský  21=Olomoucký  22=Zlínský  23=Moravskoslezský")
        locality = input("Vyber kraj [celá ČR]: ").strip()
        params["locality"] = int(locality) if locality else None
    else:
        # Pro ostatní platformy použij defaultní hodnoty
        params["category_main"] = 1
        params["category_type"] = 1
        params["locality"] = None

    print("\n" + "="*60)
    print("PARAMETRY PRO VŠECHNY PLATFORMY:")
    print("="*60)

    print("\nMaximální počet stránek:")
    print("  Zadej číslo (např. 10) nebo 0 pro všechny dostupné stránky")
    print("  ⚠️  Pozor: 0 může trvat velmi dlouho (hodiny)!")
    max_pages = input("Max. stránek [10]: ").strip() or "10"
    params["max_pages"] = None if max_pages == "0" else int(max_pages)

    print("\nVýstupní Excel soubor:")
    print("  Zadej název souboru (např. 'makleri.xlsx')")
    print("  Nebo nech prázdné pro výchozí název")
    output_file = input("Soubor [výsledky.xlsx]: ").strip() or "výsledky.xlsx"
    if not output_file.endswith(".xlsx"):
        output_file += ".xlsx"
    params["output"] = output_file

    return params


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])

    if args.list:
        print("Dostupné platformy:")
        for scraper in list_scrapers():
            print(f"- {scraper.slug:15s} {scraper.name:30s} | {scraper.description}")
        return 0

    if args.all_platforms:
        platforms = _available_slugs()
    elif args.platforms:
        platforms = _validate_platforms(args.platforms)
    elif args.prompt:
        platforms = _validate_platforms(_prompt_for_platform())
    else:
        # Default behaviour: ask a simple question (backwards compatible).
        platforms = _validate_platforms(_prompt_for_platform())

    # Interaktivní dotazování na parametry (pokud nejsou zadány z CLI)
    if not any([args.max_pages, args.category_main != 1, args.category_type != 1, args.locality, args.output]):
        # Žádné parametry nebyly zadány z CLI, zeptej se interaktivně
        interactive_params = _prompt_for_scraping_params(platforms)
        # Přepiš args s interaktivními parametry
        args.max_pages = interactive_params.get("max_pages", args.max_pages)
        args.category_main = interactive_params.get("category_main", args.category_main)
        args.category_type = interactive_params.get("category_type", args.category_type)
        args.locality = interactive_params.get("locality", args.locality)
        if not args.output and interactive_params.get("output"):
            args.output = Path(interactive_params["output"])

    print("Spouštím scraping pro:")
    for slug in platforms:
        scraper = get_scraper(slug)
        print(f"- {scraper.name} ({slug})")

    results: List[ScraperResult] = []
    for slug in platforms:
        scraper = get_scraper(slug)
        kwargs = {
            "category_main": args.category_main,
            "category_type": args.category_type,
            "locality_region_id": args.locality,
        }
        print("\n==============================")
        print(f"Platforma: {scraper.name} ({slug})")
        print(f"Popis: {scraper.description}")
        print(f"Rate-limit: {scraper.rate_limit_info}")
        if args.full_scan and not scraper.supports_full_scan:
            print("⚠️  Platforma nepodporuje plný průchod, použiji dostupný režim.")

        # Informace o délce trvání
        max_p = args.max_pages or (None if args.full_scan else 10)
        if max_p:
            print(f"📄 Stahuji max. {max_p} stránek...")
        else:
            print(f"📄 Stahuji všechny dostupné stránky (může trvat dlouho)...")
        print(f"⏳ Probíhá stahování (kvůli rate-limitingu může trvat několik minut)...\n")
        sys.stdout.flush()

        result = scraper.scrape(
            max_pages=args.max_pages,
            full_scan=args.full_scan,
            **kwargs,
        )
        if result.records:
            print(f"✓ {len(result.records)} záznamů")
        if result.warnings:
            print("⚠️  Varování:")
            for warning in result.warnings:
                print(f"   - {warning}")
        if result.errors:
            print("❌ Chyby:")
            for error in result.errors:
                print(f"   - {error}")
        results.append(result)

    merged = merge_results(results)
    print("\n==============================")
    print(f"Celkem nalezeno {len(merged.records)} unikátních záznamů.")

    if args.output:
        _save_to_excel(merged, args.output)
        print(f"Data uložena do {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
