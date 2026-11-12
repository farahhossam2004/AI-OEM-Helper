
from src.llm.base import LLMProvider
from src.models.orchestration_result import OrchestrationResult
from src.services.catalog_lookup_service import CatalogLookupService
from src.services.response_builder import ResponseBuilder
from src.services.validation_service import ValidationService


class Orchestrator:

    def __init__(
        self,
        llm_provider: LLMProvider,
        validation_service: ValidationService,
        response_builder: ResponseBuilder,
        catalog_lookup_service: CatalogLookupService | None = None,
    ):
        self.llm_provider = llm_provider
        self.validation_service = validation_service
        self.response_builder = response_builder
        self.catalog_lookup_service = catalog_lookup_service

    def process(self, user_text: str) -> OrchestrationResult:

        # 1. Extract vehicle and part information.
        extracted_request = self.llm_provider.extract_vehicle_request(
            user_text
        )

        # 2. Validate extracted information.
        validation_result = self.validation_service.validate(
            extracted_request
        )

        catalog_result = None

        if validation_result.status == "invalid":
            status = "invalid"

        elif validation_result.status == "needs_clarification":
            status = "needs_clarification"

        elif self.catalog_lookup_service is None:
            status = "ready_for_catalog"

        else:
            # 3. Search the external catalog.
            catalog_result = self.catalog_lookup_service.lookup(
                extracted_request
            )

            status = catalog_result.status

        # 4. Build the final user-facing response.
        result = OrchestrationResult(
            status=status,
            extracted_request=extracted_request,
            validation=validation_result,
            catalog_result=catalog_result,
            response="",
        )

        response = self.response_builder.build(
            user_text,
            result,
        )

        return result.model_copy(update={"response": response})
