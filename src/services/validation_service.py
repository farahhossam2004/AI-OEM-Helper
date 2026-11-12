
from src.models.extracted_vehicle_request import ExtractedVehicleRequest
from src.models.validation_result import ValidationResult


class ValidationService:

    POSITION_REQUIRED_PARTS = {
        "brake discs",
        "brake rotors",
        "brake pads",
    }

    def validate(
        self,
        request: ExtractedVehicleRequest,
    ) -> ValidationResult:

        missing_fields = []
        clarification_reasons = []
        errors = []

        # Check required vehicle and part information.
        required_fields = {
            "make": request.make,
            "model": request.model,
            "year": request.year,
            "part_name": request.part_name,
        }

        for field, value in required_fields.items():
            if value is None or (
                isinstance(value, str) and not value.strip()
            ):
                missing_fields.append(field)

        # Check year validity.
        if request.year is not None and request.year <= 0:
            errors.append("invalid_year")

        # Check whether part position is required.
        if request.part_name:
            part_name = request.part_name.strip().lower()

            if (
                part_name in self.POSITION_REQUIRED_PARTS
                and request.position is None
            ):
                clarification_reasons.append(
                    "part_position_required"
                )

        # Preserve additional clarification detected by the LLM.
        if (
            request.needs_clarification
            and not clarification_reasons
        ):
            clarification_reasons.append(
                "llm_requested_clarification"
            )

        # Invalid input has priority.
        if errors:
            status = "invalid"

        elif missing_fields or clarification_reasons:
            status = "needs_clarification"

        else:
            status = "valid"

        return ValidationResult(
            status=status,
            missing_fields=missing_fields,
            clarification_reasons=clarification_reasons,
            errors=errors,
            suggested_question=(
                request.clarification_question
                if clarification_reasons
                else None
            ),
        )
