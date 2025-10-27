# 🏠 Sreality Makler Scraper

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Lokální scraper pro stahování nabídek nemovitostí ze **Sreality.cz** do Excel souborů.

> ⚠️ **Poznámka**: Tento scraper není oficiálně podporován Sreality.cz. Používej odpovědně a respektuj podmínky použití.

## ✨ Funkce

✅ Stahuje nabídky **bytů, domů, pozemků, komerčních nemovitostí**  
✅ Ukládá data do **Excel (.xlsx)** nebo **CSV**  
✅ **Respektuje rate limiting** (2-5s delay mezi requesty)  
✅ **Rotace User-Agent** pro vyhnutí se blokování  
✅ **Retry logika** při chybách s exponential backoff  
✅ **Interaktivní rozhraní** v terminálu  
✅ **Konfigurovatelné parametry** vyhledávání  

---

## 🚀 Rychlý start

### 1. Klonuj repozitář

```bash
git clone https://github.com/vojtechbit/srealitymaklerscraper.git
cd srealitymaklerscraper
```

### 2. Nainstaluj závislosti

```bash
pip install -r requirements.txt
```

nebo:

```bash
pip3 install -r requirements.txt
```

### 3. Spusť scraper

```bash
python sreality_scraper.py
```

nebo jednoduchým scriptem (Mac/Linux):

```bash
chmod +x start.sh
./start.sh
```

---

## 📋 Požadavky

- **Python 3.8+** ([stáhnout](https://www.python.org/downloads/))
- **pip** (package manager)
- Knihovny (viz `requirements.txt`):
  - `requests` - HTTP requesty
  - `pandas` - zpracování dat
  - `openpyxl` - Excel export

---

## 💻 Použití

### Interaktivní režim

Při spuštění `python sreality_scraper.py` se program zeptá na:

1. **Typ nemovitosti:**
   - 1 = Byty
   - 2 = Domy
   - 3 = Pozemky
   - 4 = Komerční
   - 5 = Ostatní

2. **Typ inzerátu:**
   - 1 = Prodej
   - 2 = Pronájem
   - 3 = Dražby

3. **Kraj** (volitelné):
   - 10 = Praha
   - 23 = Moravskoslezský
   - ... nebo prázdné pro celou ČR

4. **Počet stránek:**
   - Kolik stránek výsledků stáhnout (1 stránka ≈ 60 nabídek)

### Programové použití

```python
from sreality_scraper import SrealityScraper

# Vytvoř scraper
scraper = SrealityScraper(verbose=True)

# Stáhni byty na prodej v Praze
scraper.scrape_listings(
    category_main=1,        # Byty
    category_type=1,        # Prodej
    locality_region_id=10,  # Praha
    max_pages=5
)

# Ulož do Excelu
scraper.save_to_excel("praha_byty.xlsx")
```

### Hotové příklady

Spusť připravené příklady:

```bash
python examples.py
```

Obsahuje příklady pro:
- Byty na prodej v Praze
- Domy na pronájem (celá ČR)
- Pozemky v Moravskoslezském kraji
- Komerční nemovitosti v Brně

---

## 📊 Výstupní data

Data se ukládají do složky **`data/`** ve formátu:

```
sreality_data_YYYYMMDD_HHMMSS.xlsx
```

### Sloupce v Excelu:

| Sloupec | Popis |
|---------|-------|
| `hash_id` | Unikátní ID nabídky |
| `name` | Název/popis nabídky |
| `locality` | Lokalita |
| `price` | Cena (text) |
| `price_czk` | Cena v Kč (číslo) |
| `price_note` | Poznámka k ceně |
| `url` | Odkaz na detail |
| `floor` | Patro |
| `area` | Plocha |
| `building_type` | Typ stavby |
| `ownership` | Vlastnictví |
| `full_address` | Plná adresa |
| `scraped_at` | Datum stažení |

---

## ⚙️ Konfigurace

V souboru `sreality_scraper.py` můžeš upravit třídu `Config`:

```python
class Config:
    MIN_DELAY = 2      # Minimální delay (sekundy)
    MAX_DELAY = 5      # Maximální delay
    MAX_PAGES = 50     # Výchozí max. stránek
    OUTPUT_DIR = "data"  # Složka pro výstupy
```

---

## 🗺️ ID krajů

| ID | Kraj |
|----|------|
| 10 | Praha |
| 11 | Středočeský |
| 12 | Jihočeský |
| 13 | Plzeňský |
| 14 | Karlovarský |
| 15 | Ústecký |
| 16 | Liberecký |
| 17 | Královéhradecký |
| 18 | Pardubický |
| 19 | Vysočina |
| 20 | Jihomoravský |
| 21 | Olomoucký |
| 22 | Zlínský |
| 23 | Moravskoslezský |

Nech prázdné pro **celou Českou republiku**.

---

## 🛡️ Bezpečnost & Etika

### Co scraper dělá:
✅ Respektuje rate limiting (pauzy mezi requesty)  
✅ Používá rotaci User-Agent  
✅ Stahuje pouze veřejně dostupná data  
✅ Neobchází CAPTCHAs ani anti-bot ochranu  

### Doporučení:
⚠️ Nepoužívej příliš často (max **1x za pár hodin**)  
⚠️ Nestahuj více dat, než potřebuješ  
⚠️ Data používej **pouze pro osobní účely**  
⚠️ Respektuj [podmínky použití](https://www.sreality.cz/) Sreality.cz  

---

## 🧪 Testování

Ověř, že máš všechny závislosti:

```bash
python test_setup.py
```

---

## 🐛 Řešení problémů

### Chyba: `ModuleNotFoundError`

```bash
pip install -r requirements.txt
```

### Chyba: `Permission denied`

```bash
chmod +x start.sh
chmod +x git_setup.sh
```

### Chyba 429 (Too Many Requests)

- Počkej **pár minut** a zkus znovu
- Zvyš `MIN_DELAY` a `MAX_DELAY` v konfiguraci

### Data se neukládají

- Zkontroluj, že máš práva zápisu do složky `data/`
- Ověř, že je nainstalována `openpyxl`: `pip install openpyxl`

---

## 📚 Dokumentace

- **[QUICKSTART.txt](QUICKSTART.txt)** - Rychlý návod k použití
- **[GIT_SETUP.md](GIT_SETUP.md)** - Návod pro Git a GitHub
- **[examples.py](examples.py)** - Hotové příklady kódu
- **[README.md](README.md)** - Tento soubor

---

## 🔄 Vývoj & Přispívání

### Struktura projektu

```
srealitymaklerscraper/
├── sreality_scraper.py    # Hlavní scraper
├── examples.py            # Příklady použití
├── test_setup.py          # Test závislostí
├── requirements.txt       # Python závislosti
├── start.sh               # Start script
├── git_setup.sh           # Git setup
├── data/                  # Výstupní data (gitignore)
├── README.md              # Dokumentace
├── QUICKSTART.txt         # Rychlý start
├── GIT_SETUP.md          # Git návod
└── .gitignore            # Git ignore
```

### Přispívání

1. Fork repozitář
2. Vytvoř feature branch (`git checkout -b feature/nova-funkce`)
3. Commit změny (`git commit -m 'Přidána nová funkce'`)
4. Push do branch (`git push origin feature/nova-funkce`)
5. Vytvoř Pull Request

---

## 📜 Licence

Tento projekt je poskytován "jak je" bez jakýchkoli záruk.  
Použití na **vlastní riziko**.

---

## 👤 Autor

**vojtechbit**  
🔗 GitHub: [@vojtechbit](https://github.com/vojtechbit)  
📦 Repozitář: [srealitymaklerscraper](https://github.com/vojtechbit/srealitymaklerscraper)

---

## 🙏 Poděkování

Vytvořeno s pomocí **Claude** (Anthropic).

---

## ⚠️ Disclaimer

Tento scraper **není oficiálně podporován** Sreality.cz ani žádnou jinou společností.  
Používáním tohoto nástroje souhlasíš s tím, že:
- Respektuješ podmínky použití Sreality.cz
- Nebudeš scraper používat pro komerční účely bez povolení
- Nebudeš přetěžovat servery Sreality.cz
- Data použiješ pouze pro osobní účely

---

## 📞 Podpora

Máš problém nebo nápad? 
- 🐛 [Vytvoř issue](https://github.com/vojtechbit/srealitymaklerscraper/issues)
- 💡 [Navrhni vylepšení](https://github.com/vojtechbit/srealitymaklerscraper/issues/new)

---

<div align="center">

**⭐ Pokud se ti projekt líbí, dej mu hvězdičku na GitHubu! ⭐**

Made with ❤️ in Czech Republic 🇨🇿

</div>
