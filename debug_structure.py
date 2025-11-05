#!/usr/bin/env python3
"""
Debug script - zkontroluje strukturu dat z API
"""

import json
import requests

def debug_api():
    url = "https://www.sreality.cz/api/cs/v2/estates"
    params = {
        "category_main_cb": 2,  # Domy
        "category_type_cb": 2,  # Pronájem
        "page": 1,
        "per_page": 5,  # Jen 5 inzerátů pro test
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    try:
        print("🔍 Stahuju první inzerát...")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Chyba {response.status_code}")
            return

        data = response.json()
        estates = data.get("_embedded", {}).get("estates", [])

        print(f"\n✅ Nalezeno {len(estates)} inzerátů")

        if not estates:
            print("⚠️  Žádné inzeráty")
            return

        # Projdi první 3 inzeráty
        for idx, estate in enumerate(estates[:3], 1):
            print("\n" + "="*80)
            print(f"INZERÁT #{idx}")
            print("="*80)

            # Základní info
            print(f"\nhash_id: {estate.get('hash_id')}")
            print(f"name: {estate.get('name')}")

            # _embedded struktura
            embedded = estate.get("_embedded", {})
            print(f"\n_embedded keys: {list(embedded.keys())}")

            # Seller
            seller = embedded.get("seller", {})
            if seller:
                print("\n📌 SELLER:")
                print(json.dumps(seller, indent=2, ensure_ascii=False))
            else:
                print("\n⚠️  Žádný seller")

            # Broker
            broker = embedded.get("broker", {})
            if broker:
                print("\n📌 BROKER:")
                print(json.dumps(broker, indent=2, ensure_ascii=False))
            else:
                print("\n⚠️  Žádný broker")

            # Company
            company = embedded.get("company", {})
            if company:
                print("\n📌 COMPANY:")
                print(json.dumps(company, indent=2, ensure_ascii=False))

            # Phones
            phones = embedded.get("phones", [])
            if phones:
                print(f"\n📞 PHONES: {phones}")

            # Emails
            emails = embedded.get("emails", [])
            if emails:
                print(f"\n📧 EMAILS: {emails}")

            # _links struktura
            links = estate.get("_links", {})
            if links:
                print(f"\n🔗 _links keys: {list(links.keys())}")

                # Self link
                self_link = links.get("self", {})
                if self_link:
                    print(f"   self: {self_link}")

                # Další linky
                for key in links:
                    if key != "self":
                        print(f"   {key}: {links[key]}")

            print("\n" + "="*80)

    except Exception as e:
        print(f"❌ Chyba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api()
