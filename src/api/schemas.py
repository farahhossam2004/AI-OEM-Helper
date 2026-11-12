
from pydantic import BaseModel, Field, field_validator


class LookupRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="Vehicle and requested part in Arabic or English",
        examples=["هوبات كامري 2026 أمامي"],
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty.")

        return value
