
import os
import time
from typing import Any

import httpx


class FAPIError(Exception):
    """Base exception for FAPI integration errors."""


class FAPIAuthenticationError(FAPIError):
    """Invalid or unauthorized API credentials."""


class FAPIQuotaError(FAPIError):
    """The API account has no available quota or plan."""


class FAPIRequestError(FAPIError):
    """The API rejected the request."""


class FAPIUnavailableError(FAPIError):
    """The API is temporarily unavailable."""


class FAPIAdapter:
    BASE_URL = "https://fapi.iisis.ru/fapi/v2"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 8.0,
        max_retries: int = 2,
        client: httpx.Client | None = None,
    ):
        self.api_key = api_key or os.getenv("FAPI_API_KEY")

        if not self.api_key:
            raise ValueError("FAPI_API_KEY is missing")

        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.max_retries = max(0, max_retries)

        self.client = client or httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            },
        )

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.get(url, params=params)

                if response.status_code == 402:
                    # Never retry quota or payment errors.
                    raise FAPIQuotaError(
                        "FAPI account quota or plan does not allow this request."
                    )

                if response.status_code in (401, 403):
                    raise FAPIAuthenticationError(
                        "FAPI authentication or permission failed."
                    )

                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        time.sleep(0.5 * (attempt + 1))
                        continue

                    raise FAPIUnavailableError(
                        f"FAPI server error: HTTP {response.status_code}"
                    )

                if not response.is_success:
                    raise FAPIRequestError(
                        f"FAPI request failed: HTTP {response.status_code}"
                    )

                try:
                    return response.json()
                except ValueError as exc:
                    raise FAPIRequestError(
                        "FAPI returned an invalid JSON response."
                    ) from exc

            except FAPIError:
                raise

            except httpx.RequestError as exc:
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue

                raise FAPIUnavailableError(
                    "Could not connect to FAPI after retrying."
                ) from exc

        raise FAPIUnavailableError("FAPI request failed.")

    def get_manufacturers(self) -> Any:
        return self._get("catalogList/dt/manufacturerList")

    def get_models(self, manufacturer_id: int) -> Any:
        return self._get(
            "catalogList/dt/modelList",
            params={"mfi": manufacturer_id},
        )

    def get_modifications(self, model_id: int) -> Any:
        return self._get(
            "catalogList/dt/modificationList",
            params={"mi": model_id},
        )

    def get_parts_tree(self, modification_id: int) -> Any:
        return self._get(
            "catalogList/dt/treeList",
            params={"mi": modification_id},
        )

    def get_oem_parts(
        self,
        modification_id: int,
        node_id: int,
        strict: bool = True,
    ) -> Any:
        return self._get(
            "catalogList/dt/productListOEM",
            params={
                "modi": modification_id,
                "nodei": node_id,
                "strict": int(strict),
            },
        )

    def close(self) -> None:
        self.client.close()
