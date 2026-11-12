
import os
import time

from dotenv import load_dotenv
from groq import Groq

from src.llm.base import LLMProvider
from src.models.extracted_vehicle_request import ExtractedVehicleRequest

load_dotenv()



SYSTEM_PROMPT = """
You are an automotive parts identification assistant.

Understand Arabic, Egyptian colloquial Arabic, and English
automotive terminology.

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
2. If the user does not specify the position for these parts,
   set position to null and needs_clarification to true.
3. If the user specifies Front, Rear, or Both, use that value.
4. Do not ask for Front or Rear for Hubcaps by default.
5. For parts that do not require a position, use null
   and needs_clarification should be false unless
   other essential information is missing.

CLARIFICATION RULES:
1. Ask only for information that is genuinely required.
2. Do not ask unnecessary questions.
3. Ask in the same language used by the user.
4. If information is missing, use null where appropriate.

IMPORTANT:
- Never invent OEM part numbers.
- Return data matching the provided JSON schema.
"""



class GroqClient(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b",
        )

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing")

        self.client = Groq(
            api_key=api_key,
            timeout=30.0,
            max_retries=0,
        )

    def generate(self, prompt: str) -> str:
        start = time.perf_counter()

        print(f"Sending request to Groq ({self.model})...")

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_completion_tokens=512,
        )

        elapsed = time.perf_counter() - start
        print(f"Groq response received in {elapsed:.2f} seconds")

        content = completion.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty response")

        return content

    def extract_vehicle_request(
        self,
        user_text: str,
    ) -> ExtractedVehicleRequest:

        start = time.perf_counter()

        print(f"Extracting vehicle request using {self.model}...")

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
            temperature=0,
            max_completion_tokens=512,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extracted_vehicle_request",
                    "strict": True,
                    "schema": ExtractedVehicleRequest.model_json_schema(),
                },
            },
        )

        elapsed = time.perf_counter() - start
        print(f"Extraction completed in {elapsed:.2f} seconds")

        content = completion.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty structured response")

        return ExtractedVehicleRequest.model_validate_json(content)
