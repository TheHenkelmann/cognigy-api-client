"""Tests for list endpoint auto-pagination."""

from __future__ import annotations

from cognigy.pagination import paginate_async, paginate_sync
from conftest import CURSOR


def _make_item(index: int) -> dict:
    return {"_id": f"{index:024d}", "name": f"Item {index}"}


class TestPaginateSync:
    def test_fetches_single_page(self):
        def make_request(params):
            assert params["limit"] == 100
            return {"items": [_make_item(1)], "nextCursor": None}

        result = paginate_sync(make_request, {})
        assert len(result) == 1

    def test_respects_user_limit(self):
        pages = [
            {"items": [_make_item(i) for i in range(1, 76)], "nextCursor": CURSOR},
            {"items": [_make_item(i) for i in range(76, 151)], "nextCursor": None},
        ]
        call_count = 0

        def make_request(params):
            nonlocal call_count
            data = pages[call_count]
            call_count += 1
            return data

        result = paginate_sync(make_request, {}, user_limit=75)
        assert len(result) == 75
        assert call_count == 1

    def test_follows_next_cursor_and_drops_skip(self):
        seen_params: list[dict] = []
        full_page = [_make_item(i) for i in range(1, 101)]

        def make_request(params):
            seen_params.append(dict(params))
            if "next" not in params:
                return {"items": full_page, "nextCursor": CURSOR}
            return {"items": [_make_item(101)], "nextCursor": None}

        result = paginate_sync(make_request, {"skip": 10})
        assert len(result) == 101
        assert "skip" in seen_params[0]
        assert "skip" not in seen_params[1]
        assert seen_params[1]["next"] == CURSOR

    def test_stops_when_page_is_incomplete(self):
        def make_request(params):
            return {"items": [_make_item(1)], "nextCursor": CURSOR}

        result = paginate_sync(make_request, {})
        assert len(result) == 1

    def test_does_not_mutate_base_params(self):
        base_params = {"sort": "name", "next": CURSOR}

        def make_request(params):
            return {"items": [], "nextCursor": None}

        paginate_sync(make_request, base_params)
        assert base_params == {"sort": "name", "next": CURSOR}


class TestPaginateAsync:
    async def test_fetches_all_pages_without_limit(self):
        pages = [
            {"items": [_make_item(i) for i in range(1, 101)], "nextCursor": CURSOR},
            {"items": [_make_item(101)], "nextCursor": None},
        ]
        call_count = 0

        async def make_request(params):
            nonlocal call_count
            data = pages[call_count]
            call_count += 1
            return data

        result = await paginate_async(make_request, {})
        assert len(result) == 101
        assert call_count == 2

    async def test_respects_user_limit(self):
        async def make_request(params):
            limit = params["limit"]
            return {
                "items": [_make_item(i) for i in range(1, limit + 1)],
                "nextCursor": CURSOR,
            }

        result = await paginate_async(make_request, {}, user_limit=5)
        assert len(result) == 5
