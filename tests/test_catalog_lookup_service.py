
import pytest

from src.integrations.fapi_adapter import FAPIQuotaError
from src.services.catalog_lookup_service import CatalogLookupService


class FakeFAPIAdapter:

    def get_manufacturers(self):
        return {
            "mf": [
                {"dbi": 111, "ds": "TOYOTA", "da": "TOYOTA"}
            ]
        }

    def get_models(self, manufacturer_id):
        assert manufacturer_id == 111

        return {
            "m": [
                {
                    "i": 45723,
                    "dbi": 45723,
                    "d": "CAMRY",
                    "fd": "TOYOTA CAMRY",
                    "cb": 1704067200000,
                }
            ]
        }

    def get_modifications(self, model_id):
        assert model_id == 45723

        return {
            "m": [
                {
                    "dbi": 159441,
                    "d": "2.5 Hybrid",
                    "fd": "2.5 Hybrid A25A-FXS",
                    "cb": 1704067200000,
                    "ce": None,
                    "p": {"p": ["2.5l", "A25A-FXS"]},
                }
            ]
        }

    def get_parts_tree(self, modification_id):
        assert modification_id == 159441

        return {
            "nodes": [
                {
                    "i": 100032,
                    "d": "Тормозной диск",
                }
            ]
        }

    def get_oem_parts(self, modification_id, node_id, strict=True):
        assert modification_id == 159441
        assert node_id == 100032

        return {
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


class FakeQuotaAdapter(FakeFAPIAdapter):

    def get_manufacturers(self):
        raise FAPIQuotaError("Quota exceeded")


class FakeAmbiguousAdapter(FakeFAPIAdapter):

    def get_modifications(self, model_id):
        data = super().get_modifications(model_id)

        data["m"].append({
            "dbi": 159975,
            "d": "2.0 Petrol",
            "fd": "2.0 Petrol M20A-FKS",
            "cb": 1704067200000,
            "ce": None,
            "p": {"p": ["2.0l", "M20A-FKS"]},
        })

        return data


class FakeEmptyOEMAdapter(FakeFAPIAdapter):

    def get_oem_parts(self, modification_id, node_id, strict=True):
        return {"products": []}


def create_request():
    from src.models.extracted_vehicle_request import ExtractedVehicleRequest

    return ExtractedVehicleRequest(
        make="Toyota",
        model="Camry",
        year=2026,
        part_name="Brake Discs",
        position="front",
        needs_clarification=False,
        clarification_question=None,
    )


def test_complete_catalog_lookup():
    service = CatalogLookupService(FakeFAPIAdapter())

    result = service.lookup(create_request())

    assert result.status == "found"
    assert len(result.parts) == 1
    assert result.parts[0].oem_number == "4243178010"
    assert result.parts[0].verification_status == "catalog_candidate"


def test_multiple_modifications_require_clarification():
    service = CatalogLookupService(FakeAmbiguousAdapter())

    result = service.lookup(create_request())

    assert result.status == "needs_clarification"
    assert result.clarification_question is not None


def test_quota_error_is_handled():
    service = CatalogLookupService(FakeQuotaAdapter())

    result = service.lookup(create_request())

    assert result.status == "quota_exceeded"
    assert result.parts == []


def test_empty_oem_results():
    service = CatalogLookupService(FakeEmptyOEMAdapter())

    result = service.lookup(create_request())

    assert result.status == "not_found"
    assert result.parts == []
