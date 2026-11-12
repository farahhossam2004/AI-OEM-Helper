
from typing import Literal

from pydantic import BaseModel, Field

from src.models.oem_part import OEMPart


class CatalogLookupResult(BaseModel):
    status: Literal[
        "found",
        "needs_clarification",
        "not_found",
        "unavailable",
        "quota_exceeded",
        "error",
    ]

    parts: list[OEMPart] = Field(default_factory=list)
    clarification_question: str | None = None
    details: str | None = None
    selected_modification_id: int | None = None
    selected_modification_name: str | None = None
