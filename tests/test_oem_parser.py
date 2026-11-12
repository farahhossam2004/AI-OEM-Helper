

from src.services.catalog_service import CatalogService


def test_parse_oem_records():
    service = CatalogService()

    fake_response = {
        "products": [
            {
                "mfi": 11822,
                "mfd": "TOYOTA",
                "ns": "4243178010",
                "n": "4243178010",
                "d": "Тормозной диск",
                "sources": 98,
            }
        ]
    }

    results = service.parse_oem_response(fake_response)

    assert len(results) == 1
    assert results[0].oem_number == "4243178010"
    assert results[0].manufacturer_name == "TOYOTA"
    assert results[0].sources == 98
    assert results[0].verification_status == "catalog_candidate"


def test_parse_nested_oem_records():
    service = CatalogService()

    fake_response = {
        "data": {
            "items": [
                {
                    "mfi": 11822,
                    "mfd": "TOYOTA",
                    "ns": "4351233150",
                    "n": "4351233150",
                    "d": "Тормозной диск",
                    "sources": 78,
                }
            ]
        }
    }

    results = service.parse_oem_response(fake_response)

    assert len(results) == 1
    assert results[0].oem_number == "4351233150"


def test_duplicate_oem_records_are_removed():
    service = CatalogService()

    record = {
        "mfi": 11822,
        "mfd": "TOYOTA",
        "ns": "4243178010",
        "n": "4243178010",
        "d": "Тормозной диск",
        "sources": 98,
    }

    results = service.parse_oem_response([record, record])

    assert len(results) == 1


def test_empty_oem_response():
    service = CatalogService()

    results = service.parse_oem_response({"products": []})

    assert results == []
