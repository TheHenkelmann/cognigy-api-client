"""Integration tests for the projects resource with mocked HTTP."""

from __future__ import annotations

import json

import httpx

from cognigy.models.project import ProjectCreate, ProjectUpdate

from conftest import CURSOR, PROJECT_ID, make_async_client, make_sync_client, sample_project


class TestProjectsResource:
    def test_list_projects(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v2.0/projects"
            return httpx.Response(
                200,
                json={"items": [sample_project()], "nextCursor": None},
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            projects = client.projects.list()
        finally:
            client.close()

        assert len(projects) == 1
        assert projects[0].id == PROJECT_ID
        assert projects[0].name == "Test Project"

    def test_get_project(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == f"/v2.0/projects/{PROJECT_ID}"
            return httpx.Response(200, json=sample_project())

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            project = client.projects.get(PROJECT_ID)
        finally:
            client.close()

        assert project.id == PROJECT_ID

    def test_create_project(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            captured["body"] = json.loads(request.content)
            return httpx.Response(201, json=sample_project(name="Created"))

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            project = client.projects.create(ProjectCreate(name="Created", color="blue"))
        finally:
            client.close()

        assert captured["method"] == "POST"
        assert captured["body"] == {"name": "Created", "color": "blue"}
        assert project.name == "Created"

    def test_update_project_fetches_when_api_returns_no_body(self):
        requests: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append((request.method, request.url.path))
            if request.method == "PATCH":
                return httpx.Response(204)
            return httpx.Response(200, json=sample_project(name="Updated"))

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            project = client.projects.update(
                PROJECT_ID,
                ProjectUpdate(name="Updated"),
            )
        finally:
            client.close()

        assert requests == [
            ("PATCH", f"/v2.0/projects/{PROJECT_ID}"),
            ("GET", f"/v2.0/projects/{PROJECT_ID}"),
        ]
        assert project is not None
        assert project.name == "Updated"

    def test_update_project_returns_none_when_fetch_disabled(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(204)

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            project = client.projects.update(
                PROJECT_ID,
                ProjectUpdate(name="Updated"),
                fetch_updated=False,
            )
        finally:
            client.close()

        assert project is None

    def test_delete_project(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            captured["path"] = request.url.path
            return httpx.Response(204)

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            client.projects.delete(PROJECT_ID)
        finally:
            client.close()

        assert captured == {
            "method": "DELETE",
            "path": f"/v2.0/projects/{PROJECT_ID}",
        }

    def test_list_with_pagination(self):
        pages = [
            {
                "items": [
                    sample_project(name=f"Page 1 #{i}", _id=f"{i:024d}")
                    for i in range(1, 3)
                ],
                "nextCursor": None,
            },
        ]
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            data = pages[call_count]
            call_count += 1
            return httpx.Response(200, json=data)

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            projects = client.projects.list(limit=2)
        finally:
            client.close()

        assert len(projects) == 2
        assert call_count == 1


class TestAsyncProjectsResource:
    async def test_list_projects(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"items": [sample_project()], "nextCursor": None},
            )

        client = make_async_client(httpx.MockTransport(handler))
        try:
            projects = await client.projects.list()
        finally:
            await client.close()

        assert len(projects) == 1
        assert projects[0].id == PROJECT_ID

    async def test_create_project(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(201, json=sample_project(name="Async Created"))

        client = make_async_client(httpx.MockTransport(handler))
        try:
            project = await client.projects.create(ProjectCreate(name="Async Created"))
        finally:
            await client.close()

        assert project.name == "Async Created"
