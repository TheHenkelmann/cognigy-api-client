"""Tests for CognigyClient configuration and request handling."""

from __future__ import annotations

import json

import httpx
import pytest

from cognigy import CognigyClient
from cognigy.exceptions import CognigyAPIError, CognigyConfigurationError
from cognigy.models.project import ProjectCreate

from conftest import BASE_URL, make_sync_client, sample_project


class TestCognigyClientConfiguration:
    def test_requires_api_key(self, monkeypatch):
        monkeypatch.delenv("COGNIGY_API_KEY", raising=False)
        with pytest.raises(CognigyConfigurationError, match="API Key is required"):
            CognigyClient()

    def test_accepts_api_key_argument(self):
        client = CognigyClient(api_key="my-key", base_url=BASE_URL)
        assert client.http_client.headers["X-API-Key"] == "my-key"
        client.close()

    def test_reads_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("COGNIGY_API_KEY", "env-key")
        client = CognigyClient(base_url=BASE_URL)
        assert client.http_client.headers["X-API-Key"] == "env-key"
        client.close()

    def test_default_base_url(self, monkeypatch):
        monkeypatch.setenv("COGNIGY_API_KEY", "key")
        monkeypatch.delenv("COGNIGY_BASE_URL", raising=False)
        client = CognigyClient()
        assert str(client.http_client.base_url).rstrip("/") == BASE_URL
        client.close()

    def test_custom_base_url_from_env(self, monkeypatch):
        monkeypatch.setenv("COGNIGY_API_KEY", "key")
        monkeypatch.setenv("COGNIGY_BASE_URL", "https://api-staging.cognigy.ai")
        client = CognigyClient()
        assert "api-staging" in str(client.http_client.base_url)
        client.close()

    def test_rejects_invalid_base_url(self):
        with pytest.raises(CognigyConfigurationError, match="Invalid base URL"):
            CognigyClient(api_key="key", base_url="https://app.cognigy.ai")

    def test_accepts_telekom_cloud_base_url(self):
        client = CognigyClient(
            api_key="key",
            base_url="https://api.live.ai.telekomcloud.com",
        )
        client.close()

    def test_context_manager_closes_client(self):
        with CognigyClient(api_key="key", base_url=BASE_URL) as client:
            assert client.http_client is not None
        assert client.http_client.is_closed

    def test_exposes_all_resources(self):
        with CognigyClient(api_key="key", base_url=BASE_URL) as client:
            for attr in (
                "projects", "flows", "nodes", "aiagents", "analytics",
                "conversations", "knowledge_stores", "knowledge_chunks",
                "knowledge_sources", "knowledge_connectors", "locales",
                "logs", "tasks", "search", "snapshots", "extensions",
                "functions", "llm", "connections",
            ):
                assert hasattr(client, attr), f"missing resource: {attr}"


class TestCognigyClientRequest:
    def test_serializes_pydantic_model_in_request_body(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json=sample_project())

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            client._request(
                "POST",
                "/v2.0/projects",
                data=ProjectCreate(name="New Project", color="blue"),
            )
        finally:
            client.close()

        assert captured["body"] == {"name": "New Project", "color": "blue"}

    def test_returns_none_for_204_response(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(204)

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            result = client._request("PATCH", "/v2.0/projects/abc")
        finally:
            client.close()

        assert result is None

    def test_raises_api_error_on_failure(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                401,
                json={"detail": "Invalid API key"},
                request=request,
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            with pytest.raises(CognigyAPIError) as exc_info:
                client._request("GET", "/v2.0/projects")
        finally:
            client.close()

        err = exc_info.value
        assert err.status_code == 401
        assert err.response_body == {"detail": "Invalid API key"}
        assert "Invalid API key" in str(err)

    def test_parses_json_response(self):
        payload = sample_project(name="Parsed")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=payload)

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            result = client._request("GET", f"/v2.0/projects/{payload['_id']}")
        finally:
            client.close()

        assert result == payload
