#!/usr/bin/env python3
"""
Debug: Testuje, jestli můžeme filtrovat inzeráty podle seller_id
"""

import requests

def test_seller_filter():
    print("="*80)
    print("🔍 Test: Filtrování inzerátů podle seller_id")
    print("="*80)

    # Použijeme seller_id z předchozího testu
    seller_id = 72849  # Ing. Lucie Mikulíková

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    # Zkusíme různé názvy parametru
    test_params = [
        {"seller_id": seller_id},
        {"user_id": seller_id},
        {"agent_id": seller_id},
        {"broker_id": seller_id},
        {"seller": seller_id},
    ]

    for params in test_params:
        param_name = list(params.keys())[0]
        print(f"\n🔗 Zkouším parametr: {param_name}={seller_id}")

        url = "https://www.sreality.cz/api/cs/v2/estates"
        full_params = {
            **params,
            "per_page": 5,
        }

        try:
            response = requests.get(url, params=full_params, headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                result_size = data.get("result_size", 0)
                estates = data.get("_embedded", {}).get("estates", [])

                print(f"   ✅ FUNGUJE!")
                print(f"   📊 Celkem inzerátů: {result_size}")
                print(f"   📋 Vráceno v této stránce: {len(estates)}")

                if estates:
                    first_estate = estates[0]
                    embedded = first_estate.get("_embedded", {})
                    print(f"   📄 První inzerát:")
                    print(f"      name: {first_estate.get('name')}")
                    print(f"      _embedded keys: {list(embedded.keys())}")

                    # Zkontroluj, jestli má seller s našim ID
                    seller = embedded.get("seller", {})
                    if seller:
                        print(f"      ✅ seller found: id={seller.get('id')}, name={seller.get('user_name')}")

            elif response.status_code == 400:
                print(f"   ❌ 400 - neplatný parametr")
            elif response.status_code == 403:
                print(f"   ⚠️  403 - Cloudflare/forbidden")
            else:
                print(f"   ⚠️  Status: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Chyba: {e}")

    print("\n" + "="*80)
    print("✅ Test dokončen!")
    print("="*80)

if __name__ == "__main__":
    test_seller_filter()
