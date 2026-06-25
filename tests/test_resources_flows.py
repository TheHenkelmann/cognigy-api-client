"""Integration tests for the flows resource with mocked HTTP."""

from __future__ import annotations

import json

import httpx

from cognigy.models.flow import FlowCreate
from conftest import FLOW_ID, PROJECT_ID, make_async_client, make_sync_client, sample_flow


class TestFlowsResource:
    def test_list_flows_with_project_filter(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["params"] = dict(request.url.params)
            return httpx.Response(
                200,
                json={"items": [sample_flow()], "nextCursor": None},
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            flows = client.flows.list(project_id=PROJECT_ID)
        finally:
            client.close()

        assert captured["params"]["projectId"] == PROJECT_ID
        assert len(flows) == 1
        assert flows[0].id == FLOW_ID

    def test_get_flow(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == f"/v2.0/flows/{FLOW_ID}"
            return httpx.Response(200, json=sample_flow())

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            flow = client.flows.get(FLOW_ID)
        finally:
            client.close()

        assert flow.id == FLOW_ID
        assert flow.name == "Test Flow"

    def test_create_flow_serializes_body(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            captured["body"] = json.loads(request.content)
            return httpx.Response(201, json=sample_flow(name="Created Flow"))

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            flow = client.flows.create(
                FlowCreate(name="Created Flow", project_id=PROJECT_ID),
            )
        finally:
            client.close()

        assert captured["method"] == "POST"
        assert captured["body"] == {"name": "Created Flow", "projectId": PROJECT_ID}
        assert flow.name == "Created Flow"

    def test_list_with_pagination(self):
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            return httpx.Response(
                200,
                json={
                    "items": [sample_flow(name=f"Flow {i}", _id=f"{i:024d}") for i in range(1, 3)],
                    "nextCursor": None,
                },
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            flows = client.flows.list(limit=2)
        finally:
            client.close()

        assert len(flows) == 2
        assert call_count == 1


class TestAsyncFlowsResource:
    async def test_async_list_flows(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"items": [sample_flow()], "nextCursor": None},
            )

        client = make_async_client(httpx.MockTransport(handler))
        try:
            flows = await client.flows.list(project_id=PROJECT_ID)
        finally:
            await client.close()

        assert len(flows) == 1
        assert flows[0].id == FLOW_ID
