
import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.llm.base import LLMProvider
from src.models.extracted_vehicle_request import ExtractedVehicleRequest

load_dotenv()


EXTRACTION_PROMPT = """
You are an automotive parts identification assistant.

Understand Arabic, Egyptian colloquial Arabic, and English.

TERMINOLOGY:
- "هوبات" means "Brake Discs" or "Brake Rotors".
- "طاسات" means "Hubcaps" or "Wheel Covers".
- "تيل فرامل" means "Brake Pads".

EXTRACTION RULES:
1. Extract make, model, year, and part name.
2. Normalize part names to standard English automotive terms.
3. Never confuse similar automotive parts.
4. Never invent missing vehicle information.

POSITION RULES:
1. Brake Discs and Brake Pads may require Front or Rear position.
2. If position is missing for these parts, set position to null
   and needs_clarification to true.
3. If the user specifies Front, Rear, or Both, use that value.
4. Do not ask for position for Hubcaps by default.

CLARIFICATION RULES:
1. Ask only for genuinely required information.
2. Ask in the same language used by the user.
3. Use null for missing information.
4. Never invent OEM part numbers.

Return ONLY valid JSON matching this schema:
{schema}
"""


class GeminiClient(LLMProvider):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=60000),
        )

    def generate(self, prompt: str) -> str:
        start = time.perf_counter()

        print(f"Sending request to Gemini ({self.model})...")

        interaction = self.client.interactions.create(
            model=self.model,
            input=prompt,
            store=False,
            generation_config={
                "thinking_level": "low",
                "max_output_tokens": 512,
            },
        )

        elapsed = time.perf_counter() - start
        print(f"Gemini response received in {elapsed:.2f} seconds")

        if not interaction.output_text:
            raise RuntimeError("Gemini returned an empty response")

        return interaction.output_text

    def extract_vehicle_request(
        self,
        user_text: str,
    ) -> ExtractedVehicleRequest:

        schema = json.dumps(
            ExtractedVehicleRequest.model_json_schema(),
            ensure_ascii=False,
        )

        prompt = (
            EXTRACTION_PROMPT.format(schema=schema)
            + "\n\nUser request:\n"
            + user_text
        )

        content = self.generate(prompt)

        try:
            return ExtractedVehicleRequest.model_validate_json(content)
        except Exception as exc:
            raise RuntimeError(
                "Gemini returned an invalid structured response"
            ) from exc
