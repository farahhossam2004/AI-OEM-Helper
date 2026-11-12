
import os

from dotenv import load_dotenv

from src.llm.base import LLMProvider
from src.llm.gemini_client import GeminiClient
from src.llm.groq_client import GroqClient

load_dotenv()


def get_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        return GroqClient()

    if provider == "gemini":
        return GeminiClient()

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )
