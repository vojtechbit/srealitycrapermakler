"""Test script to explore Sreality.cz agent profile API."""

import requests
import json

# Nejdřív získáme nějakého makléře z existujících inzerátů
api_url = "https://www.sreality.cz/api/cs/v2/estates"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}

# Získáme první stránku inzerátů
params = {
    "category_main_cb": 1,  # Byty
    "category_type_cb": 1,  # Prodej
    "page": 1,
    "per_page": 10,
}

print("🔍 Získávám vzorový inzerát...")
response = requests.get(api_url, params=params, headers=headers, timeout=30)

if response.status_code == 200:
    data = response.json()
    estates = data.get("_embedded", {}).get("estates", [])

    if estates:
        first_estate = estates[0]
        hash_id = first_estate.get("hash_id")

        print(f"\n📋 Vzorový inzerát: {first_estate.get('name')}")
        print(f"   Hash ID: {hash_id}")

        # Získáme detail inzerátu
        detail_url = f"https://www.sreality.cz/api/cs/v2/estates/{hash_id}"
        print(f"\n🔍 Stahuji detail inzerátu...")

        detail_response = requests.get(detail_url, headers=headers, timeout=30)

        if detail_response.status_code == 200:
            detail = detail_response.json()

            # Hledáme makléře
            embedded = detail.get("_embedded", {})
            seller = embedded.get("seller", {})
            broker = embedded.get("broker", {})

            print(f"\n👤 Informace o makléři:")
            print(f"   Jméno: {seller.get('user_name') or broker.get('user_name')}")
            print(f"   ID: {seller.get('id') or broker.get('id')}")
            print(f"   User ID: {seller.get('user_id') or broker.get('user_id')}")

            # Zkusíme různé možné API endpointy pro profily
            agent_id = seller.get("user_id") or broker.get("user_id") or seller.get("id") or broker.get("id")

            if agent_id:
                print(f"\n🔍 Zkoušíme různé API endpointy pro profil makléře {agent_id}...")

                # Možné varianty
                endpoints = [
                    f"https://www.sreality.cz/api/cs/v2/users/{agent_id}",
                    f"https://www.sreality.cz/api/cs/v2/agents/{agent_id}",
                    f"https://www.sreality.cz/api/cs/v2/brokers/{agent_id}",
                    f"https://www.sreality.cz/api/cs/v2/sellers/{agent_id}",
                ]

                for endpoint in endpoints:
                    print(f"\n   Zkouším: {endpoint}")
                    test_response = requests.get(endpoint, headers=headers, timeout=30)
                    print(f"   Status: {test_response.status_code}")

                    if test_response.status_code == 200:
                        print("   ✅ Funguje!")
                        agent_data = test_response.json()
                        print(f"   Data: {json.dumps(agent_data, indent=2, ensure_ascii=False)[:500]}...")
                        break
                    elif test_response.status_code == 404:
                        print("   ❌ Neexistuje")
                    else:
                        print(f"   ⚠️  Jiná chyba: {test_response.status_code}")

            # Zkusíme také najít inzeráty od tohoto makléře
            print(f"\n🔍 Hledám všechny inzeráty od tohoto makléře...")

            if agent_id:
                agent_estates_url = f"https://www.sreality.cz/api/cs/v2/estates"
                agent_params = {
                    "user_id": agent_id,
                    "per_page": 60,
                }

                print(f"   URL: {agent_estates_url}")
                print(f"   Params: {agent_params}")

                agent_estates_response = requests.get(
                    agent_estates_url,
                    params=agent_params,
                    headers=headers,
                    timeout=30
                )

                print(f"   Status: {agent_estates_response.status_code}")

                if agent_estates_response.status_code == 200:
                    agent_estates = agent_estates_response.json()
                    count = agent_estates.get("result_size", 0)
                    print(f"   ✅ Našel jsem {count} inzerátů od tohoto makléře!")

                    estates_list = agent_estates.get("_embedded", {}).get("estates", [])
                    print(f"   Prvních pár inzerátů:")
                    for i, est in enumerate(estates_list[:3], 1):
                        print(f"      {i}. {est.get('name')}")
                else:
                    print(f"   ❌ Nepodařilo se načíst inzeráty")

            print("\n" + "="*60)
            print("SOUHRN ZJIŠTĚNÍ:")
            print("="*60)

else:
    print(f"❌ Chyba při načítání inzerátů: {response.status_code}")
