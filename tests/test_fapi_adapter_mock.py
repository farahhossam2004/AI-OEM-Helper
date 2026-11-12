
import httpx
import pytest

from src.integrations import fapi_adapter
from src.integrations.fapi_adapter import (
    FAPIAdapter,
    FAPIQuotaError,
    FAPIUnavailableError,
)


def create_adapter(handler):
    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    return FAPIAdapter(
        api_key="local-test-key",
        client=client,
        max_retries=2,
    )


def test_successful_response():
    def handler(request):
        return httpx.Response(
            200,
            json={"manufacturers": [{"id": 111, "name": "Toyota"}]},
        )

    adapter = create_adapter(handler)

    try:
        result = adapter.get_manufacturers()
        assert result["manufacturers"][0]["name"] == "Toyota"
    finally:
        adapter.close()


def test_402_does_not_retry(monkeypatch):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(402, json={"error": "Payment Required"})

    monkeypatch.setattr(fapi_adapter.time, "sleep", lambda _: None)

    adapter = create_adapter(handler)

    try:
        with pytest.raises(FAPIQuotaError):
            adapter.get_manufacturers()

        assert attempts == 1
    finally:
        adapter.close()


def test_5xx_retries_twice(monkeypatch):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(503, json={"error": "Unavailable"})

    monkeypatch.setattr(fapi_adapter.time, "sleep", lambda _: None)

    adapter = create_adapter(handler)

    try:
        with pytest.raises(FAPIUnavailableError):
            adapter.get_manufacturers()

        assert attempts == 3
    finally:
        adapter.close()
