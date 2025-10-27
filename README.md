# Sreality Scraper Makléřů

Scraper pro získání kontaktů na makléře ze Sreality.cz.

## Instalace

```bash
pip install -r requirements.txt
```

## Použití

### Základní spuštění
```bash
python sreality_scraper.py
```

### Programové použití
```python
from sreality_scraper import AgentScraper

scraper = AgentScraper()
scraper.scrape_agents(
    category_main=1,        # 1=Byty, 2=Domy, 3=Pozemky, 4=Komerční, 5=Ostatní
    category_type=1,        # 1=Prodej, 2=Pronájem, 3=Dražby
    locality_region_id=10,  # 10=Praha (volitelné)
    max_pages=10,
    fetch_details=True      # True=přesnější data, False=rychlejší
)
scraper.save_to_excel()
```

## Výstup

Excel soubor v `data/` složce s těmito sloupci:
- Jméno makléře
- Telefon
- Email
- Realitní kancelář
- Kraj
- Město
- Počet inzerátů
- Typy nemovitostí
- Inzeráty (ukázka)
- Odkazy (ukázka)

## Kódy krajů

- 10 = Praha
- 11 = Středočeský
- 12 = Jihočeský
- 13 = Plzeňský
- 14 = Karlovarský
- 15 = Ústecký
- 16 = Liberecký
- 17 = Královéhradecký
- 18 = Pardubický
- 19 = Vysočina
- 20 = Jihomoravský
- 21 = Olomoucký
- 22 = Zlínský
- 23 = Moravskoslezský

## Poznámky

- Scraper respektuje rate limity
- Pro fetch_details=True je scraping pomalejší (více requestů)
- Data se deduplikují podle makléře
- Používej odpovědně
