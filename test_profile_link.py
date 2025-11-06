#!/usr/bin/env python3
"""
Test: Ověří, že link na profil makléře funguje
"""

import unicodedata
import re

def slugify(name):
    """Převede název na URL-friendly slug."""
    if not name:
        return "company"
    normalized = unicodedata.normalize("NFKD", name)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.lower()
    ascii_value = re.sub(r"[^a-z0-9]+", "-", ascii_value)
    ascii_value = re.sub(r"-+", "-", ascii_value)
    return ascii_value.strip("-") or "company"

# Data z předchozích testů
company_name = "REMACH realitní kancelář"
company_id = 13950
seller_id = 72849  # Ing. Lucie Mikulíková
seller_name = "Ing. Lucie Mikulíková"

# Vytvoř URL
company_slug = slugify(company_name)
profile_url = f"https://www.sreality.cz/adresar/{company_slug}/{company_id}/makleri/{seller_id}"

print("="*80)
print("🔗 Test URL profilu makléře")
print("="*80)
print()
print(f"Company: {company_name}")
print(f"Company ID: {company_id}")
print(f"Company slug: {company_slug}")
print()
print(f"Makléř: {seller_name}")
print(f"Makléř ID: {seller_id}")
print()
print(f"✅ Vygenerovaný URL:")
print(f"   {profile_url}")
print()
print("="*80)
print("👉 ZKUS OTEVŘÍT TENTO LINK V PROHLÍŽEČI!")
print("="*80)
print()
print("Pokud link funguje → můžeme pokračovat s optimalizací!")
print("Pokud NE → musíme upravit formát URL")
