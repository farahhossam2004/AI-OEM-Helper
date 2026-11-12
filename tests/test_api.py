
from fastapi.testclient import TestClient

import src.api.app as api_module

from src.models.catalog_lookup_result import CatalogLookupResult
from src.models.extracted_vehicle_request import ExtractedVehicleRequest
from src.models.oem_part import OEMPart


class FakeLLM:

    def extract_vehicle_request(self, user_text):
        return ExtractedVehicleRequest(
            make="Toyota",
            model="Camry",
            year=2026,
            part_name="Brake Discs",
            position="front",
            needs_clarification=False,
            clarification_question=None,
        )

    def generate(self, prompt):
        return ""


class FakeFAPIAdapter:

    def close(self):
        pass


class FakeCatalogLookupService:

    def __init__(self, adapter):
        self.adapter = adapter

    def lookup(self, request):
        return CatalogLookupResult(
            status="found",
            parts=[
                OEMPart(
                    oem_number="4243178010",
                    description="Brake Disc",
                    manufacturer_name="TOYOTA",
                    sources=98,
                )
            ],
            selected_modification_id=159441,
            selected_modification_name="2.5 Hybrid A25A-FXS",
        )


def setup_test_client(monkeypatch):
    monkeypatch.setattr(
        api_module,
        "get_llm_provider",
        lambda: FakeLLM(),
    )

    monkeypatch.setattr(
        api_module,
        "FAPIAdapter",
        FakeFAPIAdapter,
    )

    monkeypatch.setattr(
        api_module,
        "CatalogLookupService",
        FakeCatalogLookupService,
    )

    return TestClient(api_module.app)


def test_health_endpoint(monkeypatch):
    with setup_test_client(monkeypatch) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_lookup_endpoint_returns_oem_result(monkeypatch):
    with setup_test_client(monkeypatch) as client:
        response = client.post(
            "/api/v1/lookup",
            json={"message": "هوبات كامري 2026 أمامي"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "found"
    assert data["catalog_result"]["parts"][0]["oem_number"] == "4243178010"
    assert "4243178010" in data["response"]


def test_lookup_rejects_empty_message(monkeypatch):
    with setup_test_client(monkeypatch) as client:
        response = client.post(
            "/api/v1/lookup",
            json={"message": "   "},
        )

    assert response.status_code == 422


def test_lookup_rejects_missing_message(monkeypatch):
    with setup_test_client(monkeypatch) as client:
        response = client.post(
            "/api/v1/lookup",
            json={},
        )

    assert response.status_code == 422
