# Sreality Scraper Makléřů

Scraper pro získání kontaktů na makléře ze Sreality.cz. Výstupem je Excel tabulka s kontakty.

---

## 📥 Jak stáhnout a spustit na Macu (krok za krokem)

### Krok 1: Zkontroluj/Nainstaluj Python

Otevři **Terminal** (najdeš v Applications → Utilities → Terminal) a zadej:

```bash
python3 --version
```

Pokud vidíš něco jako `Python 3.8.0` nebo vyšší, máš Python. Pokud ne, nainstaluj ho:

**Instalace Pythonu:**
1. Jdi na [python.org/downloads](https://www.python.org/downloads/)
2. Stáhni a nainstaluj nejnovější verzi pro Mac
3. Restartuj Terminal a zkus znovu `python3 --version`

### Krok 2: Zkontroluj/Nainstaluj Git

V Terminálu zadej:

```bash
git --version
```

Pokud vidíš verzi Gitu, máš ho. Pokud ne:

**Instalace Gitu:**
- Mac tě automaticky vyzve k instalaci Xcode Command Line Tools
- Klikni "Install" a počkej na dokončení
- Nebo jdi na [git-scm.com](https://git-scm.com/download/mac) a stáhni instalátor

### Krok 3: Stáhni projekt z GitHubu

V Terminálu zadej následující příkazy (jeden po druhém):

```bash
cd ~/Desktop
git clone https://github.com/vojtechbit/srealitycrapermakler.git
cd srealitycrapermakler
```

**Co se stalo:**
- `cd ~/Desktop` = přešel jsi do složky Desktop (Plocha)
- `git clone ...` = stáhl jsi projekt z GitHubu
- `cd srealitycrapermakler` = přešel jsi do složky projektu

Nyní jsi ve složce projektu. Ověř si to příkazem:

```bash
pwd
```

Měl bys vidět něco jako: `/Users/tvojejmeno/Desktop/srealitycrapermakler`

### Krok 4: Nainstaluj potřebné knihovny

V Terminálu (stále ve složce projektu) zadej:

```bash
pip3 install -r requirements.txt
```

Počkej, až se nainstalují tři knihovny: `requests`, `pandas`, `openpyxl`.

**Uvidíš nějaké warningy? To je normální! ✅**

Pokud uvidíš něco jako:
```
WARNING: The scripts ... are installed in '...' which is not on PATH.
WARNING: You are using pip version 21.2.4; however, version 25.3 is available.
```

**Nemusíš nic řešit!** Tyto warningy nejsou kritické. Důležité je, že na konci vidíš:
```
Successfully installed certifi-... requests-... pandas-... openpyxl-...
```

Pokud vidíš `Successfully installed`, vše je OK a můžeš pokračovat.

### Krok 4.5: Ověř instalaci (volitelné, ale doporučené)

Pro jistotu ověř, že je vše správně nainstalované:

```bash
python3 test_instalace.py
```

Měl bys vidět:
```
✅ requests 2.32.5
✅ pandas 2.3.3
✅ openpyxl 3.1.5
✨ Všechny knihovny jsou nainstalované!
```

Pokud vidíš všechny ✅, vše funguje a můžeš pokračovat. Pokud vidíš ❌, opakuj Krok 4.

### Krok 5: Spusť scraper

```bash
python3 sreality_scraper.py
```

Program se tě zeptá na několik otázek (viz níže).

---

## 🚀 Použití scraperu

### Interaktivní režim

Po spuštění `python3 sreality_scraper.py` se program zeptá:

**1. Typ nemovitosti (1-5):**
- `1` = Byty
- `2` = Domy
- `3` = Pozemky
- `4` = Komerční
- `5` = Ostatní

**2. Typ inzerátu (1-3):**
- `1` = Prodej
- `2` = Pronájem
- `3` = Dražby

**3. Kraj (volitelné):**
- Zadej číslo kraje (viz tabulka níže) nebo nech prázdné pro celou ČR
- Příklad: `10` pro Prahu

**4. Max. počet stránek:**
- 1 stránka = cca 60 inzerátů
- Doporučuji: `5-10` pro začátek
- **Zadej `0` pro VŠECHNY stránky** (celé Sreality) - VAROVÁNÍ: může trvat hodiny!

**5. Stahovat detaily? (y/n):**
- `y` = Přesnější data (telefon, email), ale **pomalejší** (2-3x déle)
- `n` = Rychlejší, ale méně informací (často chybí telefony/emaily)

### Příklad použití

```
Typ nemovitosti: 1=Byty, 2=Domy, 3=Pozemky, 4=Komerční, 5=Ostatní
Typ [1]: 1

Typ inzerátu: 1=Prodej, 2=Pronájem, 3=Dražby
Typ [1]: 1

Kraj (10=Praha, 11=Středočeský, prázdné=celá ČR)
Kraj []: 10

Max. stránek [10]: 5

Stahovat detaily? (pomalejší, ale přesnější) [y/n]: y
```

Toto stáhne makléře prodávající byty v Praze z prvních 5 stránek (cca 300 inzerátů).

---

## 📊 Výstup

### Kde se uloží Excel?

Excel soubor se uloží do složky **`data/`** ve složce projektu s názvem `makleri_YYYYMMDD_HHMMSS.xlsx`.

**Úplná cesta:**
```
/Users/tvojejmeno/Desktop/srealitycrapermakler/data/makleri_20250127_143022.xlsx
```

Program ti ukáže přesnou cestu na konci:
```
📂 Excel soubor: /Users/vojtechbroucek/Desktop/srealitycrapermakler/data/makleri_20250127_143022.xlsx
```

### Jak poznat že to funguje?

**Když to FUNGUJE správně, uvidíš:**
```
📄 Stránka 1/10... ✓ 60 inzerátů | 45 makléřů
📄 Stránka 2/10... ✓ 60 inzerátů | 78 makléřů
📄 Stránka 3/10... ✓ 60 inzerátů | 102 makléřů
...
✨ Dokončeno! 156 makléřů z 600 inzerátů
📂 Excel soubor: /Users/.../data/makleri_20250127_143022.xlsx
```

**Když se to POKAZÍ (Cloudflare blokace):**
```
📄 Stránka 1/10... ❌ CHYBA! Pravděpodobně Cloudflare blokace.
   Zkus to znovu za chvíli, nebo z jiné sítě.
```

**Co dělat při chybě:**
1. Počkej 10-15 minut
2. Zkus znovu
3. Vypni VPN (pokud používáš)
4. Zkus z jiné WiFi (např. mobilní hotspot)

### Sloupce v Excelu:

| Sloupec | Popis |
|---------|-------|
| **Jméno makléře** | Celé jméno makléře |
| **Telefon** | Telefonní číslo (pokud dostupné) |
| **Email** | Email (pokud dostupný) |
| **Realitní kancelář** | Název RK (za koho makléř prodává) |
| **Kraj** | Kraj kde makléř působí |
| **Město** | Město kde makléř působí |
| **Počet inzerátů** | Kolik inzerátů má tento makléř |
| **Typy nemovitostí** | Jaké typy prodává (Byt, Dům, atd.) |
| **Inzeráty** | Ukázka prvních 5 inzerátů |
| **Odkazy** | Odkazy na prvních 3 inzeráty |

Data jsou seřazená podle počtu inzerátů (nejvíce aktivní makléři nahoře).

---

## ⚙️ Jak to funguje (technický popis)

### Proces scrapování:

1. **Připojení k Sreality API** (1-3 sekundy)
   - Scraper se připojí na oficiální API Sreality.cz
   - Používá rotaci User-Agent pro vyhnutí se blokování

2. **Stahování inzerátů** (1-3 sekundy na stránku)
   - Stahuje 60 inzerátů za stránku
   - Mezi každým requestem čeká 1-3 sekundy (respektování rate limitů)
   - Pokud je `fetch_details=True`, stahuje detail každého inzerátu (+ další 1-3s na inzerát)

3. **Extrakce dat o makléřích**
   - Z každého inzerátu vytáhne:
     - Jméno makléře (z `seller.user_name` nebo `broker.name`)
     - Telefon (z `contact.phone`)
     - Email (z `contact.email`)
     - Realitní kancelář (z `seller.company_name`)
     - Lokalita (z `locality` → parsuje kraj a město)
     - Typ nemovitosti (z názvu inzerátu)

4. **Deduplikace makléřů**
   - Makléře deduplikuje podle klíče: `jméno_realitka_telefon`
   - Pokud stejný makléř má více inzerátů, agreguje je do jednoho záznamu
   - Počítá celkový počet inzerátů pro každého makléře

5. **Uložení do Excelu** (1-2 sekundy)
   - Vytvoří pandas DataFrame
   - Seřadí podle počtu inzerátů (sestupně)
   - Uloží do `data/makleri_TIMESTAMP.xlsx`

### Časové odhady:

| Režim | Čas na stránku (60 inzerátů) | Čas na 5 stránek (300 inzerátů) | Čas na VŠECHNY stránky (0) |
|-------|-------------------------------|-----------------------------------|----------------------------|
| **Bez detailů** (`fetch_details=False`) | ~3-5 sekund | ~15-25 sekund | **1-2 hodiny** |
| **S detaily** (`fetch_details=True`) | ~3-5 minut | ~15-25 minut | **10-20 hodin!** |

**Doporučení:**
- Pro rychlý test: `fetch_details=False`, `max_pages=2-3`
- Pro kompletní data: `fetch_details=True`, `max_pages=10-20`
- Pro CELÉ Sreality: `fetch_details=False`, `max_pages=0` (zadej 0) - **nech to běžet přes noc!**

---

## 🗺️ Kódy krajů

| Kód | Kraj |
|-----|------|
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

Pokud chceš celou ČR, nech pole prázdné (stiskni Enter).

---

## ⚠️ Možné chyby a řešení

### Chyba: `ModuleNotFoundError: No module named 'requests'`

**Řešení:**
```bash
pip3 install -r requirements.txt
```

Nebo nainstaluj ručně:
```bash
pip3 install requests pandas openpyxl
```

---

### Warningy při `pip3 install` - je to OK?

**ANO! Tyto warningy jsou normální a NENÍ třeba nic řešit:**

**1. `WARNING: The scripts ... are installed in '...' which is not on PATH.`**
- **Co to znamená:** Některé pomocné skripty (numpy-config, f2py) nejsou v PATH
- **Je to problém?** NE! Scraper tyto skripty nepotřebuje
- **Můžeš ignorovat** a pokračovat normálně

**2. `WARNING: You are using pip version 21.2.4; however, version 25.3 is available.`**
- **Co to znamená:** Máš starší verzi pipu
- **Je to problém?** NE! Starší pip stále funguje perfektně
- **Chceš upgradovat?** (volitelné):
  ```bash
  python3 -m pip install --upgrade pip
  ```

**3. `Defaulting to user installation because normal site-packages is not writeable`**
- **Co to znamená:** Instaluje se do tvé uživatelské složky místo systémové
- **Je to problém?** NE! To je normální na Macu
- **Můžeš ignorovat**

**✅ Důležité je vidět na konci:**
```
Successfully installed certifi-... requests-... pandas-... openpyxl-...
```

Pokud vidíš `Successfully installed`, **všechno je OK!** Můžeš spustit scraper.

**Pro ověření spusť:**
```bash
python3 test_instalace.py
```

---

### Chyba: `❌ HTTP 403`

**Co to znamená:**
- Sreality.cz blokuje request (cloudflare ochrana)
- Stává se hlavně v cloud prostředích nebo při VPN

**Řešení:**
1. Zkus bez VPN
2. Zkus z jiné sítě (mobilní data)
3. Zvyš delay v kódu (otevři `sreality_scraper.py` a změň `MIN_DELAY = 3`, `MAX_DELAY = 6`)
4. Počkaj pár hodin a zkus znovu

---

### Chyba: `❌ Rate limit! Čekám Xs...`

**Co to znamená:**
- Posíláš requesty příliš rychle
- Scraper automaticky počká a zkusí znovu

**Řešení:**
- Nech scraper běžet, automaticky se zpomalí
- Pokud se opakuje často, zvyš delay (viz výše)

---

### Chyba: `Permission denied` při vytváření souboru

**Řešení:**
```bash
mkdir -p data
chmod 755 data
```

---

### Program se zasekl / nereaguje

**Řešení:**
- Stiskni `Ctrl+C` pro zastavení
- Počkej 10-15 sekund (může dokončovat request)
- Spusť znovu

---

### Excel soubor je prázdný nebo má málo dat

**Možné příčiny:**
1. Mnoho makléřů nemá veřejné kontakty
2. Používáš `fetch_details=False` → chybí detaily
3. Byl jsi zablokován (403 chyby)

**Řešení:**
- Použij `fetch_details=True` pro přesnější data
- Zkus jiný kraj nebo typ nemovitosti
- Zkontroluj, jestli nebyly 403 chyby v logu

---

## 💡 Tipy pro efektivní použití

### Tip 1: Začni s malým testem
```
Typ: 1 (Byty)
Typ inzerátu: 1 (Prodej)
Kraj: 10 (Praha)
Max. stránek: 2
Detaily: n
```
Tento test trvá ~10 sekund a ověříš, že vše funguje.

### Tip 2: Pro kompletní data použij detaily
```
Typ: 1 (Byty)
Typ inzerátu: 1 (Prodej)
Kraj: (prázdné - celá ČR)
Max. stránek: 20
Detaily: y
```
Toto trvá ~40-60 minut, ale získáš kvalitní databázi makléřů.

### Tip 3: Kombinuj více běhů
- Spusť scraper pro různé typy nemovitostí (byty, domy, komerční)
- Získáš více makléřů
- Můžeš pak Excel soubory spojit

---

## 📝 Programové použití (pokročilé)

Pokud chceš scraper ovládat z Pythonu:

```python
from sreality_scraper import AgentScraper

scraper = AgentScraper(verbose=True)

# Byty na prodej v Praze
scraper.scrape_agents(
    category_main=1,        # 1=Byty
    category_type=1,        # 1=Prodej
    locality_region_id=10,  # 10=Praha
    max_pages=5,
    fetch_details=True      # True=přesnější data
)

# Ulož do vlastního souboru
scraper.save_to_excel("moje_makleri.xlsx")
```

Spusť:
```bash
python3 muj_script.py
```

---

## 🔍 Hotové příklady

Spusť připravené příklady:

```bash
python3 examples.py
```

Obsahuje:
1. Makléři prodávající byty v Praze
2. Makléři prodávající domy v celé ČR
3. Makléři prodávající komerční nemovitosti - Jihomoravský kraj

---

## 📂 Struktura projektu

```
srealitycrapermakler/
├── sreality_scraper.py    # Hlavní scraper
├── examples.py            # Hotové příklady
├── test_instalace.py      # Test instalace knihoven
├── requirements.txt       # Závislosti
├── data/                  # Výstupní Excel soubory (vytvoří se automaticky)
├── README.md              # Tento soubor
└── LICENSE                # Licence
```

---

## ⚖️ Poznámky k používání

- **Používej odpovědně** - respektuj rate limity
- **Nepoužívej příliš často** - max 1x za několik hodin
- **Data jsou veřejná** - scraper stahuje pouze veřejně dostupné kontakty
- **Pro osobní použití** - nepoužívej pro spam nebo obtěžování
- **Respektuj GDPR** - získané kontakty používej v souladu se zákonem

---

## 📞 Podpora

Máš problém?
1. Zkontroluj sekci **Možné chyby a řešení** výše
2. Ujisti se, že máš nejnovější verzi: `git pull`
3. Zkus přeinstalovat dependencies: `pip3 install -r requirements.txt --upgrade`

---

**Vytvořeno s pomocí Claude**
