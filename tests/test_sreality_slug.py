from scrapers.sreality import _slugify_locality


def test_slugify_locality_preserves_numeric_parts():
    value = "Praha, Praha 4 - Milevská"
    assert _slugify_locality(value) == "praha-praha-4-milevska"


def test_slugify_locality_handles_empty_result():
    assert _slugify_locality("   ") is None
