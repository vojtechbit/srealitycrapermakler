#!/usr/bin/env python3
"""
Debug script - zaměřuje se na _embedded.sellers z company API
"""

import json
import requests

def test_sellers_endpoint():
    print("="*80)
    print("🔍 Test: _embedded.sellers z company API")
    print("="*80)

    # Použijeme company_id z předchozího testu
    company_id = 13950  # REMACH realitní kancelář

    url = f"https://www.sreality.cz/api/cs/v2/companies/{company_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    try:
        print(f"\n🔗 Stahuji: {url}")
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Chyba {response.status_code}")
            return

        data = response.json()

        # Zaměříme se na sellers
        embedded = data.get("_embedded", {})
        sellers = embedded.get("sellers", {})

        if not sellers:
            print("❌ Klíč 'sellers' neexistuje nebo je prázdný")
            return

        print("\n✅ Našel jsem 'sellers'!")
        print(f"📋 Typ: {type(sellers)}")

        if isinstance(sellers, dict):
            print(f"📋 Klíče v sellers: {list(sellers.keys())}")

            # Hledáme seznam makléřů
            for key, value in sellers.items():
                print(f"\n🔍 Kontroluji klíč: '{key}'")
                print(f"   Typ hodnoty: {type(value)}")

                if isinstance(value, list):
                    print(f"   ✅ Je to seznam! Počet položek: {len(value)}")
                    if value:
                        print(f"   📄 První položka:")
                        print(json.dumps(value[0], indent=4, ensure_ascii=False))

                        # Zkontroluj, jestli má user_id
                        if isinstance(value[0], dict):
                            if "user_id" in value[0]:
                                print(f"\n   🎯 NALEZEN user_id: {value[0].get('user_id')}")
                            if "id" in value[0]:
                                print(f"   🎯 NALEZEN id: {value[0].get('id')}")

                            print(f"   📋 Všechny klíče v první položce: {list(value[0].keys())}")

                        # Pokud je položek více, zobraz i další
                        if len(value) > 1:
                            print(f"\n   📄 Druhá položka:")
                            print(json.dumps(value[1], indent=4, ensure_ascii=False))

                        if len(value) > 2:
                            print(f"\n   ... a dalších {len(value) - 2} položek")

                elif isinstance(value, dict):
                    print(f"   ℹ️  Je to dictionary")
                    print(f"   Klíče: {list(value.keys())}")

                    # Možná je tam _embedded s makléři
                    if "_embedded" in value:
                        inner_embedded = value["_embedded"]
                        print(f"   📋 _embedded klíče: {list(inner_embedded.keys())}")
                else:
                    print(f"   Hodnota: {value}")

        elif isinstance(sellers, list):
            print(f"✅ 'sellers' je přímo seznam! Počet: {len(sellers)}")
            if sellers:
                print(f"\n📄 První makléř:")
                print(json.dumps(sellers[0], indent=4, ensure_ascii=False))

        # Zobraz i další užitečné info z company
        print("\n" + "="*80)
        print("ℹ️  Další informace o company:")
        print("="*80)
        print(f"seller_count: {data.get('seller_count')}")
        print(f"estates_count: {data.get('estates_count')}")
        print(f"premise_count: {data.get('premise_count')}")

        print("\n" + "="*80)
        print("✅ Test dokončen!")
        print("="*80)

    except Exception as e:
        print(f"❌ Chyba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sellers_endpoint()
