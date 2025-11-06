# 🚀 Super Rychlý Scraper Makléřů (Company API)

## Co je nového?

`scrape_agents_fast.py` je **NEJRYCHLEJŠÍ** scraper, který využívá Company API endpoint pro získání seznamu makléřů.

### Klíčový rozdíl oproti `scrape_agents_simple.py`:

**Simple scraper:**
- Agreguje podle `user_id` (profilu makléře)
- Musí stahovat detaily inzerátů pro získání kontaktů
- ⚠️  **Problém:** Základní listing často NEMÁ seller/broker v `_embedded`!

**Fast scraper (NOVÝ):**
- Agreguje podle `company_id` (realitní kanceláře)
- Stahuje seznam makléřů přímo z Company API
- ✅ **Výhoda:** Jeden API call = všichni makléři RK s kontakty!

## Jak to funguje?

```
FÁZE 1: Agregace podle company_id
1. Projdi inzeráty podle kategorie
2. Z každého inzerátu extrahuj company_id
3. Agreguj statistiky (počet inzerátů, lokality, rozložení)

FÁZE 2: Stáhni makléře z Company API
4. Pro každou unikátní RK zavolej:
   GET /api/cs/v2/companies/{company_id}
5. Vrátí seznam VŠECH makléřů RK s kontakty (email, telefon)
6. Podporuje paginaci (max 20 makléřů/stránka)

Výsledek:
- 5 stránek inzerátů = 5 API volání (FÁZE 1)
- 15 RK = 15 API volání (FÁZE 2)
- CELKEM: 20 API volání = 30-60 SEKUND! ⚡
- 100% kontakty! ✅
```

## 🎯 Cross-Combination Deduplication

### Problém který jsme řešili:

Když uživatel vybere více kombinací (např. **Byty/Prodej + Byty/Pronájem**), stejná RK se objeví v obou výsledcích.

**Původní přístup (NEEFEKTIVNÍ):**
```
Byty/Prodej:
  → RE/MAX (ID 123) ← Volá sellers API
  → Century21 (ID 456) ← Volá sellers API

Byty/Pronájem:
  → RE/MAX (ID 123) ← Volá sellers API ZNOVU! ❌
  → MAXIMA REALITY (ID 789) ← Volá sellers API
```

**Výsledek:** RE/MAX sellers API zavoláno 2× zbytečně!

### Řešení: `scrape_agents_fast_combined()`

```
FÁZE 1: Agreguj companies ze VŠECH kombinací
- Projdi Byty/Prodej → najdi RE/MAX (123), Century21 (456)
- Projdi Byty/Pronájem → najdi RE/MAX (123), MAXIMA (789)
- Sdílený dictionary → deduplikace automaticky!

FÁZE 2: Volej sellers API jen pro UNIKÁTNÍ RK
- RE/MAX (123) ← Volá JEN JEDNOU! ✅
- Century21 (456) ← Volá jednou
- MAXIMA (789) ← Volá jednou

Výsledek:
- 3 API volání místo 4
- Čím víc kombinací, tím větší úspora!
```

### Příklad úspory:

```
Scénář: 2 typy nemovitostí × 2 typy inzerátů × 3 kraje
= 12 kombinací

Průměrně 50% RK se opakuje mezi kombinacemi.

Původní přístup:
- 12 kombinací × 15 RK = 180 API volání

Optimalizovaný přístup:
- 12 kombinací (FÁZE 1)
- ~90 unikátních RK (FÁZE 2)
- CELKEM: 102 API volání

ÚSPORA: 43% API volání! 🎉
```

## 🎯 JAK TO SPUSTIT?

### ⭐ DOPORUČENO: Interaktivní mód s deduplikací

```bash
python3 scrape_agents_fast.py --prompt
```

**Co se stane:**
1. Vybereš typ nemovitosti (1, 2, 3... nebo více: `1,2`)
2. Vybereš typ inzerátu (1, 2, 3... nebo více: `1,2`)
3. Vybereš kraje (volitelné: `10,11,20`)
4. Zadáš počet stránek nebo `all`
5. **Scraper AUTOMATICKY deduplikuje RK napříč všemi kombinacemi!** ✅

**Příklad:**
```
Vyber typ nemovitosti (1-5) [1]: 1,2      ← Byty + Domy
Vyber typ inzerátu (1-3) [1]: 1,2         ← Prodej + Pronájem
Vyber kraje (10-23) nebo Enter: 10        ← Praha
Max stránek (nebo 'all') [5]: 5

🎯 Celkem 4 kombinací k zpracování:
   1. Byty / Prodej / Praha
   2. Byty / Pronájem / Praha
   3. Domy / Prodej / Praha
   4. Domy / Pronájem / Praha

🔍 FÁZE 1: Agregace companies ze všech kombinací...
   Kombinace 1/4: Byty / Prodej
      Stránka 1: 60 inzerátů (Nové RK: 15, Existující: 0)
      ...
   Kombinace 2/4: Byty / Pronájem
      Stránka 1: 60 inzerátů (Nové RK: 5, Existující: 10) ← 10 RK už známe!
      ...

✅ Nalezeno 30 UNIKÁTNÍCH realitních kanceláří

🔍 FÁZE 2: Stahuji seznam makléřů (jen pro unikátní RK)...
   1/30: RE/MAX Reality - 12 makléřů
   2/30: Century 21 - 8 makléřů
   ...
```

### Základní použití (bez interakce)

```bash
# Jedna kategorie (klasický mód)
python3 scrape_agents_fast.py --category-main 1 --category-type 1 --max-pages 5

# Domy na pronájem v Praze
python3 scrape_agents_fast.py \
  --category-main 2 \
  --category-type 2 \
  --locality 10 \
  --max-pages 10

# Vlastní výstup
python3 scrape_agents_fast.py \
  --prompt \
  -o export_makleri.xlsx
```

### Parametry

```
--prompt               Interaktivní mód (DOPORUČENO)
--category-main        Typ nemovitosti:
                       1 = Byty
                       2 = Domy
                       3 = Pozemky
                       4 = Komerční
                       5 = Ostatní

--category-type        Typ inzerátu:
                       1 = Prodej
                       2 = Pronájem
                       3 = Dražby

--locality             Kraj (volitelné):
                       10 = Praha
                       11 = Středočeský
                       12 = Jihočeský
                       ... atd.

--max-pages            Kolik stránek (výchozí: 5)
--full-scan            Projde VŠECHNY stránky
-o, --output           Výstupní soubor .xlsx
```

## Výstup

Excel soubor s **hierarchickou strukturou**:

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 RE/MAX Reality    │ Praha │ 45 inzerátů │ Byty/Prodej: 30 │
├─────────────────────────────────────────────────────────────┤
│   → Jan Novák        │ +420777888999 │ jan@remax.cz │ Profil │
│   → Petra Svobodová  │ +420606123456 │ petra@remax.cz │ Profil │
│   → Milan Dvořák     │ +420733222111 │ milan@remax.cz │ Profil │
├─────────────────────────────────────────────────────────────┤
│ 📊 Century 21 Praha  │ Praha │ 28 inzerátů │ Byty/Prodej: 20 │
├─────────────────────────────────────────────────────────────┤
│   → Eva Nováková     │ +420777222333 │ eva@c21.cz │ Profil │
│   → Tomáš Černý      │ +420606444555 │ tomas@c21.cz │ Profil │
└─────────────────────────────────────────────────────────────┘
```

**Formátování:**
- 📋 Company řádky: **modrý background**, **tučné písmo**
- 👤 Makléř řádky: odsazené "→", klikací hyperlink na profil

**URL formát:**
```
https://www.sreality.cz/adresar/{company-slug}/{company_id}/makleri/{seller_id}

Příklad:
https://www.sreality.cz/adresar/re-max-reality/12345/makleri/67890
```

## Porovnání všech scraperů

| Scraper | Rychlost | Přístup | Deduplikace | Použití |
|---------|----------|---------|-------------|---------|
| `scrape_agents_fast.py` | ⚡⚡⚡ SUPER rychlý | Company API | ✅ Across combinations | **👉 PREFERUJ!** |
| `scrape_agents_simple.py` | ⚡⚡ Velmi rychlý | User aggregation | ⚠️  Within page only | Alternativa |
| `scrape_active_agents.py` | 🐌 Velmi pomalý | Full profile scraping | N/A | ❌ DEPRECATED |

## Výhody `scrape_agents_fast.py`

### ✅ Rychlost
- 30-60 sekund pro 5 stránek (vs. 10+ minut u starého scraperu)
- Minimální počet API volání
- Nízké riziko Cloudflare bloku

### ✅ Přesnost
- 100% kontakty (telefon + email) z Company API
- Kompletní seznam makléřů pro každou RK
- Podpora paginace (RK s 50+ makléři)

### ✅ Efektivita
- **Cross-combination deduplication** - žádné duplicitní API volání
- Automatické slučování výsledků
- Inteligentní agregace statistik

### ✅ Použitelnost
- Interaktivní mód s multiple selection
- Hierarchický Excel output
- Klikací profily makléřů

## Technické detaily

### Company API Response

```json
{
  "_embedded": {
    "sellers": {
      "result_size": 8,
      "per_page": 20,
      "page": 1,
      "sellers": [
        {
          "id": 72849,
          "name": "Ing. Lucie Mikulíková",
          "email": "mikulikova@company.cz",
          "phones": [
            {
              "code": "420",
              "type": "TEL",
              "number": "603744244"
            }
          ]
        }
      ]
    }
  }
}
```

### Paginace

Pokud RK má více než 20 makléřů:
```python
while True:
    params = {"page": page}
    data = get(f"/companies/{id}", params)
    sellers = data["_embedded"]["sellers"]["sellers"]

    all_sellers.extend(sellers)

    # Check if more pages
    if (page * per_page) >= result_size:
        break

    page += 1
```

### Agregace napříč kombinacemi

```python
# Sdílený dictionary pro VŠECHNY kombinace
all_companies = defaultdict(lambda: {...})

# FÁZE 1: Projdi všechny kombinace
for (category_main, category_type, locality) in combinations:
    estates = api.get(f"/estates?category={category_main}&type={category_type}")

    for estate in estates:
        company_id = estate["_embedded"]["company"]["id"]

        # Agreguj do SDÍLENÉHO dictionary
        comp = all_companies[company_id]
        comp["total_estates"] += 1
        comp["category_breakdown"][(category_main, category_type)] += 1

# FÁZE 2: Volej sellers API jen pro UNIKÁTNÍ company_id
for company_id in all_companies.keys():
    sellers = api.get(f"/companies/{company_id}")
    # ... zpracuj makléře
```

## Řešení problémů

### Cloudflare blokace (HTTP 403)

**Řešení:**
1. Počkej 5-10 minut a zkus znovu
2. Změň IP (restart routeru/VPN)
3. Zpomal delay v `scrapers/sreality.py`:
   ```python
   min_delay: float = 3.0  # původně 1.0
   max_delay: float = 6.0  # původně 3.0
   ```

### Žádní makléři u některých RK

**Možné důvody:**
- RK nemá žádné makléře v databázi
- Company API vrátilo prázdný seznam
- Chyba při stahování

**Scraper to hlásí:**
```
⚠️  Company XYZ: žádní makléři
```

### Velké RK s 50+ makléři

**Automaticky řešeno paginací:**
```
✓ RE/MAX Reality - 87 makléřů (5 stránek)
```

Scraper automaticky projde všechny stránky sellers API.

## Závěr

`scrape_agents_fast.py` je **nejlepší volba** pro rychlé získání aktivních makléřů organizovaných podle RK!

**Klíčové výhody:**
- ✅ Super rychlý (30-60 sekund)
- ✅ 100% kontakty (Company API)
- ✅ Cross-combination deduplication (úspora 30-50% API volání)
- ✅ Hierarchický Excel (RK → Makléři)
- ✅ Klikací profily makléřů
- ✅ Podpora paginace (velké RK)

**Start prompt:**
```bash
python3 scrape_agents_fast.py --prompt
```

A máš všechny aktivní RK s jejich makléři za pár desítek sekund! 🚀
