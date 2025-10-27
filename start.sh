#!/bin/bash

# Quick start script pro Sreality Scraper

echo "🏠 Sreality Scraper - Quick Start"
echo "=================================="
echo ""

# Kontrola Pythonu
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 není nainstalován!"
    echo "   Stáhni z: https://www.python.org/downloads/"
    exit 1
fi

# Kontrola závislostí
if ! python3 -c "import requests, pandas, openpyxl" 2>/dev/null; then
    echo "📦 Instaluji závislosti..."
    pip3 install -r requirements.txt
    echo ""
fi

# Vytvoření data složky
mkdir -p data

# Spuštění scraperu
echo "🚀 Spouštím scraper..."
echo ""
python3 sreality_scraper.py

echo ""
echo "✅ Hotovo!"
