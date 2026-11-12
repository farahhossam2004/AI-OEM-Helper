
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExtractedVehicleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    make: str | None = Field(min_length=1)
    model: str | None = Field(min_length=1)
    year: int | None
    part_name: str | None = Field(min_length=1)

    position: Literal["front", "rear", "both"] | None

    needs_clarification: bool
    clarification_question: str | None
