#!/usr/bin/env python3
"""Test různých API endpointů pro profily makléřů a realitních kanceláří."""

import requests
import json
import time

BASE_URL = "https://www.sreality.cz"
API_BASE = f"{BASE_URL}/api"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.sreality.cz/",
}

session = requests.Session()

# Nejdřív získej nějakého reálného makléře z inzerátů
print("🔍 Získávám vzorového makléře z inzerátů...")
params = {
    "category_main_cb": 1,  # Byty
    "category_type_cb": 1,  # Prodej
    "page": 1,
    "per_page": 10,
}

try:
    response = session.get(f"{API_BASE}/cs/v2/estates", params=params, headers=headers, timeout=30)

    if response.status_code != 200:
        print(f"❌ Chyba {response.status_code} při získávání inzerátů")
        exit(1)

    data = response.json()
    estates = data.get("_embedded", {}).get("estates", [])

    if not estates:
        print("❌ Žádné inzeráty")
        exit(1)

    # Získej detail prvního inzerátu
    first_estate = estates[0]
    hash_id = first_estate.get("hash_id")

    print(f"\n📋 Inzerát: {first_estate.get('name')}")
    print(f"   Hash ID: {hash_id}")

    time.sleep(2)

    detail_url = f"{API_BASE}/cs/v2/estates/{hash_id}"
    detail_response = session.get(detail_url, headers=headers, timeout=30)

    if detail_response.status_code != 200:
        print(f"❌ Chyba při získávání detailu")
        exit(1)

    detail = detail_response.json()
    embedded = detail.get("_embedded", {})

    seller = embedded.get("seller", {})
    broker = embedded.get("broker", {})
    company = embedded.get("company", {})

    print(f"\n👤 Makléř:")
    print(f"   Jméno: {seller.get('user_name') or broker.get('user_name')}")
    print(f"   User ID: {seller.get('user_id') or broker.get('user_id')}")
    print(f"   Seller ID: {seller.get('id')}")

    print(f"\n🏢 Realitní kancelář:")
    print(f"   Název: {company.get('name')}")
    print(f"   Company ID: {company.get('id')}")

    # Zkusíme různé API endpointy
    user_id = seller.get("user_id") or broker.get("user_id") or seller.get("id")
    company_id = company.get("id")

    print("\n" + "="*80)
    print("🔍 TESTOVÁNÍ API ENDPOINTŮ")
    print("="*80)

    # Seznam endpointů k otestování
    endpoints = [
        # Profil makléře
        (f"{API_BASE}/cs/v2/users/{user_id}", "User profile v2"),
        (f"{API_BASE}/cs/v1/users/{user_id}", "User profile v1"),
        (f"{API_BASE}/cs/v2/brokers/{user_id}", "Broker profile v2"),
        (f"{API_BASE}/cs/v1/brokers/{user_id}", "Broker profile v1"),
        (f"{API_BASE}/cs/v2/sellers/{user_id}", "Seller profile v2"),

        # Realitní kancelář
        (f"{API_BASE}/cs/v2/companies/{company_id}", "Company profile v2"),
        (f"{API_BASE}/cs/v1/companies/{company_id}", "Company profile v1"),

        # Makléři v kanceláři
        (f"{API_BASE}/cs/v2/companies/{company_id}/brokers", "Company brokers v2"),
        (f"{API_BASE}/cs/v2/companies/{company_id}/sellers", "Company sellers v2"),
        (f"{API_BASE}/cs/v2/companies/{company_id}/users", "Company users v2"),

        # Adresář
        (f"{API_BASE}/cs/v2/directory/companies/{company_id}", "Directory company v2"),
        (f"{API_BASE}/cs/v2/directory/brokers/{user_id}", "Directory broker v2"),

        # Inzeráty makléře
        (f"{API_BASE}/cs/v2/estates?user_id={user_id}&per_page=1", "Broker estates"),
    ]

    for endpoint, description in endpoints:
        print(f"\n📍 Testing: {description}")
        print(f"   URL: {endpoint}")

        time.sleep(0.5)  # Rate limiting

        try:
            test_response = session.get(endpoint, headers=headers, timeout=15)
            print(f"   Status: {test_response.status_code}")

            if test_response.status_code == 200:
                print("   ✅ SUCCESS!")
                try:
                    json_data = test_response.json()
                    # Zobraz klíče
                    if isinstance(json_data, dict):
                        keys = list(json_data.keys())[:10]
                        print(f"   Keys: {keys}")

                        # Zobraz část dat
                        print(f"   Data preview:")
                        print(f"   {json.dumps(json_data, indent=6, ensure_ascii=False)[:500]}...")
                except:
                    print(f"   Text: {test_response.text[:200]}...")
            elif test_response.status_code == 404:
                print("   ❌ Not found")
            elif test_response.status_code == 403:
                print("   ❌ Forbidden")
            else:
                print(f"   ⚠️  Other status")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "="*80)
    print("✅ TESTOVÁNÍ DOKONČENO")
    print("="*80)

except Exception as e:
    print(f"❌ Chyba: {e}")
    import traceback
    traceback.print_exc()
