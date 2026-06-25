"""
Auto-pagination helpers for list-style endpoints.

The Cognigy API enforces a server-side page limit of 100 items per request.
These helpers transparently fetch multiple pages so callers can request any
number of items (or all items) without worrying about the server cap.
"""

from __future__ import annotations

from typing import Any, Callable

_SERVER_PAGE_LIMIT = 100


def paginate_sync(
    make_request: Callable[[dict[str, Any]], dict[str, Any]],
    base_params: dict[str, Any],
    user_limit: int | None = None,
) -> list[dict[str, Any]]:
    """
    Auto-paginate a list endpoint (synchronous).

    Args:
        make_request: Callable that takes a params dict and returns the raw
            API response dict (must contain ``"items"`` and optionally
            ``"nextCursor"``).
        base_params: Query parameters **without** ``limit``.  The ``"next"``
            key, if present, is consumed as the initial cursor.
        user_limit: Maximum total items the caller wants.
            ``None`` means *fetch everything*.

    Returns:
        Flat list of raw item dicts collected across all pages.
    """
    all_items: list[dict[str, Any]] = []
    remaining = user_limit
    next_cursor: str | None = base_params.get("next")
    # Work on a copy so the caller's dict is never mutated.
    base_params = {k: v for k, v in base_params.items() if k != "next"}

    while True:
        # Determine how many items to request in this batch
        if remaining is not None:
            batch_size = min(remaining, _SERVER_PAGE_LIMIT)
            if batch_size <= 0:
                break
        else:
            batch_size = _SERVER_PAGE_LIMIT

        params = {**base_params, "limit": batch_size}
        if next_cursor:
            params["next"] = next_cursor
            # Cursor-based and offset-based pagination are mutually exclusive;
            # once we follow a cursor, skip must not be sent.
            params.pop("skip", None)

        data = make_request(params)
        items = data.get("items", [])
        all_items.extend(items)

        if remaining is not None:
            remaining -= len(items)

        next_cursor = data.get("nextCursor")
        if not next_cursor or len(items) < batch_size:
            break

    return all_items


async def paginate_async(
    make_request: Callable[[dict[str, Any]], Any],
    base_params: dict[str, Any],
    user_limit: int | None = None,
) -> list[dict[str, Any]]:
    """
    Auto-paginate a list endpoint (asynchronous).

    Same semantics as :func:`paginate_sync` but ``make_request`` is awaited.
    """
    all_items: list[dict[str, Any]] = []
    remaining = user_limit
    next_cursor: str | None = base_params.get("next")
    # Work on a copy so the caller's dict is never mutated.
    base_params = {k: v for k, v in base_params.items() if k != "next"}

    while True:
        if remaining is not None:
            batch_size = min(remaining, _SERVER_PAGE_LIMIT)
            if batch_size <= 0:
                break
        else:
            batch_size = _SERVER_PAGE_LIMIT

        params = {**base_params, "limit": batch_size}
        if next_cursor:
            params["next"] = next_cursor
            params.pop("skip", None)

        data = await make_request(params)
        items = data.get("items", [])
        all_items.extend(items)

        if remaining is not None:
            remaining -= len(items)

        next_cursor = data.get("nextCursor")
        if not next_cursor or len(items) < batch_size:
            break

    return all_items
