"""Integration tests for the search resource with mocked HTTP."""

from __future__ import annotations

import httpx

from conftest import PROJECT_ID, SEARCH_RESULT_ID, make_sync_client, sample_search_result


class TestSearchResource:
    def test_search_with_query_and_project(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["params"] = dict(request.url.params)
            return httpx.Response(
                200,
                json={"items": [sample_search_result()], "nextCursor": None},
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            results = client.search.search(query="pizza", project_id=PROJECT_ID)
        finally:
            client.close()

        assert captured["params"]["filter"] == "pizza"
        assert captured["params"]["projectId"] == PROJECT_ID
        assert len(results) == 1

    def test_search_with_types_filter(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["types"] = request.url.params.get_list("type")
            return httpx.Response(
                200,
                json={"items": [sample_search_result()], "nextCursor": None},
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            client.search.search(types=["flow", "endpoint"])
        finally:
            client.close()

        assert captured["types"] == ["flow", "endpoint"]

    def test_search_returns_search_results(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"items": [sample_search_result()], "nextCursor": None},
            )

        client = make_sync_client(httpx.MockTransport(handler))
        try:
            results = client.search.search()
        finally:
            client.close()

        assert len(results) == 1
        assert results[0].id == SEARCH_RESULT_ID
        assert results[0].name == "Test Flow Result"
        assert results[0].type.value == "flow"
