
from abc import ABC, abstractmethod

from src.models.extracted_vehicle_request import ExtractedVehicleRequest


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text response from the given prompt."""
        raise NotImplementedError

    @abstractmethod
    def extract_vehicle_request(
        self,
        user_text: str,
    ) -> ExtractedVehicleRequest:
        """Extract structured vehicle and part information."""
        raise NotImplementedError
