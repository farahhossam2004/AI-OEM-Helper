
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.schemas import LookupRequest
from src.integrations.fapi_adapter import FAPIAdapter
from src.llm.llm_factory import get_llm_provider
from src.models.orchestration_result import OrchestrationResult
from src.services.catalog_lookup_service import CatalogLookupService
from src.services.orchestrator import Orchestrator
from src.services.response_builder import ResponseBuilder
from src.services.validation_service import ValidationService


STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    fapi_adapter = None

    try:
        llm_provider = get_llm_provider()
        fapi_adapter = FAPIAdapter()

        catalog_lookup_service = CatalogLookupService(
            adapter=fapi_adapter
        )

        app.state.orchestrator = Orchestrator(
            llm_provider=llm_provider,
            validation_service=ValidationService(),
            response_builder=ResponseBuilder(),
            catalog_lookup_service=catalog_lookup_service,
        )

        yield

    finally:
        if fapi_adapter is not None:
            fapi_adapter.close()


app = FastAPI(
    title="AI OEM Helper API",
    description=(
        "An AI-powered assistant that helps automotive technicians "
        "find OEM part number candidates using vehicle information."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI OEM Helper",
    }


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(STATIC_DIR / "index.html")


@app.post(
    "/api/v1/lookup",
    response_model=OrchestrationResult,
)
def lookup_part(
    payload: LookupRequest,
    request: Request,
):
    try:
        orchestrator = request.app.state.orchestrator
        return orchestrator.process(payload.message)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the request.",
        ) from exc
