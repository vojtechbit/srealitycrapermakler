#!/usr/bin/env python3
"""Test instalace - ověří, že jsou všechny potřebné knihovny nainstalované"""

def test_imports():
    """Zkontroluje import všech potřebných knihoven"""
    print("🔍 Kontroluji nainstalované knihovny...\n")

    errors = []
    success = []

    # Test requests
    try:
        import requests
        success.append(f"✅ requests {requests.__version__}")
    except ImportError as e:
        errors.append(f"❌ requests - není nainstalován")

    # Test pandas
    try:
        import pandas as pd
        success.append(f"✅ pandas {pd.__version__}")
    except ImportError as e:
        errors.append(f"❌ pandas - není nainstalován")

    # Test openpyxl
    try:
        import openpyxl
        success.append(f"✅ openpyxl {openpyxl.__version__}")
    except ImportError as e:
        errors.append(f"❌ openpyxl - není nainstalován")

    # Výsledky
    print("\n".join(success))

    if errors:
        print("\n" + "\n".join(errors))
        print("\n❌ Některé knihovny chybí!")
        print("\nNainstaluj je pomocí:")
        print("  pip3 install -r requirements.txt")
        return False
    else:
        print("\n✨ Všechny knihovny jsou nainstalované!")
        print("\n✅ Můžeš spustit scraper:")
        print("  python3 sreality_scraper.py")
        return True

if __name__ == "__main__":
    test_imports()
