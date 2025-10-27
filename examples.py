from sreality_scraper import AgentScraper

def example_prague_flats():
    """Makléři prodávající byty v Praze"""
    scraper = AgentScraper(verbose=True)
    scraper.scrape_agents(
        category_main=1,
        category_type=1,
        locality_region_id=10,
        max_pages=5,
        fetch_details=True
    )
    scraper.save_to_excel("makleri_praha_byty.xlsx")

def example_houses_all():
    """Makléři prodávající domy v celé ČR"""
    scraper = AgentScraper(verbose=True)
    scraper.scrape_agents(
        category_main=2,
        category_type=1,
        locality_region_id=None,
        max_pages=10,
        fetch_details=False
    )
    scraper.save_to_excel("makleri_domy_cr.xlsx")

def example_commercial_brno():
    """Makléři prodávající komerční nemovitosti v Jihomoravském kraji"""
    scraper = AgentScraper(verbose=True)
    scraper.scrape_agents(
        category_main=4,
        category_type=1,
        locality_region_id=20,
        max_pages=3,
        fetch_details=True
    )
    scraper.save_to_excel("makleri_komercni_brno.xlsx")

if __name__ == "__main__":
    print("Příklady:")
    print("1 - Makléři prodávající byty v Praze")
    print("2 - Makléři prodávající domy v celé ČR")
    print("3 - Makléři prodávající komerční nemovitosti - Jihomoravský kraj")

    choice = input("\nVolba (1-3): ").strip()

    if choice == "1":
        example_prague_flats()
    elif choice == "2":
        example_houses_all()
    elif choice == "3":
        example_commercial_brno()
    else:
        print("Neplatná volba")
