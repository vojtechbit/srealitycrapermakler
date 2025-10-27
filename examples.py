"""
Příklady použití Sreality Scraperu
Zkopíruj a uprav podle svých potřeb
"""

from sreality_scraper import SrealityScraper

# ===== PŘÍKLAD 1: Byty na prodej v Praze =====
def example_prague_flats():
    scraper = SrealityScraper(verbose=True)
    
    scraper.scrape_listings(
        category_main=1,        # Byty
        category_type=1,        # Prodej
        locality_region_id=10,  # Praha
        max_pages=5             # 5 stránek = cca 300 nabídek
    )
    
    scraper.save_to_excel("praha_byty_prodej.xlsx")


# ===== PŘÍKLAD 2: Domy na pronájem - celá ČR =====
def example_houses_rent():
    scraper = SrealityScraper(verbose=True)
    
    scraper.scrape_listings(
        category_main=2,        # Domy
        category_type=2,        # Pronájem
        locality_region_id=None, # Celá ČR
        max_pages=10
    )
    
    scraper.save_to_excel("domy_pronajem_cr.xlsx")


# ===== PŘÍKLAD 3: Pozemky v Moravskoslezském kraji =====
def example_land_moravia():
    scraper = SrealityScraper(verbose=True)
    
    scraper.scrape_listings(
        category_main=3,        # Pozemky
        category_type=1,        # Prodej
        locality_region_id=23,  # Moravskoslezský
        max_pages=3
    )
    
    scraper.save_to_excel("pozemky_msk.xlsx")
    scraper.save_to_csv("pozemky_msk.csv")  # Uložit i do CSV


# ===== PŘÍKLAD 4: Komerční nemovitosti - Brno =====
def example_commercial_brno():
    scraper = SrealityScraper(verbose=True)
    
    scraper.scrape_listings(
        category_main=4,        # Komerční
        category_type=1,        # Prodej
        locality_region_id=20,  # Jihomoravský (Brno)
        max_pages=2
    )
    
    scraper.save_to_excel("komercni_brno.xlsx")


# ===== SPUŠTĚNÍ =====
if __name__ == "__main__":
    print("Vyber příklad:")
    print("1 - Byty na prodej v Praze")
    print("2 - Domy na pronájem - celá ČR")
    print("3 - Pozemky v Moravskoslezském kraji")
    print("4 - Komerční nemovitosti - Brno")
    
    choice = input("\nTvá volba (1-4): ").strip()
    
    if choice == "1":
        example_prague_flats()
    elif choice == "2":
        example_houses_rent()
    elif choice == "3":
        example_land_moravia()
    elif choice == "4":
        example_commercial_brno()
    else:
        print("❌ Neplatná volba!")
