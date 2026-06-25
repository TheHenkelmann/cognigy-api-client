"""Integration tests for the knowledge stores resource with mocked HTTP."""

from __future__ import annotations

import json

import httpx

from cognigy.models.knowledge_store import KnowledgeStoreCreate
from conftest import (
    PROJECT_ID,
    STORE_ID,
    make_async_client,
    make_sync_client,
    sample_knowledge_store,
)


class TestKnowledgeStoresResource:
    def test_list_knowledge_stores_by_project(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["params"] = dict(request.url.params)
            return httpx.Response(
                200,
                json={"items": [sample_knowledge_store()], "nextCursor": None},
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            stores = client.knowledge_stores.list(project_id=PROJECT_ID)
        finally:
            client.close()

        assert captured["params"]["projectId"] == PROJECT_ID
        assert len(stores) == 1
        assert stores[0].id == STORE_ID

    def test_get_knowledge_store(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == f"/v2.0/knowledgestores/{STORE_ID}"
            return httpx.Response(200, json=sample_knowledge_store())

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            store = client.knowledge_stores.get(STORE_ID)
        finally:
            client.close()

        assert store.id == STORE_ID
        assert store.name == "Test Knowledge Store"

    def test_create_knowledge_store(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(201, json=sample_knowledge_store(name="Product Docs"))

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            store = client.knowledge_stores.create(
                KnowledgeStoreCreate(name="Product Docs", project_id=PROJECT_ID),
            )
        finally:
            client.close()

        assert captured["body"] == {"name": "Product Docs", "projectId": PROJECT_ID}
        assert store.name == "Product Docs"


class TestAsyncKnowledgeStoresResource:
    async def test_async_list_knowledge_stores(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"items": [sample_knowledge_store()], "nextCursor": None},
            )

        client = make_async_client(httpx.MockTransport(handler))
        try:
            stores = await client.knowledge_stores.list(project_id=PROJECT_ID)
        finally:
            await client.close()

        assert len(stores) == 1
        assert stores[0].id == STORE_ID
