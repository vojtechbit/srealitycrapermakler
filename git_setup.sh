#!/bin/bash

# Git setup script pro nahrání do GitHub repozitáře
# https://github.com/vojtechbit/srealitymaklerscraper

echo "📦 Git Setup - Sreality Makler Scraper"
echo "======================================="
echo ""

# Kontrola, jestli je Git nainstalovaný
if ! command -v git &> /dev/null; then
    echo "❌ Git není nainstalován!"
    echo "   Stáhni z: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git je nainstalován"
echo ""

# Inicializace Git repozitáře (pokud ještě není)
if [ ! -d .git ]; then
    echo "🔧 Inicializuji Git repozitář..."
    git init
    echo ""
fi

# Nastavení remote (pokud ještě není nastavený)
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Přidávám GitHub remote..."
    git remote add origin https://github.com/vojtechbit/srealitymaklerscraper.git
    echo ""
fi

# Kontrola aktuálního stavu
echo "📊 Aktuální stav:"
git status
echo ""

# Přidání všech souborů
echo "➕ Přidávám soubory do Git..."
git add .
echo ""

# Zobrazení změn
echo "📝 Změny k commitnutí:"
git status --short
echo ""

# Commit
read -p "💬 Commit message [Initial commit]: " commit_msg
commit_msg=${commit_msg:-"Initial commit - Sreality scraper"}

git commit -m "$commit_msg"
echo ""

# Push do GitHubu
echo "🚀 Nahrávám na GitHub..."
echo "   Repozitář: https://github.com/vojtechbit/srealitymaklerscraper"
echo ""

# Pokud je to první push, použijeme -u
if git rev-parse --abbrev-ref --symbolic-full-name @{u} &> /dev/null; then
    git push
else
    git push -u origin main || git push -u origin master
fi

echo ""
echo "✨ Hotovo! Soubory jsou na GitHubu."
echo "🔗 https://github.com/vojtechbit/srealitymaklerscraper"
echo ""
