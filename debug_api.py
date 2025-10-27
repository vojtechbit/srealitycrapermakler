#!/usr/bin/env python3
"""Debug script - ukáže strukturu API pro jeden inzerát"""

import requests
import json
import time

BASE_URL = "https://www.sreality.cz"
API_URL = f"{BASE_URL}/api/cs/v2/estates"

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.sreality.cz/',
}

print("🔍 Stahuju seznam inzerátů...")

params = {
    'category_main_cb': 1,  # Byty
    'category_type_cb': 1,  # Prodej
    'page': 1,
    'per_page': 3,
}

response = session.get(API_URL, params=params, headers=headers, timeout=30)

if response.status_code != 200:
    print(f"❌ Chyba {response.status_code}")
    print("Pravděpodobně Cloudflare blokace. Zkus znovu za chvíli.")
    exit(1)

data = response.json()
estates = data.get('_embedded', {}).get('estates', [])

if not estates:
    print("❌ Žádné inzeráty")
    exit(1)

print(f"✅ Staženo {len(estates)} inzerátů\n")

# Vezmi první inzerát
estate = estates[0]
estate_id = estate.get('hash_id')

print("="*80)
print(f"ZÁKLADNÍ INFO (bez detailu) - ID: {estate_id}")
print("="*80)
print(json.dumps(estate, indent=2, ensure_ascii=False))

# Stáhni detail
print("\n\n")
print("="*80)
print(f"DETAIL INZERÁTU - ID: {estate_id}")
print("="*80)

time.sleep(2)

detail_url = f"{BASE_URL}/api/cs/v2/estates/{estate_id}"
detail_response = session.get(detail_url, headers=headers, timeout=30)

if detail_response.status_code == 200:
    detail = detail_response.json()
    print(json.dumps(detail, indent=2, ensure_ascii=False))

    # Extrahuj důležité části
    print("\n\n")
    print("="*80)
    print("DŮLEŽITÉ ČÁSTI PRO KONTAKTY:")
    print("="*80)

    embedded = detail.get('_embedded', {})

    print("\n1. _embedded klíče:")
    print(list(embedded.keys()))

    if 'seller' in embedded:
        print("\n2. _embedded.seller:")
        print(json.dumps(embedded['seller'], indent=2, ensure_ascii=False))

    if 'company' in embedded:
        print("\n3. _embedded.company:")
        print(json.dumps(embedded['company'], indent=2, ensure_ascii=False))

    if 'broker' in embedded:
        print("\n4. _embedded.broker:")
        print(json.dumps(embedded['broker'], indent=2, ensure_ascii=False))

    if 'contact' in detail:
        print("\n5. detail.contact:")
        print(json.dumps(detail['contact'], indent=2, ensure_ascii=False))

    # Zkus najít jakékoliv telefony nebo emaily
    print("\n\n")
    print("="*80)
    print("HLEDÁNÍ TELEFONŮ A EMAILŮ V CELÉM JSON:")
    print("="*80)

    def find_in_dict(d, search_keys):
        """Rekurzivně hledá klíče v dictionary"""
        results = []
        if isinstance(d, dict):
            for key, value in d.items():
                if any(search in key.lower() for search in search_keys):
                    results.append(f"{key}: {value}")
                if isinstance(value, (dict, list)):
                    results.extend(find_in_dict(value, search_keys))
        elif isinstance(d, list):
            for item in d:
                results.extend(find_in_dict(item, search_keys))
        return results

    phones = find_in_dict(detail, ['phone', 'tel', 'mobile', 'telefon'])
    emails = find_in_dict(detail, ['email', 'mail'])

    print("\nNALEZENÉ TELEFONY:")
    for p in phones:
        print(f"  • {p}")

    print("\nNALEZENÉ EMAILY:")
    for e in emails:
        print(f"  • {e}")

else:
    print(f"❌ Chyba při stahování detailu: {detail_response.status_code}")

print("\n\n✅ Hotovo!")
