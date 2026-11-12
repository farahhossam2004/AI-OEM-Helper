
from typing import Literal

from pydantic import BaseModel, ConfigDict


class OEMPart(BaseModel):
    model_config = ConfigDict(extra="ignore")

    oem_number: str
    description: str | None = None
    manufacturer_id: int | None = None
    manufacturer_name: str | None = None
    namespace: str | None = None
    sources: int | None = None

    verification_status: Literal[
        "catalog_candidate",
        "compatibility_confirmed",
        "unverified",
    ] = "catalog_candidate"
