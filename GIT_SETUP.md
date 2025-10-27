# 🚀 Git Setup - Nahrání na GitHub

## Rychlý start (automaticky)

### Krok 1: Otevři terminál ve složce sreality_scraper

```bash
cd /Users/vojtechbroucek/Desktop/sreality_scraper
```

### Krok 2: Spusť automatický script

```bash
chmod +x git_setup.sh
./git_setup.sh
```

Script automaticky:
- Inicializuje Git repozitář
- Přidá GitHub remote
- Commitne všechny soubory
- Nahraje na GitHub

---

## Manuální postup

### 1. Inicializace Git repozitáře

```bash
cd /Users/vojtechbroucek/Desktop/sreality_scraper
git init
```

### 2. Přidání GitHub remote

```bash
git remote add origin https://github.com/vojtechbit/srealitymaklerscraper.git
```

### 3. Přidání souborů

```bash
git add .
```

### 4. Commit

```bash
git commit -m "Initial commit - Sreality scraper"
```

### 5. Push na GitHub

První push:
```bash
git push -u origin main
```

Nebo pokud používáš master:
```bash
git push -u origin master
```

---

## Další použití (po první nahrání)

### Když něco změníš:

```bash
# 1. Zobraz změny
git status

# 2. Přidej změněné soubory
git add .

# 3. Commitni změny
git commit -m "Popis změn"

# 4. Nahraj na GitHub
git push
```

---

## Užitečné Git příkazy

### Zobrazit historii commitů
```bash
git log --oneline
```

### Zobrazit změny v souborech
```bash
git diff
```

### Zrušit změny v souboru
```bash
git checkout -- soubor.py
```

### Vytvoření nové větve
```bash
git checkout -b nova-vetev
```

### Přepnutí mezi větvemi
```bash
git checkout main
```

### Stažení změn z GitHubu
```bash
git pull
```

---

## Práce s Claude Code

Po nahrání na GitHub můžeš:

1. **Klonovat repozitář jinde:**
   ```bash
   git clone https://github.com/vojtechbit/srealitymaklerscraper.git
   ```

2. **Otevřít v Claude Code:**
   - Otevři Claude Code
   - File → Open Folder
   - Vyber složku s repozitářem

3. **Synchronizace změn:**
   - Změny v Claude Code → commit → push
   - Stáhni změny: `git pull`

---

## Struktura projektu na GitHubu

```
srealitymaklerscraper/
├── .gitignore              # Ignorované soubory (data/, cache)
├── README.md               # Hlavní dokumentace
├── QUICKSTART.txt          # Rychlý návod
├── GIT_SETUP.md           # Tento soubor
├── requirements.txt        # Python závislosti
├── sreality_scraper.py    # Hlavní scraper
├── examples.py            # Příklady použití
├── test_setup.py          # Test závislostí
├── start.sh               # Start script
├── git_setup.sh           # Git setup script
└── data/                  # Data (ignorováno v .gitignore)
```

---

## Tipy

### Ignorování dat v Git

`.gitignore` už obsahuje:
- `data/` - Excel soubory se neukládají do Git
- `*.xlsx` - Excel soubory
- `*.csv` - CSV soubory
- `__pycache__/` - Python cache

### Před prvním pushem

Ujisti se, že máš repozitář vytvořený na GitHubu:
- https://github.com/vojtechbit/srealitymaklerscraper

### Pokud repozitář už má nějaký obsah

```bash
# Stáhni obsah z GitHubu
git pull origin main --allow-unrelated-histories

# Pak pushni
git push -u origin main
```

---

## Řešení problémů

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/vojtechbit/srealitymaklerscraper.git
```

### "error: failed to push some refs"
```bash
git pull origin main --rebase
git push
```

### "Permission denied (publickey)"
Nastav GitHub autentizaci:
- Token: https://github.com/settings/tokens
- SSH key: https://github.com/settings/keys

---

## Kontakt

🔗 GitHub: https://github.com/vojtechbit/srealitymaklerscraper
👤 Author: vojtechbit
