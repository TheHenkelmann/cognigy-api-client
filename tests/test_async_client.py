"""Tests for AsyncCognigyClient configuration and request handling."""

from __future__ import annotations

import httpx
import pytest

from cognigy import AsyncCognigyClient
from cognigy.exceptions import CognigyAPIError, CognigyConfigurationError

from conftest import BASE_URL, make_async_client, sample_project


class TestAsyncCognigyClientConfiguration:
    def test_requires_api_key(self, monkeypatch):
        monkeypatch.delenv("COGNIGY_API_KEY", raising=False)
        with pytest.raises(CognigyConfigurationError, match="API Key is required"):
            AsyncCognigyClient()

    async def test_context_manager_closes_client(self):
        async with AsyncCognigyClient(api_key="key", base_url=BASE_URL) as client:
            assert client.http_client is not None
        assert client.http_client.is_closed

    def test_rejects_invalid_base_url(self):
        with pytest.raises(CognigyConfigurationError, match="Invalid base URL"):
            AsyncCognigyClient(api_key="key", base_url="https://app.cognigy.ai")


class TestAsyncCognigyClientRequest:
    async def test_returns_none_for_204_response(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(204)

        client = make_async_client(httpx.MockTransport(handler))
        try:
            result = await client._request("PATCH", "/v2.0/projects/abc")
        finally:
            await client.close()

        assert result is None

    async def test_raises_api_error_on_failure(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                404,
                json={"detail": "Not found"},
                request=request,
            )

        client = make_async_client(httpx.MockTransport(handler))
        try:
            with pytest.raises(CognigyAPIError) as exc_info:
                await client._request("GET", "/v2.0/projects/missing")
        finally:
            await client.close()

        assert exc_info.value.status_code == 404

    async def test_parses_json_response(self):
        payload = sample_project()

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=payload)

        client = make_async_client(httpx.MockTransport(handler))
        try:
            result = await client._request("GET", "/v2.0/projects")
        finally:
            await client.close()

        assert result == payload
