#!/usr/bin/env python3
"""Analyzuj, jaká data vrací API o makléřích."""

import requests
import json
import time
from pprint import pprint

BASE_URL = "https://www.sreality.cz"
API_BASE = f"{BASE_URL}/api"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.sreality.cz/",
}

session = requests.Session()

print("🔍 Analyzuji data o makléřích z API...")

params = {
    "category_main_cb": 1,
    "category_type_cb": 1,
    "page": 1,
    "per_page": 3,
}

try:
    response = session.get(f"{API_BASE}/cs/v2/estates", params=params, headers=headers, timeout=30)

    if response.status_code != 200:
        print(f"❌ Chyba {response.status_code}")
        exit(1)

    data = response.json()
    estates = data.get("_embedded", {}).get("estates", [])

    if not estates:
        print("❌ Žádné inzeráty")
        exit(1)

    # Analyzuj první 3 inzeráty
    for i, estate in enumerate(estates, 1):
        print(f"\n{'='*80}")
        print(f"INZERÁT #{i}")
        print('='*80)

        hash_id = estate.get("hash_id")
        print(f"\nHash ID: {hash_id}")
        print(f"Název: {estate.get('name')}")

        # Hledej všechna pole obsahující "seller", "broker", "user", "company"
        print(f"\n🔍 Klíče v základních datech inzerátu:")
        relevant_keys = [k for k in estate.keys() if any(word in k.lower() for word in ['seller', 'broker', 'user', 'company', 'agent'])]
        for key in relevant_keys:
            print(f"  • {key}: {estate.get(key)}")

        # Získej detail
        time.sleep(2)
        detail_url = f"{API_BASE}/cs/v2/estates/{hash_id}"
        detail_response = session.get(detail_url, headers=headers, timeout=30)

        if detail_response.status_code != 200:
            print(f"❌ Chyba při detailu")
            continue

        detail = detail_response.json()

        print(f"\n🔍 _embedded klíče:")
        embedded = detail.get("_embedded", {})
        print(f"  Dostupné klíče: {list(embedded.keys())}")

        # Seller
        if "seller" in embedded:
            print(f"\n👤 SELLER:")
            seller = embedded["seller"]
            print(json.dumps(seller, indent=2, ensure_ascii=False))

        # Broker
        if "broker" in embedded:
            print(f"\n👤 BROKER:")
            broker = embedded["broker"]
            print(json.dumps(broker, indent=2, ensure_ascii=False))

        # Company
        if "company" in embedded:
            print(f"\n🏢 COMPANY:")
            company = embedded["company"]
            print(json.dumps(company, indent=2, ensure_ascii=False))

        # Hledej jakékoliv URL v celém detailu
        print(f"\n🔗 Hledám URL v datech...")

        def find_urls(obj, path=""):
            """Rekurzivně najdi všechny URL v objektu."""
            urls = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and ("http" in value or "/" in value):
                        if "sreality" in value or value.startswith("/"):
                            urls.append((new_path, value))
                    urls.extend(find_urls(value, new_path))
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    urls.extend(find_urls(item, f"{path}[{idx}]"))
            return urls

        urls = find_urls(detail)
        for path, url in urls:
            if "makler" in url.lower() or "broker" in url.lower() or "seller" in url.lower() or "adresar" in url.lower():
                print(f"  ✅ {path}: {url}")

except Exception as e:
    print(f"❌ Chyba: {e}")
    import traceback
    traceback.print_exc()
