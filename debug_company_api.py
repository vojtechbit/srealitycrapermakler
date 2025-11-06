#!/usr/bin/env python3
"""
Debug script - zkouší různé API endpointy pro company
Cíl: Zjistit, jestli existuje endpoint, který vrací seznam makléřů z RK
"""

import json
import requests
import time

def test_company_endpoints():
    # Nejdřív získáme nějakou company_id z běžného výpisu
    print("="*80)
    print("🔍 Krok 1: Získávám company_id z výpisu inzerátů")
    print("="*80)

    url = "https://www.sreality.cz/api/cs/v2/estates"
    params = {
        "category_main_cb": 2,  # Domy
        "category_type_cb": 2,  # Pronájem
        "page": 1,
        "per_page": 10,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Chyba {response.status_code}")
            return

        data = response.json()
        estates = data.get("_embedded", {}).get("estates", [])

        if not estates:
            print("❌ Žádné inzeráty")
            return

        # Získáme první company
        company = None
        company_id = None
        company_url = None

        for estate in estates:
            embedded = estate.get("_embedded", {})
            comp = embedded.get("company", {})
            if comp and comp.get("id"):
                company = comp
                company_id = comp.get("id")
                company_url = comp.get("url")
                break

        if not company_id:
            print("❌ Nenašel jsem žádnou company")
            return

        print(f"\n✅ Našel jsem company:")
        print(f"   ID: {company_id}")
        print(f"   Název: {company.get('name')}")
        print(f"   URL: {company_url}")
        print(f"   Všechny klíče: {list(company.keys())}")

        # Teď zkusíme různé API endpointy
        print("\n" + "="*80)
        print("🔍 Krok 2: Zkoušíme různé API endpointy pro company")
        print("="*80)

        test_endpoints = [
            f"https://www.sreality.cz/api/cs/v2/companies/{company_id}",
            f"https://www.sreality.cz/api/cs/v2/companies/{company_id}/agents",
            f"https://www.sreality.cz/api/cs/v2/companies/{company_id}/brokers",
            f"https://www.sreality.cz/api/cs/v2/companies/{company_id}/users",
            f"https://www.sreality.cz/api/cs/v2/companies/{company_id}/employees",
            f"https://www.sreality.cz/api/cs/v2/company/{company_id}",
            f"https://www.sreality.cz/api/cs/v2/company/{company_id}/agents",
            f"https://www.sreality.cz/api/cs/v1/companies/{company_id}",
        ]

        # Pokud má company URL, zkusíme i to
        if company_url:
            # Např. /realitni-kancelar/12345
            # Zkusíme https://www.sreality.cz/api/cs/v2{company_url}
            test_endpoints.append(f"https://www.sreality.cz/api/cs/v2{company_url}")
            test_endpoints.append(f"https://www.sreality.cz/api/cs/v2{company_url}/agents")

        for endpoint in test_endpoints:
            print(f"\n🔗 Zkouším: {endpoint}")
            time.sleep(1)  # Delay mezi požadavky

            try:
                resp = requests.get(endpoint, headers=headers, timeout=30)
                print(f"   Status: {resp.status_code}")

                if resp.status_code == 200:
                    print("   ✅ FUNGUJE! Odpověď:")
                    try:
                        json_data = resp.json()

                        # Vypsat strukturu
                        print(f"   📋 Top-level klíče: {list(json_data.keys())}")

                        # Hledat makléře/agenty
                        if "_embedded" in json_data:
                            embedded = json_data["_embedded"]
                            print(f"   📋 _embedded klíče: {list(embedded.keys())}")

                            # Hledat pole s makléři
                            for key in embedded:
                                if any(word in key.lower() for word in ['agent', 'broker', 'user', 'employee', 'seller']):
                                    items = embedded[key]
                                    if isinstance(items, list):
                                        print(f"   🎯 NAŠEL JSEM: {key} (počet: {len(items)})")
                                        if items:
                                            print(f"   📄 První položka:")
                                            print(json.dumps(items[0], indent=4, ensure_ascii=False))

                        # Vypsat celou odpověď (zkráceně)
                        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                        if len(json_str) > 1000:
                            print(f"   📄 Odpověď (první 1000 znaků):")
                            print(json_str[:1000] + "\n   ...")
                        else:
                            print(f"   📄 Celá odpověď:")
                            print(json_str)
                    except:
                        print(f"   📄 Odpověď (text): {resp.text[:500]}")

                elif resp.status_code == 404:
                    print("   ❌ 404 - endpoint neexistuje")
                elif resp.status_code == 403:
                    print("   ⚠️  403 - Cloudflare/forbidden")
                else:
                    print(f"   ⚠️  Neočekávaný status")

            except Exception as e:
                print(f"   ❌ Chyba: {e}")

        print("\n" + "="*80)
        print("✅ Test dokončen!")
        print("="*80)

    except Exception as e:
        print(f"❌ Chyba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_company_endpoints()
