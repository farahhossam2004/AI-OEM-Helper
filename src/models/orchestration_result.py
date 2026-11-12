
from typing import Literal

from pydantic import BaseModel

from src.models.catalog_lookup_result import CatalogLookupResult
from src.models.extracted_vehicle_request import ExtractedVehicleRequest
from src.models.validation_result import ValidationResult


class OrchestrationResult(BaseModel):
    status: Literal[
        "invalid",
        "needs_clarification",
        "ready_for_catalog",
        "found",
        "not_found",
        "unavailable",
        "quota_exceeded",
        "error",
    ]

    extracted_request: ExtractedVehicleRequest
    validation: ValidationResult
    catalog_result: CatalogLookupResult | None = None
    response: str
