"""Integration tests for the AI agents resource with mocked HTTP."""

from __future__ import annotations

import json

import httpx

from cognigy.models.aiagent import AIAgentCreate
from conftest import AGENT_ID, PROJECT_ID, make_async_client, make_sync_client, sample_ai_agent


class TestAIAgentsResource:
    def test_list_ai_agents(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v2.0/aiagents"
            return httpx.Response(
                200,
                json={"items": [sample_ai_agent()], "nextCursor": None},
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            agents = client.aiagents.list()
        finally:
            client.close()

        assert len(agents) == 1
        assert agents[0].id == AGENT_ID

    def test_get_ai_agent(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == f"/v2.0/aiagents/{AGENT_ID}"
            return httpx.Response(200, json=sample_ai_agent())

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            agent = client.aiagents.get(AGENT_ID)
        finally:
            client.close()

        assert agent.id == AGENT_ID
        assert agent.name == "Test Agent"

    def test_create_ai_agent(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return httpx.Response(201, json=sample_ai_agent(name="Support Agent"))

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            agent = client.aiagents.create(
                AIAgentCreate(name="Support Agent", project_id=PROJECT_ID),
            )
        finally:
            client.close()

        assert captured["body"] == {"name": "Support Agent", "projectId": PROJECT_ID}
        assert agent.name == "Support Agent"

    def test_validate_name_posts_correct_payload(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            captured["path"] = request.url.path
            captured["body"] = json.loads(request.content)
            return httpx.Response(204)

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            client.aiagents.validate_name("My Agent", PROJECT_ID)
        finally:
            client.close()

        assert captured == {
            "method": "POST",
            "path": "/v2.0/aiagents/validatename",
            "body": {"name": "My Agent", "projectId": PROJECT_ID},
        }

    def test_get_jobs(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == f"/v2.0/aiagents/{AGENT_ID}/jobs"
            return httpx.Response(
                200,
                json=[
                    {
                        "_id": "a" * 24,
                        "label": "Support",
                        "tools": [],
                    }
                ],
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            jobs = client.aiagents.get_jobs(AGENT_ID)
        finally:
            client.close()

        assert len(jobs) == 1
        assert jobs[0].label == "Support"


class TestAsyncAIAgentsResource:
    async def test_async_create_ai_agent(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(201, json=sample_ai_agent(name="Async Agent"))

        client = make_async_client(httpx.MockTransport(handler))
        try:
            agent = await client.aiagents.create(
                AIAgentCreate(name="Async Agent", project_id=PROJECT_ID),
            )
        finally:
            await client.close()

        assert agent.name == "Async Agent"
