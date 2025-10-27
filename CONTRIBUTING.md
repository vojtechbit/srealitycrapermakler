# Přispívání do Sreality Makler Scraper

Děkujeme, že máš zájem přispět! 🎉

## 🚀 Jak můžeš pomoct

### 1. Nahlášení chyb (Issues)

Našel jsi chybu? [Vytvoř issue](https://github.com/vojtechbit/srealitymaklerscraper/issues/new) a uveď:

- **Popis problému** - Co se stalo?
- **Kroky k reprodukci** - Jak problém zopakovat?
- **Očekávané chování** - Co by mělo fungovat?
- **Prostředí**:
  - OS (Windows/Mac/Linux)
  - Python verze
  - Verze knihoven (z `pip freeze`)
- **Logy/Screenshot** - Pokud je to možné

### 2. Návrhy na vylepšení

Máš nápad na novou funkci? [Vytvoř issue](https://github.com/vojtechbit/srealitymaklerscraper/issues/new) s tagem "enhancement" a popiš:

- **Co by mělo dělat** - Funkce/vylepšení
- **Proč je to užitečné** - Use case
- **Jak by to mělo fungovat** - Návrh implementace

### 3. Pull Requesty

Chceš přidat kód? Skvělé! Postupuj takto:

#### Krok 1: Fork a Clone

```bash
# Fork repozitář na GitHubu, pak:
git clone https://github.com/tvuj-username/srealitymaklerscraper.git
cd srealitymaklerscraper
```

#### Krok 2: Vytvoř branch

```bash
git checkout -b feature/nova-funkce
```

Pojmenování branches:
- `feature/nazev` - Nová funkce
- `fix/nazev` - Oprava chyby
- `docs/nazev` - Dokumentace
- `refactor/nazev` - Refaktoring

#### Krok 3: Proveď změny

- Dodržuj existující styl kódu
- Přidej komentáře k složitému kódu
- Aktualizuj dokumentaci pokud je potřeba

#### Krok 4: Testuj

```bash
python test_setup.py  # Základní test
python sreality_scraper.py  # Funkční test
```

#### Krok 5: Commit

```bash
git add .
git commit -m "feat: Přidána nová funkce XYZ"
```

Formát commit zpráv:
- `feat:` - Nová funkce
- `fix:` - Oprava chyby
- `docs:` - Dokumentace
- `style:` - Formátování
- `refactor:` - Refaktoring
- `test:` - Testy
- `chore:` - Údržba

#### Krok 6: Push a PR

```bash
git push origin feature/nova-funkce
```

Pak vytvoř Pull Request na GitHubu s popisem změn.

## 📝 Code Style

### Python

Dodržuj PEP 8:
- 4 mezery pro odsazení (ne taby)
- Max 100 znaků na řádek
- Docstrings pro funkce a třídy
- Type hints kde je to vhodné

```python
def scrape_listings(
    self, 
    category_main: int = 1,
    category_type: int = 1,
    locality_region_id: Optional[int] = None
) -> List[Dict]:
    """
    Stáhne nabídky z Sreality
    
    Args:
        category_main: Typ nemovitosti
        category_type: Typ inzerátu
        locality_region_id: ID kraje (volitelné)
    
    Returns:
        List slovníků s daty nabídek
    """
    pass
```

### Komentáře

- Česky nebo anglicky - jak se ti líbí
- Vysvětli "proč", ne "co"
- Dokumentuj komplikovanou logiku

## 🔍 Co hledáme

Rádi uvítáme příspěvky v těchto oblastech:

### Vylepšení
- [ ] Lepší error handling
- [ ] Více parametrů pro filtrování
- [ ] Export do dalších formátů (JSON, SQLite)
- [ ] GUI rozhraní
- [ ] Paralelní scraping
- [ ] Progress bar pro dlouhé operace

### Dokumentace
- [ ] Více příkladů použití
- [ ] Video návody
- [ ] Překlad do angličtiny
- [ ] FAQ sekce

### Testy
- [ ] Unit testy
- [ ] Integration testy
- [ ] CI/CD pipeline

### Infrastruktura
- [ ] Docker kontejner
- [ ] API wrapper
- [ ] Web dashboard

## ⚖️ Pravidla

1. **Respektuj etiku** - Scraper musí být odpovědný
2. **Testuj změny** - Před odesláním PR
3. **Dokumentuj** - Aktualizuj README pokud je potřeba
4. **Komunikuj** - Diskutuj velké změny v issues
5. **Buď slušný** - Respektuj ostatní přispěvatele

## 🎯 Priority

**High priority:**
- Opravy kritických chyb
- Bezpečnostní vylepšení
- Zlepšení stability

**Medium priority:**
- Nové funkce
- Vylepšení UX
- Dokumentace

**Low priority:**
- Refaktoring
- Optimalizace
- Nice-to-have funkce

## 📞 Kontakt

Máš otázky? 
- 💬 Diskuze v [Issues](https://github.com/vojtechbit/srealitymaklerscraper/issues)
- 📧 Nebo přímo v Pull Requestu

## 🙏 Poděkování

Všem přispěvatelům patří velký dík! ❤️

Každý příspěvek, ať už velký nebo malý, je oceněn.

---

**Happy coding!** 🚀
