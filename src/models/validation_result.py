
from typing import Literal

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    status: Literal[
        "valid",
        "needs_clarification",
        "invalid",
    ]

    missing_fields: list[str] = Field(default_factory=list)
    clarification_reasons: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    suggested_question: str | None = None
