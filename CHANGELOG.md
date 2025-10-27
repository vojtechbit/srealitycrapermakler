# Changelog

Všechny významné změny v projektu budou dokumentovány zde.

Formát je založený na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
projekt používá [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Plánované
- GUI rozhraní
- Paralelní scraping
- Export do SQLite
- Progress bar
- Docker kontejner

## [1.0.0] - 2025-01-27

### Přidáno
- ✨ Základní scraper pro Sreality.cz
- 📊 Export do Excel (.xlsx)
- 📄 Export do CSV
- 🔄 Rotace User-Agent
- ⏱️ Rate limiting (2-5s delay)
- 🔁 Retry logika s exponential backoff
- 🎯 Konfigurovatelné parametry (kraj, typ, stránky)
- 📱 Interaktivní CLI rozhraní
- 📝 Kompletní dokumentace
- 🧪 Test script pro závislosti
- 💡 Hotové příklady použití
- 🚀 Automatický Git setup
- 📦 Requirements soubor

### Dokumentace
- README.md - Hlavní dokumentace
- QUICKSTART.txt - Rychlý start
- GIT_SETUP.md - Git návod
- CONTRIBUTING.md - Návod pro přispěvatele
- LICENSE - MIT licence

### Funkce
- Podpora pro Byty, Domy, Pozemky, Komerční nemovitosti
- Filtrování podle kraje
- Volba Prodej/Pronájem/Dražby
- Automatické ukládání do `data/` složky
- Parsování základních údajů (cena, plocha, patro, atd.)
- Ochrana proti blokování (delays, headers)

---

## Formát verzí

### [X.Y.Z]

- **X (Major)** - Zásadní změny, breaking changes
- **Y (Minor)** - Nové funkce, zpětně kompatibilní
- **Z (Patch)** - Opravy chyb, drobné změny

### Typy změn

- `Added` - Nové funkce
- `Changed` - Změny v existující funkcionalitě
- `Deprecated` - Zastaralé funkce (budou odstraněny)
- `Removed` - Odstraněné funkce
- `Fixed` - Opravy chyb
- `Security` - Bezpečnostní vylepšení

---

## Budoucí verze

### v1.1.0 (Q1 2025)
- [ ] Více detailů o nemovitostech
- [ ] Stahování obrázků
- [ ] Filtrování podle ceny a plochy
- [ ] Databázový export (SQLite)

### v1.2.0 (Q2 2025)
- [ ] GUI aplikace
- [ ] Automatické aktualizace dat
- [ ] Email notifikace

### v2.0.0 (2025)
- [ ] API server
- [ ] Web dashboard
- [ ] Multiprocessing scraping
- [ ] Cloud deployment

---

Pro aktuální stav vývoje viz [GitHub Issues](https://github.com/vojtechbit/srealitymaklerscraper/issues).
