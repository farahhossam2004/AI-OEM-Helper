
from src.integrations.fapi_adapter import FAPIAdapter
from src.llm.llm_factory import get_llm_provider
from src.services.catalog_lookup_service import CatalogLookupService
from src.services.orchestrator import Orchestrator
from src.services.response_builder import ResponseBuilder
from src.services.validation_service import ValidationService


def main():
    llm_provider = get_llm_provider()
    validation_service = ValidationService()
    response_builder = ResponseBuilder()

    fapi_adapter = FAPIAdapter()

    catalog_lookup_service = CatalogLookupService(
        adapter=fapi_adapter
    )

    orchestrator = Orchestrator(
        llm_provider=llm_provider,
        validation_service=validation_service,
        response_builder=response_builder,
        catalog_lookup_service=catalog_lookup_service,
    )

    try:
        user_text = input("Enter vehicle request: ")

        result = orchestrator.process(user_text)

        print("\nAssistant Response:")
        print(result.response)

        print("\nDebug Information:")
        print(result.model_dump_json(indent=2))

    finally:
        fapi_adapter.close()


if __name__ == "__main__":
    main()
