# 🚀 Jednoduchý a Rychlý Scraper Makléřů

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

## Nová logika (RYCHLÁ)

```
scrape_agents_simple.py:
1. Stáhni seznam inzerátů podle kategorie (RYCHLÉ)
2. Z KAŽDÉHO inzerátu PŘÍMO vytáhni:
   - Jméno makléře
   - Telefon, email (z _embedded.phones, _embedded.emails)
   - Company (z _embedded.seller nebo _embedded.company)
   - Typ inzerátu (z seo.category_*)
3. Agreguj data pro každého makléře
4. HOTOVO - žádné další API volání! ✅

Výsledek: 1 stránka za pár SEKUND! 🚀
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

## Použití

### Základní použití

```bash
# Jedna stránka bytů na prodej
python3 scrape_agents_simple.py

# 5 stránek
python3 scrape_agents_simple.py --max-pages 5

# Všechny stránky (full scan)
python3 scrape_agents_simple.py --full-scan
```

### Pokročilé použití

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

| Vlastnost | Původní | Nový |
|-----------|---------|------|
| Rychlost | ❌ 10+ min/stránka | ✅ Pár sekund/stránka |
| API volání | ❌ Stovky | ✅ Desítky |
| Přesnost | ✅ Velmi přesné | ⚠️  Dobrá (z inzerátů) |
| Cloudflare blok | ❌ Vysoké riziko | ✅ Nízké riziko |

## Omezení

Protože data získáváme přímo z výpisu inzerátů (ne z detailů):

- ⚠️  **Telefon a email** může u některých makléřů chybět (pokud nejsou v základním výpisu)
- ⚠️  **Počet inzerátů** je omezen na kategorie, které scrapuješ (ne celkový počet)

**Ale:** Pro většinu účelů to stačí a je to **100× rychlejší**! 🚀

## Kombinování kategorií

Pokud chceš makléře z více kategorií, spusť scraper vícekrát:

```bash
# Byty prodej
python3 scrape_agents_simple.py \
  --category-main 1 --category-type 1 \
  --max-pages 5 -o byty_prodej.xlsx

# Domy prodej
python3 scrape_agents_simple.py \
  --category-main 2 --category-type 1 \
  --max-pages 5 -o domy_prodej.xlsx

# Pak můžeš sloučit v Excelu
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

Některé inzeráty nemají kontakty v základním výpisu. To je normální.

**Řešení:**
- Použij `scrape_active_agents.py` pro detailnější data (ale bude to pomalé)
- Nebo doplň kontakty ručně pro důležité makléře

## Porovnání všech scraperů

| Scraper | Rychlost | Přesnost | Použití |
|---------|----------|----------|---------|
| `scrape_agents_simple.py` | ⚡ Velmi rychlý | 🟡 Dobrá | **Preferuj tohle!** |
| `scrape_active_agents.py` | 🐌 Velmi pomalý | ✅ Výborná | Když potřebuješ 100% přesnost |
| `scrape_agent_profiles.py` | 🐌 Pomalý | ✅ Výborná | Když znáš konkrétní profily |

## Závěr

`scrape_agents_simple.py` je **ideální volba** pro rychlé získání aktivních makléřů s jejich kontakty a statistikami.

**Není dokonalý**, ale je **praktický** a **rychlý** - což je pro většinu případů důležitější než 100% přesnost! 🎯
