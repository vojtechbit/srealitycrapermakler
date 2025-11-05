# 🚀 Rychlý Scraper Makléřů (Optimalizovaný)

## Proč nový scraper?

Původní `scrape_active_agents.py` byl **příliš pomalý** (10+ minut na stránku), protože:

```
Původní logika (POMALÁ):
1. Stáhni seznam 60 inzerátů (RYCHLÉ)
2. Pro KAŽDÉHO makléře:
   - Stáhni VŠECHNY jeho inzeráty (API volání)
   - Stáhni detail KAŽDÉHO inzerátu (API volání)

Výsledek: 20 makléřů × 40 inzerátů × 2 sekundy = 26 MINUT! ❌
```

## Nová optimalizovaná logika (RYCHLÁ + PŘESNÁ)

```
scrape_agents_simple.py:
FÁZE 1: Agregace podle user_id (profilu makléře)
1. Stáhni seznam inzerátů podle kategorie
2. Z každého inzerátu extrahuj:
   - user_id makléře (každý má profil!)
   - Jméno, company, kraj, město
   - Telefon, email (pokud jsou v základním výpisu)
   - Typ inzerátu → agreguj podle user_id

FÁZE 2: Doplň chybějící kontakty (jen pro makléře bez kontaktů!)
3. Pro makléře BEZ telefonu/emailu:
   - Stáhni detail JEDNOHO jeho inzerátu
   - Získej kontakty z detailu

Výsledek:
- 5 stránek = cca 20 makléřů
- Fáze 1: 5 API volání
- Fáze 2: cca 5-10 API volání (jen pro makléře bez kontaktů)
- CELKEM: 10-15 volání = 20-45 SEKUND! ⚡
- 100% kontakty! ✅
```

## Co získáš

Přesně to, co potřebuješ:
- ✅ Jméno makléře
- ✅ Telefon
- ✅ Email
- ✅ Realitní kancelář
- ✅ Kraj a město
- ✅ Počet inzerátů
- ✅ Rozložení inzerátů (např. "Byty/Prodej: 30, Domy/Pronájem: 5")
- ✅ Link na profil makléře (`https://www.sreality.cz/makler/{user_id}`)

## 🎯 JAK TO SPUSTIT?

### ⭐ DOPORUČENO: Interaktivní mód

```bash
python3 scrape_agents_simple.py --prompt
```

**Co se stane:**
1. Vybereš typ nemovitosti (1, 2, 3... nebo více: `1,2`)
2. Vybereš typ inzerátu (1, 2, 3... nebo více: `1,2`)
3. Vybereš kraje (volitelné, můžeš více: `10,11,20`)
4. Zadáš počet stránek nebo `all`
5. Scraper automaticky projde všechny kombinace a sloučí výsledky!

**Příklad:**
```
Vyber typ nemovitosti (1-5) [1]: 1,2      ← Byty + Domy
Vyber typ inzerátu (1-3) [1]: 1          ← Prodej
Vyber kraje (10-23) nebo Enter: 10,20    ← Praha + Jihomoravský
Max stránek (nebo 'all') [5]: 10         ← 10 stránek
```

Výsledek: Scraper projde:
- Byty/Prodej/Praha
- Byty/Prodej/Jihomoravský
- Domy/Prodej/Praha
- Domy/Prodej/Jihomoravský

A sloučí všechny makléře bez duplicit! 🎉

### Základní použití (bez interakce)

```bash
# Jedna stránka bytů na prodej (výchozí)
python3 scrape_agents_simple.py

# 5 stránek
python3 scrape_agents_simple.py --max-pages 5

# Všechny stránky (full scan)
python3 scrape_agents_simple.py --full-scan
```

### Pokročilé použití (manuální parametry)

```bash
# Domy na pronájem v Praze
python3 scrape_agents_simple.py \
  --category-main 2 \
  --category-type 2 \
  --locality 10

# Vlastní výstup
python3 scrape_agents_simple.py \
  --max-pages 10 \
  -o muj_export.xlsx
```

### Parametry

```
--category-main    Typ nemovitosti:
                   1 = Byty (výchozí)
                   2 = Domy
                   3 = Pozemky
                   4 = Komerční
                   5 = Ostatní

--category-type    Typ inzerátu:
                   1 = Prodej (výchozí)
                   2 = Pronájem
                   3 = Dražby

--locality         Kraj (volitelné):
                   10 = Praha
                   11 = Středočeský
                   12 = Jihočeský
                   ... atd.

--max-pages        Kolik stránek (výchozí: 5)

--full-scan        Projde VŠECHNY stránky

-o, --output       Výstupní soubor .xlsx
```

## Výstup

Excel soubor s:
- 📋 Tabulka makléřů seřazená podle počtu inzerátů
- 🔗 Klikací hyperlinky na profily
- 📏 Automatická šířka sloupců
- 📊 Agregovaná statistika

Příklad řádku:
```
Jméno: Jan Novák
Telefon: +420 777 888 999
Email: jan.novak@reality.cz
RK: RE/MAX Reality
Kraj: Praha
Město: Praha 1
Profil: https://www.sreality.cz/makler/123456
Počet inzerátů: 45
Rozložení: Byty/Prodej: 30, Byty/Pronájem: 10, Domy/Prodej: 5
```

## Výhody oproti původnímu scraperu

| Vlastnost | Původní | Nový (Optimalizovaný) |
|-----------|---------|----------------------|
| Rychlost | ❌ 10+ min/stránka | ✅ 20-45 sekund/stránka |
| API volání | ❌ Stovky | ✅ 10-20 |
| Kontakty | ✅ 100% | ✅ 100% (doplňuje z detailů!) |
| Agregace podle profilu | ❌ Ne | ✅ Ano (user_id) |
| Slučování duplicit | ⚠️  Složité | ✅ Automatické |
| Interaktivní mód | ✅ Ano | ✅ Ano (--prompt) |
| Cloudflare blok | ❌ Vysoké riziko | ✅ Nízké riziko |

## Jak to funguje?

**Klíčový insight:** Každý makléř má `user_id` (profil na Sreality)!

1. **Agregace podle user_id** - ne podle jména/emailu
   - Jeden makléř může mít 30 inzerátů → všechny agregujeme k jednomu user_id
   - Eliminuje duplicity už v první fázi

2. **Inteligentní doplňování kontaktů**
   - Pokud inzerát má telefon/email v základním výpisu → použij ho
   - Pokud ne → stáhni detail JEDNOHO inzerátu makléře
   - Výsledek: 100% kontakty s minimem API volání

3. **Multiple selection v --prompt módu**
   - Vyber více typů nemovitostí: `1,2` (Byty + Domy)
   - Vyber více krajů: `10,20` (Praha + Jihomoravský)
   - Scraper projde všechny kombinace a sloučí výsledky

## Omezení (menší než u původního)

- ⚠️  **Počet inzerátů** je omezen na kategorie, které scrapuješ (ne celkový počet všech inzerátů makléře)
  - Ale pro většinu účelů stačí vědět "má 30 bytů na prodej" místo "celkem 150 inzerátů všech typů"

**Výhody převažují:** 20-30× rychlejší + 100% kontakty + lepší agregace! 🎯

## Kombinování kategorií

### ⭐ DOPORUČENO: Použij `--prompt` mód

```bash
python3 scrape_agents_simple.py --prompt
# Pak zadej: 1,2 pro Byty+Domy
# Automaticky sloučí!
```

### Alternativa: Manuální kombinování

Pokud nechceš interaktivní mód, můžeš spustit vícekrát:

```bash
# Byty prodej
python3 scrape_agents_simple.py \
  --category-main 1 --category-type 1 \
  --max-pages 5 -o byty_prodej.xlsx

# Domy prodej
python3 scrape_agents_simple.py \
  --category-main 2 --category-type 1 \
  --max-pages 5 -o domy_prodej.xlsx

# Pak sloučíš v Excelu
```

## Řešení problémů

### Cloudflare blokace (HTTP 403)

Pokud dostaneš chybu:
```
⚠️  Chyba při stahování stránky 1
```

**Řešení:**
1. **Počkej 5-10 minut** a zkus znovu (Cloudflare má časový limit)
2. **Změň IP** (restartuj router nebo použij VPN)
3. **Použij prohlížeč** - otevři https://www.sreality.cz v prohlížeči, počkej na Cloudflare check, pak zkus scraper
4. **Zpomal** - i když je tento scraper rychlý, přidej delší prodlevy v kódu:
   ```python
   # V scrapers/sreality.py, řádek 24:
   min_delay: float = 3.0  # původně 1.0
   max_delay: float = 6.0  # původně 3.0
   ```

### Žádné kontakty (telefon/email prázdné)

**To by se nemělo stávat!** Nový scraper automaticky doplňuje kontakty z detailů.

Pokud se přesto stane:
- Zkontroluj output - scraper hlásí "🔍 Doplňuji kontakty pro X makléřů..."
- Možná byl problém s API voláním (Cloudflare blok)
- Zkus spustit znovu

## Porovnání všech scraperů

| Scraper | Rychlost | Kontakty | Interaktivní | Použití |
|---------|----------|----------|--------------|---------|
| `scrape_agents_simple.py` | ⚡⚡⚡ Velmi rychlý | ✅ 100% | ✅ Ano | **👉 PREFERUJ TOHLE!** |
| `scrape_active_agents.py` | 🐌 Velmi pomalý | ✅ 100% | ✅ Ano | ❌ DEPRECATED (pomalý) |
| `scrape_agent_profiles.py` | 🐌 Pomalý | ✅ 100% | ❌ Ne | Jen pro konkrétní profily |

## Závěr

`scrape_agents_simple.py` je **nejlepší volba** pro rychlé získání aktivních makléřů!

**Výhody:**
- ✅ 20-30× rychlejší než původní scraper
- ✅ 100% kontakty (automatické doplňování z detailů)
- ✅ Agregace podle user_id (profilu)
- ✅ Interaktivní mód s multiple selection
- ✅ Automatické slučování duplicit

**Start prompt:**
```bash
python3 scrape_agents_simple.py --prompt
```

A máš všechny aktivní makléře za pár desítek sekund! 🚀
