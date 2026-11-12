
from src.models.catalog_lookup_result import CatalogLookupResult
from src.models.extracted_vehicle_request import ExtractedVehicleRequest
from src.models.oem_part import OEMPart
from src.services.orchestrator import Orchestrator
from src.services.response_builder import ResponseBuilder
from src.services.validation_service import ValidationService


class FakeLLM:

    def __init__(self, request):
        self.request = request

    def extract_vehicle_request(self, user_text):
        return self.request

    def generate(self, prompt):
        return ""


class FakeCatalogLookup:

    def __init__(self, result):
        self.result = result
        self.called = False

    def lookup(self, request):
        self.called = True
        return self.result


def create_request(position="front", year=2026):
    return ExtractedVehicleRequest(
        make="Toyota",
        model="Camry",
        year=year,
        part_name="Brake Discs",
        position=position,
        needs_clarification=False,
        clarification_question=None,
    )


def create_orchestrator(request, catalog_result):
    fake_llm = FakeLLM(request)
    fake_catalog = FakeCatalogLookup(catalog_result)

    orchestrator = Orchestrator(
        llm_provider=fake_llm,
        validation_service=ValidationService(),
        response_builder=ResponseBuilder(),
        catalog_lookup_service=fake_catalog,
    )

    return orchestrator, fake_catalog


def test_complete_workflow_returns_oem_result():

    catalog_result = CatalogLookupResult(
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

    orchestrator, fake_catalog = create_orchestrator(
        create_request(),
        catalog_result,
    )

    result = orchestrator.process("Front brake discs for Toyota Camry 2026")

    assert fake_catalog.called is True
    assert result.status == "found"
    assert result.catalog_result is not None
    assert result.catalog_result.parts[0].oem_number == "4243178010"
    assert "4243178010" in result.response


def test_missing_position_stops_before_catalog_lookup():

    catalog_result = CatalogLookupResult(status="found")

    orchestrator, fake_catalog = create_orchestrator(
        create_request(position=None),
        catalog_result,
    )

    result = orchestrator.process("Brake discs for Toyota Camry 2026")

    assert result.status == "needs_clarification"
    assert fake_catalog.called is False
    assert "front" in result.response.lower()


def test_quota_error_reaches_user_response():

    catalog_result = CatalogLookupResult(
        status="quota_exceeded",
        details="Quota exceeded",
    )

    orchestrator, fake_catalog = create_orchestrator(
        create_request(),
        catalog_result,
    )

    result = orchestrator.process("Front brake discs for Toyota Camry 2026")

    assert fake_catalog.called is True
    assert result.status == "quota_exceeded"
    assert result.catalog_result.status == "quota_exceeded"
    assert "quota" in result.response.lower()


def test_missing_year_stops_before_catalog_lookup():

    catalog_result = CatalogLookupResult(status="found")

    orchestrator, fake_catalog = create_orchestrator(
        create_request(year=None),
        catalog_result,
    )

    result = orchestrator.process("Brake discs for Toyota Camry")

    assert result.status == "needs_clarification"
    assert fake_catalog.called is False
    assert "year" in result.response.lower()
