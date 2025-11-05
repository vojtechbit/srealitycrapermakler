# Sreality Scraper Makléřů

Scraper pro získání kontaktů na makléře ze Sreality.cz. Výstupem je Excel tabulka s kontakty.

---

## 📥 Jak stáhnout a spustit (krok za krokem)

### 🍎 Pro Mac | 🪟 Pro Windows

Vyber svůj operační systém:
- **[Mac - návod níže](#-mac-návod)**
- **[Windows - návod níže](#-windows-návod)**

---

## 🍎 Mac návod

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

Pokud Terminál vypíše, že `pip3` (nebo `pip`) není nalezen, zadej příkaz přímo přes Python:

```bash
python3 -m pip install -r requirements.txt
```

Tato varianta obejde špatně nastavenou instalaci Pythonu a vždy najde správný `pip`.

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
python3 scrape_agents.py --prompt
```

Program se nejprve zeptá, z jakých platforem chceš stahovat data, a následně na parametry Sreality.cz (viz [Použití scraperu](#-použití-scraperu) níže).

---

## 🪟 Windows návod

### Krok 1: Zkontroluj/Nainstaluj Python

Otevři **Command Prompt** (CMD):
- Stiskni `Windows + R`
- Napiš `cmd` a stiskni Enter
- Otevře se černé okno (Command Prompt)

V Command Prompt zadej:

```cmd
python --version
```

Pokud vidíš něco jako `Python 3.8.0` nebo vyšší, máš Python. Pokud vidíš chybu `'python' is not recognized`, pokračuj instalací.

**Instalace Pythonu:**
1. Jdi na [python.org/downloads](https://www.python.org/downloads/)
2. Stáhni "Download Python 3.x.x" (velké žluté tlačítko)
3. Spusť instalátor
4. **DŮLEŽITÉ:** ✅ Zaškrtni **"Add Python to PATH"** (dole v instalátoru!)
5. Klikni "Install Now"
6. Po instalaci **zavři a znovu otevři Command Prompt**
7. Zkus znovu `python --version`

### Krok 2: Zkontroluj/Nainstaluj Git

V Command Prompt zadej:

```cmd
git --version
```

Pokud vidíš verzi Gitu, máš ho. Pokud vidíš chybu `'git' is not recognized`, pokračuj instalací.

**Instalace Gitu:**
1. Jdi na [git-scm.com/download/win](https://git-scm.com/download/win)
2. Stáhne se automaticky instalátor
3. Spusť instalátor a klikej "Next" (výchozí nastavení jsou OK)
4. Po instalaci **zavři a znovu otevři Command Prompt**
5. Zkus znovu `git --version`

### Krok 3: Stáhni projekt z GitHubu

V Command Prompt zadej následující příkazy (jeden po druhém):

```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/vojtechbit/srealitycrapermakler.git
cd srealitycrapermakler
```

**Co se stalo:**
- `cd %USERPROFILE%\Desktop` = přešel jsi na Plochu (Desktop)
- `git clone ...` = stáhl jsi projekt z GitHubu
- `cd srealitycrapermakler` = přešel jsi do složky projektu

Nyní jsi ve složce projektu. Ověř si to příkazem:

```cmd
cd
```

Měl bys vidět něco jako: `C:\Users\tvojejmeno\Desktop\srealitycrapermakler`

### Krok 4: Nainstaluj potřebné knihovny

V Command Prompt (stále ve složce projektu) zadej:

```cmd
pip install -r requirements.txt
```

Pokud `pip` hlásí chybu nebo příkaz neexistuje, použij vždy funkční variantu:

```cmd
py -m pip install -r requirements.txt
```

Tímto příkazem se použije přesně ta verze `pip`, která je součástí nainstalovaného Pythonu, takže funguje i když se Python nepřidal do PATH.

Počkej, až se nainstalují tři knihovny: `requests`, `pandas`, `openpyxl`.

**Uvidíš nějaké warningy? To je normální! ✅**

Pokud uvidíš něco jako:
```
WARNING: The script ... is installed in '...' which is not on PATH.
WARNING: You are using pip version 21.2.4; however, version 25.3 is available.
```

**Nemusíš nic řešit!** Tyto warningy nejsou kritické. Důležité je, že na konci vidíš:
```
Successfully installed certifi-... requests-... pandas-... openpyxl-...
```

Pokud vidíš `Successfully installed`, vše je OK a můžeš pokračovat.

### Krok 4.5: Ověř instalaci (volitelné, ale doporučené)

Pro jistotu ověř, že je vše správně nainstalované:

```cmd
python test_instalace.py
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

```cmd
python scrape_agents.py --prompt
```

Program se nejprve zeptá, z jakých platforem chceš stahovat data, a následně na parametry Sreality.cz (viz [Použití scraperu](#-použití-scraperu) níže).

**Poznámka pro Windows:**
- Na Windows používej `python` (ne `python3`)
- Na Windows používej `pip` (ne `pip3`)
- Cesty používají zpětné lomítko `\` místo `/`
- Excel se uloží do: `C:\Users\tvojejmeno\Desktop\srealitycrapermakler\data\`

---

## 🎯 Dva způsoby scrapování

Tento nástroj nabízí **dva hlavní způsoby** získání kontaktů na makléře ze Sreality.cz:

### 1️⃣ **Scraping podle kategorií** (`scrape_agents.py`)
- Projde inzeráty podle kategorie (byty, domy, atd.)
- Získá makléře z těchto inzerátů
- **Výhoda**: Můžeš filtrovat podle typu nemovitosti, kraje, atd.
- **Nevýhoda**: Nemusíš získat všechny inzeráty od jednoho makléře

### 2️⃣ **Scraping profilů makléřů** (`scrape_agent_profiles.py`) 🆕
- Projde konkrétní profily makléřů
- Získá **všechny inzeráty** od daného makléře
- **Výhoda**: Kompletní přehled inzerátů jednoho makléře, včetně počtu
- **Nevýhoda**: Musíš znát URL nebo ID makléře předem

---

## 🔍 Jak najít profily makléřů

Pro použití scraperu profilů potřebuješ URL nebo ID makléře:

1. Jdi na [Sreality.cz](https://www.sreality.cz)
2. Najdi libovolný inzerát od makléře
3. Klikni na **jméno makléře** v inzerátu
4. Zkopíruj URL z prohlížeče (např. `https://www.sreality.cz/makler/123456`)
5. Můžeš použít celou URL nebo jen číslo (např. `123456`)

---

## 🚀 Použití scraperu profilů makléřů

### Rychlý start

**macOS:**
```bash
python3 scrape_agent_profiles.py -u "https://www.sreality.cz/makler/123456"
```

**Windows:**
```cmd
python scrape_agent_profiles.py -u "https://www.sreality.cz/makler/123456"
```

### Příklady použití

**1. Jeden makléř podle URL:**
```bash
python3 scrape_agent_profiles.py -u "https://www.sreality.cz/makler/123456"
```

**2. Více makléřů najednou:**
```bash
python3 scrape_agent_profiles.py -u "https://www.sreality.cz/makler/123456" "https://www.sreality.cz/makler/789012"
```

**3. Použití jen user_id (čísla):**
```bash
python3 scrape_agent_profiles.py -u 123456 789012
```

**4. Načtení seznamu makléřů ze souboru:**
```bash
python3 scrape_agent_profiles.py -f makleri.txt
```

Formát souboru `makleri.txt` (jeden makléř na řádek):
```
https://www.sreality.cz/makler/123456
https://www.sreality.cz/makler/789012
345678
# Toto je komentář
```

**5. Vlastní název výstupního souboru:**
```bash
python3 scrape_agent_profiles.py -u 123456 -o muj_export.xlsx
```

**6. Rychlejší scraping bez detailů:**
```bash
python3 scrape_agent_profiles.py -u 123456 --no-details
```

### Co získáš

Výstupní Excel obsahuje:

| Sloupec | Popis |
|---------|-------|
| `zdroj` | Název platformy (Sreality.cz) |
| `jmeno_maklere` | Jméno makléře |
| `telefon` | Telefon (pokud je dostupný) |
| `email` | Email (pokud je dostupný) |
| `realitni_kancelar` | Název realitní kanceláře |
| `kraj` | Kraj (z nejčastější lokality) |
| `mesto` | Město (z nejčastější lokality) |
| `specializace` | Typy nemovitostí, které makléř nabízí |
| `detailni_informace` | Názvy prvních 10 inzerátů |
| `odkazy` | URL všech inzerátů makléře (oddělené čárkou) |
| `profil_url` | URL profilu makléře |
| `pocet_inzeratu` | **Celkový počet aktivních inzerátů makléře** 🎯 |

### Časové odhady

| Režim | Čas na makléře s 10 inzeráty | Čas na makléře se 100 inzeráty |
|-------|------------------------------|--------------------------------|
| **Bez detailů** (`--no-details`) | ~5-10 sekund | ~30-60 sekund |
| **S detaily** (výchozí) | ~30-60 sekund | ~5-10 minut |

**Doporučení:**
- Pro rychlý přehled: `--no-details`
- Pro přesné kontakty: bez přepínače (s detaily)

---

## 🚀 Použití scraperu podle kategorií

### Rychlý start

- **macOS:** `python3 scrape_agents.py --prompt`
- **Windows:** `python scrape_agents.py --prompt`

Skript se nejprve zeptá na výběr platforem (zadej např. `sreality` nebo více hodnot oddělených čárkou), poté na parametry specifické pro Sreality.cz:

1. **Typ nemovitosti (1-5)** – Byty, Domy, Pozemky, Komerční, Ostatní.
2. **Typ inzerátu (1-3)** – Prodej, Pronájem, Dražby.
3. **Kraj (volitelné číslo)** – např. `10` pro Prahu. Prázdné = celá ČR.
4. **Maximální počet stránek** – každá stránka ≈ 60 inzerátů. Hodnota `0` nebo režim `--full-scan` znamená pokus o kompletní průchod.

Aktuálně je plně implementovaný scraper pro **Sreality.cz**. Ostatní platformy jsou zaregistrované jako moduly se stručným popisem omezení – ve výstupu se zobrazí varování, že je potřeba doplnit autentizaci nebo parser.

### Důležité přepínače CLI

| Přepínač | Význam |
|----------|--------|
| `--platform/-p slug` | Spustí jen vybrané platformy (např. `-p sreality -p bezrealitky`). |
| `--all-platforms` | Pokusí se spustit všechny registrované zdroje. |
| `--full-scan` | Pokud to platforma podporuje, projde všechny stránky bez limitu. |
| `--max-pages N` | Ručně omezí počet stránek (např. `--max-pages 5`). |
| `--category-main` / `--category-type` / `--locality` | Parametry předané scraperu Sreality.cz. |
| `--output cesta.xlsx` | Uloží sjednocenou tabulku do Excelu. |
| `--list` | Vypíše dostupné platformy a skončí. |

### Kompletní průchod přes všechny zdroje

```
python3 scrape_agents.py --all-platforms --full-scan --output data/full_scan.xlsx
```

Upozornění: většina platforem zatím vrací pouze varování, protože vyžadují přihlášení, tokeny nebo headless prohlížeč. Skript vše sepíše v přehledu, takže víš, co je potřeba doplnit.

### Limity platforem (souhrn)

| Platforma | Popis limitů |
|-----------|---------------|
| Sreality.cz | Doporučeno držet cca 60 detailů/min, reagovat na HTTP 429 náhodným čekáním. |
| Bezrealitky.cz | API chráněné tokeny a reCAPTCHA – nutné reverzní inženýrství. |
| Reality.iDNES.cz | Silná anti-bot ochrana (Akami/Arkose), doporučené prohlížečové řešení. |
| Reality.cz | Nekonzistentní HTML, nutný parser typu BeautifulSoup a pomalejší tempo. |
| Realtia.cz | Partner API s klíčem, limit cca 120 požadavků/hod. |
| UlovDomov.cz | Vue.js + CSRF tokeny, doporučeno max. 1 požadavek/s. |
| LinkedIn | Silné restrikce, pouze přes oficiální API/OAuth. |
| Registr OSVČ | Veřejné SOAP rozhraní, nutné dotazování podle jména/IČO. |

### Sloučení více exportů do jedné tabulky

#### Metoda 1: Sloučení z více běhů se stejnou strukturou

Pokud máš více XLSX souborů z různých běhů scraperu (např. různé kategorie nebo kraje) a chceš je sloučit s deduplikací inzerátů, použij `merge_xlsx.py`:

**Postup:**
1. Vytvoř složku `data_merge/` (nebo použij existující)
2. Nahraj do ní všechny XLSX soubory, které chceš sloučit
3. Spusť:
```bash
# Mac:
python3 merge_xlsx.py

# Windows:
python merge_xlsx.py
```

**Co dělá:**
- Najde všechny XLSX soubory ve složce `data_merge/`
- Sloučí makléře podle unikátního klíče (jméno + telefon + realitní kancelář)
- **Deduplikuje inzeráty podle URL** - protože jeden inzerát může být ve více skupinách/kategoriích
- Spočítá správný počet unikátních inzerátů pro každého makléře
- Vytvoří nový soubor `data/merged_agents_TIMESTAMP.xlsx`

**Proč je deduplikace důležitá?**
Některé inzeráty jsou uvedené ve více kategoriích současně (např. byt může být v kategorii "Byty" i "Investiční"). Pokud bys jen sečetl počty inzerátů z různých běhů, dostal bys chybný výsledek. Tento script zajistí, že se každý inzerát počítá jen jednou podle jeho URL.

#### Metoda 2: Sloučení z různých platforem

Pro deduplikaci kontaktů z různých platforem (Sreality, Bezrealitky, atd.) použij skript `merge_contacts.py`:

```bash
python3 merge_contacts.py data/makleri_sreality.xlsx data/dalsi_zdroj.xlsx -o data/slouceno.xlsx
```

Skript:

1. Načte libovolný počet `.xlsx` souborů.
2. Znormalizuje jména, telefony a e-maily (bez diakritiky, sjednocené formáty).
3. Sloučí záznamy se shodným jménem/telefonem/e-mailem do jednoho řádku.
4. Zachová unikátní odkazy a doplňkové informace.

### Struktura výstupního Excelu

Každý řádek má jednotnou strukturu napříč platformami:

| Sloupec | Popis |
|---------|-------|
| `zdroj` | Název platformy. |
| `jmeno_maklere` | Jméno makléře. |
| `telefon` | Telefon (pokud je dostupný). |
| `email` | Email (pokud je dostupný). |
| `realitni_kancelar` | Název realitní kanceláře. |
| `kraj` | Kraj z popisu inzerátu. |
| `mesto` | Město/lokalita. |
| `specializace` | Shrnutí typu nemovitostí (např. „Byty - Prodej“). |
| `detailni_informace` | Textový popis inzerátu/zdroje. |
| `odkazy` | Veřejné URL na inzeráty nebo profily. |

Sreality.cz navíc přidává metadata s časem exportu, počtem makléřů a použitou kategorií (viz konzole po skončení).

Excel se automaticky ukládá do složky `data/` (vytvoří se při prvním běhu) pod názvem `makleri_YYYYMMDD_HHMMSS.xlsx`, pokud použiješ původní Sreality skript nebo si zadáš `--output` v nové CLI utilitě.

### Když scraper narazí na ochrany

- Vyčkej několik minut a spusť ho znovu.
- Zvaž snížení `--max-pages` nebo vypni `--full-scan`.
- Nepoužívej VPN; případně zkus jinou IP adresu.
- Sleduj varování v konzoli – u neimplementovaných platforem se zobrazí jasná zpráva.

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
  # Mac:
  python3 -m pip install --upgrade pip

  # Windows:
  python -m pip install --upgrade pip
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
# Mac:
python3 test_instalace.py

# Windows:
python test_instalace.py
```

---

### Chyba: `❌ HTTP 403`

**Co to znamená:**
- Sreality.cz blokuje request (cloudflare ochrana)
- Stává se hlavně v cloud prostředích nebo při VPN

**Řešení:**
1. Zkus bez VPN
2. Zkus z jiné sítě (mobilní data)
3. Zvyš delay v kódu (otevři `scrapers/sreality.py` a uprav `_Config.min_delay` / `_Config.max_delay`)
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
# Mac:
python3 muj_script.py

# Windows:
python muj_script.py
```

---

## 🔍 Hotové příklady

Spusť připravené příklady:

```bash
# Mac:
python3 examples.py

# Windows:
python examples.py
```

Obsahuje:
1. Makléři prodávající byty v Praze
2. Makléři prodávající domy v celé ČR
3. Makléři prodávající komerční nemovitosti - Jihomoravský kraj

---

## 📂 Struktura projektu

```
srealitycrapermakler/
├── scrape_agents.py       # Nová CLI utilita pro všechny platformy
├── merge_contacts.py      # Sloučení více Excelů z různých platforem
├── merge_xlsx.py          # Sloučení více běhů se stejnou strukturou + deduplikace
├── scrapers/              # Moduly pro jednotlivé platformy
│   ├── base.py            # Společné abstrakce
│   ├── sreality.py        # Implementace Sreality.cz
│   ├── bezrealitky.py     # Základ pro Bezrealitky.cz (zatím upozornění)
│   └── ...                # Další zdroje / stubs
├── sreality_scraper.py    # Původní jednoplatf. skript (ponechán pro kompatibilitu)
├── examples.py            # Hotové příklady
├── test_instalace.py      # Test instalace knihoven
├── requirements.txt       # Závislosti
├── data/                  # Výstupní Excel soubory (vytvoří se automaticky)
├── data_merge/            # Složka pro XLSX soubory k sloučení (vytvoř ručně)
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
