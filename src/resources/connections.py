"""
Connections resource for the Cognigy API (v2.0 /connections).

Provides synchronous and asynchronous resource classes for managing
Cognigy Connections, their fields, batch operations, and Connection schemas.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, List, Optional, Sequence, Union

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient

from ..exceptions import CognigyValidationError
from ..models.connection import (
    Connection,
    ConnectionBatchCreateOp,
    ConnectionBatchDeleteOp,
    ConnectionBatchOperation,
    ConnectionBatchRequest,
    ConnectionBatchResult,
    ConnectionBatchUpdateOp,
    ConnectionCreate,
    ConnectionFieldCreate,
    ConnectionListItem,
    ConnectionSchemaItem,
    ConnectionUpdate,
    ResourceLevel,
)
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data


OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")


def _require_object_id(value: str, field_name: str) -> None:
    if not OBJECT_ID_PATTERN.match(value):
        raise CognigyValidationError(
            f"{field_name} must be a 24-character lowercase hex ObjectId, "
            f"got {value!r}."
        )


def _resource_level_value(
    resource_level: Optional[Union[str, ResourceLevel]],
) -> Optional[str]:
    if resource_level is None:
        return None
    if isinstance(resource_level, ResourceLevel):
        return resource_level.value
    if isinstance(resource_level, str):
        try:
            return ResourceLevel(resource_level).value
        except ValueError as exc:
            raise CognigyValidationError(
                f"Invalid resource_level {resource_level!r}. "
                f"Expected one of: {[e.value for e in ResourceLevel]}."
            ) from exc
    raise CognigyValidationError(
        "resource_level must be a str or ResourceLevel enum."
    )


class ConnectionsResource:
    """Synchronous resource for Cognigy Connections."""

    def __init__(self, client: CognigyClient) -> None:
        self._client = client

    def list(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        resource_level: Optional[Union[str, ResourceLevel]] = None,
        **kwargs: Any,
    ) -> List[ConnectionListItem]:
        """List Connections with optional filtering and pagination."""
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        extra = {}
        if project_id is not None:
            extra["projectId"] = project_id
        rl = _resource_level_value(resource_level)
        if rl is not None:
            extra["resourceLevel"] = rl

        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra=extra or None,
        )

        def make_request(p):
            return self._client._request("GET", "/v2.0/connections", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [ConnectionListItem(**item) for item in items]

    def create(self, data: ConnectionCreate, **kwargs: Any) -> Connection:
        """Create a new Connection in a Project or at organisation level."""
        data = validate_create_update_data(data, ConnectionCreate)
        if data.project_id is None and data.resource_level != ResourceLevel.ORGANISATION:
            raise CognigyValidationError(
                "Either project_id or resource_level=ResourceLevel.ORGANISATION "
                "must be provided."
            )
        response = self._client._request("POST", "/v2.0/connections", data=data, **kwargs)
        return Connection(**response)

    def get(self, connection_id: str, **kwargs: Any) -> Connection:
        """Get a single Connection by id."""
        _require_object_id(connection_id, "connection_id")
        response = self._client._request(
            "GET", f"/v2.0/connections/{connection_id}", **kwargs
        )
        return Connection(**response)

    def update(
        self,
        connection_id: str,
        data: ConnectionUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Connection]:
        """Update a Connection's fields (PATCH)."""
        _require_object_id(connection_id, "connection_id")
        data = validate_create_update_data(data, ConnectionUpdate)
        response = self._client._request(
            "PATCH", f"/v2.0/connections/{connection_id}", data=data, **kwargs
        )
        if response is None:
            if fetch_updated:
                return self.get(connection_id, **kwargs)
            return None
        return Connection(**response)

    def delete(self, connection_id: str, **kwargs: Any) -> None:
        """Delete a Connection."""
        _require_object_id(connection_id, "connection_id")
        self._client._request(
            "DELETE", f"/v2.0/connections/{connection_id}", **kwargs
        )

    def batch(
        self,
        operations: Sequence[
            Union[
                ConnectionBatchCreateOp,
                ConnectionBatchUpdateOp,
                ConnectionBatchDeleteOp,
                ConnectionBatchOperation,
            ]
        ],
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ConnectionBatchResult:
        """
        Perform batch create/update/delete operations on Connections.

        PATCH /v2.0/connections
        """
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        request = validate_create_update_data(
            {"operations": list(operations)}, ConnectionBatchRequest
        )
        params = {"projectId": project_id} if project_id else None
        response = self._client._request(
            "PATCH",
            "/v2.0/connections",
            data=request,
            params=params,
            **kwargs,
        )
        return ConnectionBatchResult(**(response or {}))

    def create_field(
        self,
        connection_id: str,
        data: Optional[ConnectionFieldCreate] = None,
        *,
        key: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Create (or add) a Connection field.

        POST /v2.0/connections/{connectionId}/fields

        Call with either ``data=ConnectionFieldCreate(...)`` or the
        ``key``/``value`` keyword arguments.
        """
        _require_object_id(connection_id, "connection_id")
        if data is None:
            if key is None or value is None:
                raise CognigyValidationError(
                    "Provide either ``data`` or both ``key`` and ``value``."
                )
            data = ConnectionFieldCreate(key=key, value=value)
        data = validate_create_update_data(data, ConnectionFieldCreate)
        self._client._request(
            "POST",
            f"/v2.0/connections/{connection_id}/fields",
            data=data,
            **kwargs,
        )

    def delete_field(
        self, connection_id: str, field_name: str, **kwargs: Any
    ) -> None:
        """
        Delete a Connection field.

        DELETE /v2.0/connections/{connectionId}/fields/{fieldName}
        """
        _require_object_id(connection_id, "connection_id")
        if not field_name:
            raise CognigyValidationError("field_name must be a non-empty string.")
        self._client._request(
            "DELETE",
            f"/v2.0/connections/{connection_id}/fields/{field_name}",
            **kwargs,
        )

    def list_schemas(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[ConnectionSchemaItem]:
        """
        List Connection schemas.

        GET /v2.0/connections/schemas
        """
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={"projectId": project_id} if project_id else None,
        )

        def make_request(p):
            return self._client._request(
                "GET", "/v2.0/connections/schemas", params=p, **kwargs
            )

        items = paginate_sync(make_request, params, user_limit=limit)
        return [ConnectionSchemaItem(**item) for item in items]


class AsyncConnectionsResource:
    """Asynchronous resource for Cognigy Connections."""

    def __init__(self, client: AsyncCognigyClient) -> None:
        self._client = client

    async def list(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        resource_level: Optional[Union[str, ResourceLevel]] = None,
        **kwargs: Any,
    ) -> List[ConnectionListItem]:
        """List Connections with optional filtering and pagination."""
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        extra = {}
        if project_id is not None:
            extra["projectId"] = project_id
        rl = _resource_level_value(resource_level)
        if rl is not None:
            extra["resourceLevel"] = rl

        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra=extra or None,
        )

        async def make_request(p):
            return await self._client._request(
                "GET", "/v2.0/connections", params=p, **kwargs
            )

        items = await paginate_async(make_request, params, user_limit=limit)
        return [ConnectionListItem(**item) for item in items]

    async def create(self, data: ConnectionCreate, **kwargs: Any) -> Connection:
        """Create a new Connection."""
        data = validate_create_update_data(data, ConnectionCreate)
        if data.project_id is None and data.resource_level != ResourceLevel.ORGANISATION:
            raise CognigyValidationError(
                "Either project_id or resource_level=ResourceLevel.ORGANISATION "
                "must be provided."
            )
        response = await self._client._request(
            "POST", "/v2.0/connections", data=data, **kwargs
        )
        return Connection(**response)

    async def get(self, connection_id: str, **kwargs: Any) -> Connection:
        """Get a single Connection by id."""
        _require_object_id(connection_id, "connection_id")
        response = await self._client._request(
            "GET", f"/v2.0/connections/{connection_id}", **kwargs
        )
        return Connection(**response)

    async def update(
        self,
        connection_id: str,
        data: ConnectionUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Connection]:
        """Update a Connection's fields (PATCH)."""
        _require_object_id(connection_id, "connection_id")
        data = validate_create_update_data(data, ConnectionUpdate)
        response = await self._client._request(
            "PATCH", f"/v2.0/connections/{connection_id}", data=data, **kwargs
        )
        if response is None:
            if fetch_updated:
                return await self.get(connection_id, **kwargs)
            return None
        return Connection(**response)

    async def delete(self, connection_id: str, **kwargs: Any) -> None:
        """Delete a Connection."""
        _require_object_id(connection_id, "connection_id")
        await self._client._request(
            "DELETE", f"/v2.0/connections/{connection_id}", **kwargs
        )

    async def batch(
        self,
        operations: Sequence[
            Union[
                ConnectionBatchCreateOp,
                ConnectionBatchUpdateOp,
                ConnectionBatchDeleteOp,
                ConnectionBatchOperation,
            ]
        ],
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ConnectionBatchResult:
        """Perform batch create/update/delete operations on Connections."""
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        request = validate_create_update_data(
            {"operations": list(operations)}, ConnectionBatchRequest
        )
        params = {"projectId": project_id} if project_id else None
        response = await self._client._request(
            "PATCH",
            "/v2.0/connections",
            data=request,
            params=params,
            **kwargs,
        )
        return ConnectionBatchResult(**(response or {}))

    async def create_field(
        self,
        connection_id: str,
        data: Optional[ConnectionFieldCreate] = None,
        *,
        key: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Create (or add) a Connection field."""
        _require_object_id(connection_id, "connection_id")
        if data is None:
            if key is None or value is None:
                raise CognigyValidationError(
                    "Provide either ``data`` or both ``key`` and ``value``."
                )
            data = ConnectionFieldCreate(key=key, value=value)
        data = validate_create_update_data(data, ConnectionFieldCreate)
        await self._client._request(
            "POST",
            f"/v2.0/connections/{connection_id}/fields",
            data=data,
            **kwargs,
        )

    async def delete_field(
        self, connection_id: str, field_name: str, **kwargs: Any
    ) -> None:
        """Delete a Connection field."""
        _require_object_id(connection_id, "connection_id")
        if not field_name:
            raise CognigyValidationError("field_name must be a non-empty string.")
        await self._client._request(
            "DELETE",
            f"/v2.0/connections/{connection_id}/fields/{field_name}",
            **kwargs,
        )

    async def list_schemas(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[ConnectionSchemaItem]:
        """List Connection schemas."""
        if project_id is not None:
            _require_object_id(project_id, "project_id")
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={"projectId": project_id} if project_id else None,
        )

        async def make_request(p):
            return await self._client._request(
                "GET", "/v2.0/connections/schemas", params=p, **kwargs
            )

        items = await paginate_async(make_request, params, user_limit=limit)
        return [ConnectionSchemaItem(**item) for item in items]
