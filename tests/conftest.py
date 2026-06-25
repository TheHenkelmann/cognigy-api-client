"""Shared fixtures for Cognigy API client tests."""

from __future__ import annotations

import httpx
import pytest

from cognigy import AsyncCognigyClient, CognigyClient

BASE_URL = "https://api-app.cognigy.ai"
API_KEY = "test-api-key"
PROJECT_ID = "507f1f77bcf86cd799439011"
FLOW_ID = "607f1f77bcf86cd799439012"
AGENT_ID = "707f1f77bcf86cd799439013"
STORE_ID = "807f1f77bcf86cd799439014"
SEARCH_RESULT_ID = "907f1f77bcf86cd799439015"
CURSOR = "a" * 24


def sample_project(**overrides) -> dict:
    data = {
        "_id": PROJECT_ID,
        "name": "Test Project",
        "color": "blue",
    }
    data.update(overrides)
    return data


def sample_flow(**overrides) -> dict:
    data = {
        "_id": FLOW_ID,
        "name": "Test Flow",
        "projectId": PROJECT_ID,
    }
    data.update(overrides)
    return data


def sample_ai_agent(**overrides) -> dict:
    data = {
        "_id": AGENT_ID,
        "name": "Test Agent",
        "projectId": PROJECT_ID,
    }
    data.update(overrides)
    return data


def sample_knowledge_store(**overrides) -> dict:
    data = {
        "_id": STORE_ID,
        "name": "Test Knowledge Store",
        "projectId": PROJECT_ID,
    }
    data.update(overrides)
    return data


def sample_search_result(**overrides) -> dict:
    data = {
        "_id": SEARCH_RESULT_ID,
        "name": "Test Flow Result",
        "type": "flow",
        "projectId": PROJECT_ID,
    }
    data.update(overrides)
    return data


def make_sync_client(handler: httpx.MockTransport) -> CognigyClient:
    client = CognigyClient(api_key=API_KEY, base_url=BASE_URL)
    client.http_client = httpx.Client(
        base_url=BASE_URL,
        headers={"X-API-Key": API_KEY, "Accept": "application/json"},
        transport=handler,
    )
    return client


def make_async_client(handler: httpx.MockTransport) -> AsyncCognigyClient:
    client = AsyncCognigyClient(api_key=API_KEY, base_url=BASE_URL)
    client.http_client = httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"X-API-Key": API_KEY, "Accept": "application/json"},
        transport=handler,
    )
    return client


@pytest.fixture
def project_json():
    return sample_project()
