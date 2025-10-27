#!/usr/bin/env python3
"""
Test script - ověří, že jsou nainstalované všechny závislosti
"""

import sys

def test_dependencies():
    """Testuje, zda jsou nainstalované všechny potřebné knihovny"""
    print("🔍 Testuji závislosti...\n")
    
    dependencies = {
        'requests': 'HTTP requesty',
        'pandas': 'Zpracování dat',
        'openpyxl': 'Excel výstup',
    }
    
    all_ok = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"✅ {package:12} - {description}")
        except ImportError:
            print(f"❌ {package:12} - {description} - CHYBÍ!")
            all_ok = False
    
    print()
    
    if all_ok:
        print("✨ Všechny závislosti jsou nainstalované!")
        print("\nMůžeš spustit scraper:")
        print("  python3 sreality_scraper.py")
        return True
    else:
        print("⚠️  Některé závislosti chybí!")
        print("\nNainstaluj je pomocí:")
        print("  pip3 install -r requirements.txt")
        return False


def test_python_version():
    """Ověří verzi Pythonu"""
    print("🐍 Python verze:", sys.version.split()[0])
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python verze je OK (3.8+)\n")
        return True
    else:
        print("❌ Python verze je příliš stará! Potřebuješ 3.8+\n")
        return False


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         SREALITY SCRAPER - TEST ZÁVISLOSTÍ                ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    python_ok = test_python_version()
    deps_ok = test_dependencies()
    
    if python_ok and deps_ok:
        print("\n✨ Vše je připraveno k použití!")
    else:
        print("\n⚠️  Oprav prosím chyby výše.")
    
    print()


if __name__ == "__main__":
    main()
