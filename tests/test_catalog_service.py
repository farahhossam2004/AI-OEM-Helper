
import pytest

from src.services.catalog_service import (
    CatalogService,
    CatalogMatchNotFound,
)


def test_find_toyota_manufacturer():
    service = CatalogService()

    data = {
        "mf": [
            {"i": 1095, "ds": "TOYOTA", "da": "TOYOTA", "dbi": 111},
            {"i": 100, "ds": "HONDA", "da": "HONDA", "dbi": 100},
        ]
    }

    result = service.find_manufacturer(data, "Toyota")

    assert result["dbi"] == 111


def test_find_camry_model():
    service = CatalogService()

    data = {
        "m": [
            {
                "i": 45723,
                "dbi": 45723,
                "d": "CAMRY (_VA8_, _VH8_, _V8_)",
                "fd": "TOYOTA CAMRY (_VA8_, _VH8_, _V8_)",
                "cb": 1704056400000,
            }
        ]
    }

    results = service.find_models(data, "Camry", 2026)

    assert len(results) == 1
    assert results[0]["i"] == 45723


def test_find_brake_disc_node():
    service = CatalogService()

    tree = {
        "nodes": [
            {
                "i": 100006,
                "d": "Тормозная система",
                "children": [
                    {
                        "i": 100032,
                        "d": "Тормозной диск",
                    }
                ],
            }
        ]
    }

    results = service.find_part_nodes(tree, "Brake Discs")

    assert len(results) == 1
    assert results[0]["i"] == 100032


def test_unsupported_part_mapping():
    service = CatalogService()

    with pytest.raises(CatalogMatchNotFound):
        service.find_part_nodes({}, "Air Filter")
