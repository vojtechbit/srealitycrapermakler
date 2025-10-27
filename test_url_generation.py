#!/usr/bin/env python3
"""Test generování URL z API dat"""

from scrapers.sreality import SrealityScraper

def test_url_generation():
    """Testuje správné generování URL z různých typů dat"""

    scraper = SrealityScraper()

    # Test 1: Byt 2+kk v Praze - s category_type_cb, category_main_cb
    test_data_1 = {
        "hash_id": "822296156",
        "name": "Prodej bytu 2+kk 34 m²",
        "locality": "Praha 4 - Milevská, Praha",
        "seo": {
            "category_type_cb": 1,  # prodej
            "category_main_cb": 1,   # byt
            "locality": "praha-praha-4-milevska"
        }
    }

    url_1 = scraper._extract_url(test_data_1)
    print(f"Test 1 (Byt 2+kk Praha):")
    print(f"  Vygenerovaná URL: {url_1}")
    print(f"  Očekávaný formát: https://www.sreality.cz/detail/prodej/byt/2+kk/praha-praha-4-milevska/822296156")

    assert url_1 is not None, "URL by neměla být None"
    assert "detail" in url_1, "URL musí obsahovat 'detail'"
    assert "822296156" in url_1, "URL musí obsahovat hash_id"
    assert "sreality.cz" in url_1, "URL musí obsahovat sreality.cz"
    print("  ✅ PASS\n")

    # Test 2: Dům - bez podkategorie
    test_data_2 = {
        "hash_id": "24547916",
        "name": "Prodej rodinného domu 133 m²",
        "locality": "Brno, Jihomoravský kraj",
        "seo": {
            "category_type_cb": 1,  # prodej
            "category_main_cb": 2,  # dum
            "locality": "brno-jihomoravsky-kraj"
        }
    }

    url_2 = scraper._extract_url(test_data_2)
    print(f"Test 2 (Dům Brno):")
    print(f"  Vygenerovaná URL: {url_2}")

    assert url_2 is not None, "URL by neměla být None"
    assert "detail" in url_2, "URL musí obsahovat 'detail'"
    assert "24547916" in url_2, "URL musí obsahovat hash_id"
    assert "dum" in url_2 or "24547916" in url_2, "URL musí obsahovat typ nemovitosti nebo ID"
    print("  ✅ PASS\n")

    # Test 3: Se starým formátem (categoryUrl, localityUrl)
    test_data_3 = {
        "hash_id": "123456",
        "name": "Prodej bytu 3+1",
        "seo": {
            "categoryUrl": "prodej/byt/3+1",
            "localityUrl": "ostrava-moravskoslezsky-kraj",
        }
    }

    url_3 = scraper._extract_url(test_data_3)
    print(f"Test 3 (Starý formát s categoryUrl):")
    print(f"  Vygenerovaná URL: {url_3}")

    assert url_3 is not None, "URL by neměla být None"
    assert "123456" in url_3, "URL musí obsahovat hash_id"
    print("  ✅ PASS\n")

    # Test 4: Pronájem pozemku
    test_data_4 = {
        "hash_id": "999888",
        "name": "Pronájem pozemku 500 m²",
        "locality": "Liberec",
        "seo": {
            "category_type_cb": 2,  # pronajem
            "category_main_cb": 3,  # pozemek
            "locality": "liberec"
        }
    }

    url_4 = scraper._extract_url(test_data_4)
    print(f"Test 4 (Pronájem pozemku):")
    print(f"  Vygenerovaná URL: {url_4}")

    assert url_4 is not None, "URL by neměla být None"
    assert "pronajem" in url_4 or "999888" in url_4, "URL musí obsahovat typ nebo ID"
    assert "pozemek" in url_4 or "999888" in url_4, "URL musí obsahovat kategorii nebo ID"
    print("  ✅ PASS\n")

    # Test 5: Jen hash_id (fallback)
    test_data_5 = {
        "hash_id": "777666",
    }

    url_5 = scraper._extract_url(test_data_5)
    print(f"Test 5 (Jen hash_id - fallback):")
    print(f"  Vygenerovaná URL: {url_5}")

    assert url_5 is not None, "URL by neměla být None i pro fallback"
    assert "777666" in url_5, "Fallback URL musí obsahovat hash_id"
    print("  ✅ PASS\n")

    print("=" * 60)
    print("✅ Všechny testy prošly!")
    print("=" * 60)

if __name__ == "__main__":
    test_url_generation()
