
from datetime import datetime, timezone, timedelta
from typing import Any

from pydantic import BaseModel
from typing import Literal
from pydantic import Field


class VehicleModification(BaseModel):
    modification_id: int
    name: str
    full_name: str | None = None
    production_start: str | None = None
    production_end: str | None = None
    engine_details: list[Any] = Field(default_factory=list)


class ModificationResolution(BaseModel):
    status: Literal["resolved", "needs_clarification", "not_found"]
    modifications: list[VehicleModification]
    selected_modification: VehicleModification | None = None
    clarification_question: str | None = None


class ModificationService:

    MOSCOW_TIMEZONE = timezone(timedelta(hours=3))

    @classmethod
    def _get_year(cls, timestamp: int | None) -> int | None:
        if not timestamp:
            return None

        return datetime.fromtimestamp(
            timestamp / 1000,
            tz=cls.MOSCOW_TIMEZONE,
        ).year

    @classmethod
    def _format_date(cls, timestamp: int | None) -> str | None:
        if not timestamp:
            return None

        return datetime.fromtimestamp(
            timestamp / 1000,
            tz=cls.MOSCOW_TIMEZONE,
        ).strftime("%Y-%m")

    def resolve(
        self,
        response_data: dict[str, Any],
        requested_year: int,
    ) -> ModificationResolution:

        raw_modifications = response_data.get("m", [])
        matches = []

        for item in raw_modifications:
            start_year = self._get_year(item.get("cb"))
            end_year = self._get_year(item.get("ce"))

            if start_year is None:
                continue

            if start_year <= requested_year and (
                end_year is None or requested_year <= end_year
            ):
                matches.append(
                    VehicleModification(
                        modification_id=item["dbi"],
                        name=item.get("d", "Unknown"),
                        full_name=item.get("fd"),
                        production_start=self._format_date(item.get("cb")),
                        production_end=self._format_date(item.get("ce")),
                        engine_details=item.get("p", {}).get("p", []),
                    )
                )

        if not matches:
            return ModificationResolution(
                status="not_found",
                modifications=[],
            )

        if len(matches) == 1:
            return ModificationResolution(
                status="resolved",
                modifications=matches,
                selected_modification=matches[0],
            )

        return ModificationResolution(
            status="needs_clarification",
            modifications=matches,
            clarification_question=(
                "More than one vehicle modification matches this year. "
                "Please specify the engine, trim, or drivetrain."
            ),
        )
