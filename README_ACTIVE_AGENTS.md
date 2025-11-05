# 🎯 Scraper Aktivních Makléřů s Kompletními Profily

**Nejefektivnější způsob, jak získat kontakty na aktivní makléře ze Sreality.cz**

---

## 📋 Co tento scraper dělá?

Získává **pouze aktivní makléře** (s aktuálními inzeráty) a pro každého vytáhne **kompletní profil**:

✅ Jméno, telefon, email
✅ Realitní kancelář
✅ **Celkový počet aktivních inzerátů**
✅ **Rozložení podle typu** (Byty/Prodej: 20, Domy/Pronájem: 5, atd.)
✅ **Klikací odkaz na profil** makléře

**ŽÁDNÉ** seznamy jednotlivých inzerátů - jen agregovaná statistika!

---

## 🚀 RYCHLÝ START

### ⭐ INTERAKTIVNÍ MÓD (doporučeno):

```bash
# macOS:
python3 scrape_active_agents.py --prompt

# Windows:
python scrape_active_agents.py --prompt
```

**Program se tě zeptá:**
1. Typ nemovitosti (můžeš vybrat víc: `1,2` = Byty a Domy)
2. Typ inzerátu (můžeš vybrat víc: `1,2` = Prodej a Pronájem)
3. Kraje (můžeš vybrat víc: `10,20` = Praha a Brno)
4. Maximální počet stránek (`5` = výchozí, `0` = všechny)
5. Stahovat detaily? (`y` = ano, `n` = ne)

**Výhody:**
- ✅ Nemusíš pamatovat parametry
- ✅ Můžeš vybrat **více kategorií najednou**
- ✅ Vidíš souhrn před spuštěním
- ✅ Automaticky sloučí výsledky z všech kombinací

---

### Bez interaktivního módu (rychlé):

```bash
# Základní použití - byty na prodej, 5 stránek
python3 scrape_active_agents.py

# Nebo s parametry:
python3 scrape_active_agents.py --category-main 2 --locality 10
```

**Trvání:** cca 2-5 minut

---

## 📊 Co dostaneš v Excelu?

| Sloupec | Popis | Příklad |
|---------|-------|---------|
| `jmeno_maklere` | Jméno makléře | Jan Novák |
| `telefon` | Telefon | +420 123 456 789 |
| `email` | Email | jan.novak@remax.cz |
| `realitni_kancelar` | Realitní kancelář | RE/MAX Premium |
| `kraj` | Kraj | Praha |
| `mesto` | Město | Praha 2 |
| `profil_url` | **Klikací odkaz** na profil | [Profil makléře](link) 🔵 |
| `pocet_inzeratu` | **Celkem inzerátů** | 45 |
| `rozlozeni_inzeratu` | **Typy inzerátů** | Byty/Prodej: 30, Domy/Prodej: 10, Byty/Pronájem: 5 |

**Seřazeno podle počtu inzerátů (nejvíc → nejméně)**

---

## 💡 Příklady použití

### 1. Rychlý test (2-3 stránky, byty Praha):
```bash
python3 scrape_active_agents.py --max-pages 3 --locality 10
```
**Trvání:** ~1-2 minuty

### 2. Domy v celé ČR (10 stránek):
```bash
python3 scrape_active_agents.py --category-main 2 --max-pages 10
```
**Trvání:** ~5-10 minut

### 3. Komerční nemovitosti v Jihomoravském kraji:
```bash
python3 scrape_active_agents.py --category-main 4 --locality 20
```

### 4. VŠICHNI aktivní makléři s byty (může trvat hodiny!):
```bash
python3 scrape_active_agents.py --full-scan
```
**⚠️ Varování:** Toto může trvat 1-3 hodiny! Spusť přes noc.

### 5. Rychlý režim bez detailů (rychlejší, ale méně přesné kontakty):
```bash
python3 scrape_active_agents.py --no-details --max-pages 20
```
**Trvání:** ~5 minut místo 20 minut

### 6. Vlastní výstupní soubor:
```bash
python3 scrape_active_agents.py -o moji_makleri.xlsx
```

---

## 🔧 Všechny parametry

| Parametr | Popis | Výchozí |
|----------|-------|---------|
| `--category-main` | Typ nemovitosti: 1=Byty, 2=Domy, 3=Pozemky, 4=Komerční, 5=Ostatní | 1 (Byty) |
| `--category-type` | Typ inzerátu: 1=Prodej, 2=Pronájem, 3=Dražby | 1 (Prodej) |
| `--locality` | Kraj: 10=Praha, 11=Středočeský, ..., 23=Moravskoslezský | Celá ČR |
| `--max-pages` | Maximální počet stránek k procházení | 5 |
| `--full-scan` | Projít VŠECHNY stránky (ignoruje --max-pages) | Ne |
| `--no-details` | Nestahovat detaily (rychlejší, ale méně přesné kontakty) | Ne |
| `-o`, `--output` | Cesta k výstupnímu souboru | `data/active_agents_TIMESTAMP.xlsx` |

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

---

## ⏱️ Odhady času

| Scénář | Detaily | Čas |
|--------|---------|-----|
| 3 stránky, bez detailů | `--max-pages 3 --no-details` | **~30 sekund** |
| 5 stránek, s detaily | `--max-pages 5` | **~2-5 minut** |
| 10 stránek, s detaily | `--max-pages 10` | **~5-10 minut** |
| 20 stránek, s detaily | `--max-pages 20` | **~10-20 minut** |
| Full scan, s detaily | `--full-scan` | **~1-3 hodiny** ⚠️ |

**Proč s detaily trvá déle?**
- Bez detailů: stahuje jen základní seznamy inzerátů (~2-3 sekundy/stránka)
- S detaily: stahuje detail KAŽDÉHO inzerátu pro přesnější kontakty (~2-3 sekundy/inzerát)

---

## 🆚 Rozdíl oproti jiným skriptům

### `scrape_agents.py` (starý způsob):
❌ Projde byty → najde makléře
❌ Každý makléř má jen inzeráty bytů
❌ Nevidíš celkový počet inzerátů makléře
❌ Dlouhý seznam URL inzerátů

### `scrape_active_agents.py` (NOVÝ, lepší):
✅ Projde byty → najde aktivní makléře
✅ Pro každého získá **VŠECHNY jeho inzeráty** (byty, domy, pozemky...)
✅ Vidíš přesný celkový počet: **"45 inzerátů"**
✅ Agregovaná statistika: **"Byty/Prodej: 30, Domy/Prodej: 10"**
✅ Jen odkaz na profil, bez zbytečných seznamů

---

## 🔍 Jak to funguje (technicky)?

### Fáze 1: Najdi aktivní makléře (rychlé)
1. Projde inzeráty podle kategorie/kraje
2. Z každého inzerátu vytáhne `user_id` makléře
3. Vytvoří seznam unikátních aktivních makléřů

### Fáze 2: Získej kompletní profily (přesné)
1. Pro každého makléře zavolá API s `user_id`
2. Stáhne **VŠECHNY jeho aktivní inzeráty** (ne jen z jedné kategorie!)
3. Spočítá celkový počet
4. Agreguje podle typu (Byty/Prodej, Domy/Pronájem, atd.)
5. Vytvoří správnou URL profilu

---

## ❓ FAQ

### Proč nevidím telefonní čísla u některých makléřů?
Některé makléře nemají veřejné telefony v API. Zkus:
```bash
python3 scrape_active_agents.py  # S detaily (výchozí)
```
S detaily je větší šance získat kontakty.

### Můžu spustit pro více krajů najednou?
Bohužel ne přímo. Musíš spustit vícekrát:
```bash
python3 scrape_active_agents.py --locality 10 -o praha.xlsx
python3 scrape_active_agents.py --locality 20 -o brno.xlsx
```
Pak sloučit pomocí `merge_xlsx.py`.

### Kde se ukládá výstup?
Do složky `data/` která se vytvoří automaticky.
Název: `active_agents_YYYYMMDD_HHMMSS.xlsx`

### Můžu získat makléře z více kategorií?
Ano! Použij `scrape_agents.py` s parametrem `--prompt` a zadej více kategorií oddělených čárkou:
```bash
python3 scrape_agents.py --prompt
# Pak zadej: 1,2 (Byty a Domy)
```

---

## ⚠️ Řešení problémů

### Chyba: `❌ HTTP 403`
Sreality.cz blokuje requesty (Cloudflare ochrana).

**Řešení:**
1. Počkej 10-15 minut
2. Zkus bez VPN
3. Zvaž použít `--no-details` pro rychlejší běh

### Program se zasekl
**Řešení:**
1. Stiskni `Ctrl+C`
2. Počkej 10 sekund (dokončuje request)
3. Spusť znovu

### Málo kontaktů (telefonů/emailů)
**Řešení:**
Ujisti se, že nepoužíváš `--no-details`:
```bash
python3 scrape_active_agents.py  # BEZ --no-details
```

---

## 💪 Doporučené workflow

### Pro rychlý přehled (5 minut):
```bash
python3 scrape_active_agents.py --max-pages 10
```

### Pro kompletní databázi (1-2 hodiny):
```bash
# Spusť večer před spaním
python3 scrape_active_agents.py --full-scan

# Nebo odděleně pro každou kategorii:
python3 scrape_active_agents.py --category-main 1 --full-scan -o byty.xlsx
python3 scrape_active_agents.py --category-main 2 --full-scan -o domy.xlsx
python3 scrape_active_agents.py --category-main 3 --full-scan -o pozemky.xlsx

# Pak sloučit:
python3 merge_xlsx.py
```

---

## 📧 Podpora

Máš problém?
1. Zkontroluj sekci **Řešení problémů** výše
2. Ujisti se, že máš nejnovější verzi: `git pull`
3. Zkus přeinstalovat dependencies: `pip3 install -r requirements.txt --upgrade`

---

**Úspěšné scrapování! 🚀**
