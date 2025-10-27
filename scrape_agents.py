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
    scrapers = list_scrapers()
    print("Dostupné platformy:")
    for scraper in scrapers:
        print(f"  - {scraper.slug:15s} {scraper.name}")
    selected = input("Zadejte platformy oddělené čárkou (např. 'sreality,linkedin'): ")
    slugs = [slug.strip() for slug in selected.split(",") if slug.strip()]
    return slugs or ["sreality"]


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
        help="Interaktivně se zeptá na výběr platformy, pokud není zadána.",
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
