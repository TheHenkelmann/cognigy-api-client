"""
Logs resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for accessing Cognigy LogEntries via the v2.0 API endpoints.

Note: LogEntries are read-only resources. Only list, get, and tail
operations are available - no create, update, or delete endpoints exist.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient
from ..models.log import LogEntry
from ..validation import build_list_params
from ..pagination import paginate_sync, paginate_async


class LogsResource:
    """
    Synchronous resource for accessing Cognigy LogEntries.
    
    Provides methods to list, retrieve, and tail log entries
    using the Cognigy v2.0 API. LogEntries are read-only resources
    that contain runtime information from Flow executions and system events.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the LogsResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list(
        self,
        project_id: str,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[LogEntry]:
        """
        List log entries for a project with optional pagination.
        
        Retrieves a list of log entries from the Cognigy API.
        Results can be paginated using cursor-based pagination.
        
        Args:
            project_id: The ObjectId of the project to retrieve logs from
                (24 hex characters). Required parameter.
            filter: Optional filter string for server-side log filtering.
            limit: Maximum number of log entries to return. If not specified,
                a default of 1 is used.
            skip: Number of log entries to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
                Obtained from a previous list response (24 hex characters).
            previous_cursor: Cursor for fetching the previous page of results.
                Obtained from a previous list response (24 hex characters).
        
        Returns:
            List of LogEntry objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                authorization, or server errors.
        
        Example:
            >>> logs = client.logs.list(project_id="507f1f77bcf86cd799439011")
            >>> for log in logs:
            ...     print(f"{log.timestamp}: {log.msg}")
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        endpoint = f"/v2.0/projects/{project_id}/logs"

        def make_request(p):
            return self._client._request("GET", endpoint, params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [LogEntry(**item) for item in items]

    def get(self, project_id: str, log_entry_id: str, **kwargs: Any) -> LogEntry:
        """
        Get a log entry by ID.
        
        Retrieves a single log entry by its ObjectId from the specified project.
        
        Args:
            project_id: The ObjectId of the project containing the log entry
                (24 hex characters).
            log_entry_id: The ObjectId of the log entry to retrieve
                (24 hex characters).
        
        Returns:
            The LogEntry object with all available fields including 'id',
            'timestamp', 'msg', 'meta', and 'trace_id'.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                authorization, the log entry not being found (404),
                or server errors.
        
        Example:
            >>> log = client.logs.get(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     log_entry_id="507f1f77bcf86cd799439012"
            ... )
            >>> print(f"Log message: {log.msg}")
        """
        data = self._client._request(
            "GET",
            f"/v2.0/projects/{project_id}/logs/{log_entry_id}",
            **kwargs,
        )
        return LogEntry(**data)

    def tail(
        self,
        project_id: str,
        limit: Optional[int] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[LogEntry]:
        """
        Get the latest log entries for a project.
        
        Retrieves the most recent log entries from the specified project.
        This endpoint is optimized for retrieving real-time log data
        and supports cursor-based pagination for continuous tailing.
        
        Args:
            project_id: The ObjectId of the project to retrieve logs from
                (24 hex characters). Required parameter.
            limit: Maximum number of log entries to return. If not specified,
                uses the API default.
            next_cursor: Cursor for fetching the next page of results.
                Obtained from a previous tail response (24 hex characters).
            previous_cursor: Cursor for fetching the previous page of results.
                Obtained from a previous tail response (24 hex characters).
        
        Returns:
            List of LogEntry objects containing the latest log entries.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                authorization, or server errors.
        
        Example:
            >>> # Get the 10 most recent log entries
            >>> recent_logs = client.logs.tail(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     limit=10
            ... )
            >>> for log in recent_logs:
            ...     print(f"[{log.timestamp}] {log.msg}")
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if next_cursor:
            params["next"] = next_cursor
        if previous_cursor:
            params["previous"] = previous_cursor

        data = self._client._request(
            "GET",
            f"/v2.0/projects/{project_id}/logs/tail",
            params=params if params else None,
            **kwargs,
        )
        return [LogEntry(**item) for item in data.get("items", [])]


class AsyncLogsResource:
    """
    Asynchronous resource for accessing Cognigy LogEntries.
    
    Provides async methods to list, retrieve, and tail log entries
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    LogEntries are read-only resources that contain runtime information
    from Flow executions and system events.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncLogsResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list(
        self,
        project_id: str,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[LogEntry]:
        """
        List log entries for a project with optional pagination.
        
        Retrieves a list of log entries from the Cognigy API asynchronously.
        Results can be paginated using cursor-based pagination.
        
        Args:
            project_id: The ObjectId of the project to retrieve logs from
                (24 hex characters). Required parameter.
            filter: Optional filter string for server-side log filtering.
            limit: Maximum number of log entries to return. If not specified,
                a default of 1 is used.
            skip: Number of log entries to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
                Obtained from a previous list response (24 hex characters).
            previous_cursor: Cursor for fetching the previous page of results.
                Obtained from a previous list response (24 hex characters).
        
        Returns:
            List of LogEntry objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                authorization, or server errors.
        
        Example:
            >>> logs = await client.logs.list(project_id="507f1f77bcf86cd799439011")
            >>> for log in logs:
            ...     print(f"{log.timestamp}: {log.msg}")
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        endpoint = f"/v2.0/projects/{project_id}/logs"

        async def make_request(p):
            return await self._client._request("GET", endpoint, params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [LogEntry(**item) for item in items]

    async def get(self, project_id: str, log_entry_id: str, **kwargs: Any) -> LogEntry:
        """
        Get a log entry by ID.
        
        Retrieves a single log entry by its ObjectId from the specified
        project asynchronously.
        
        Args:
            project_id: The ObjectId of the project containing the log entry
                (24 hex characters).
            log_entry_id: The ObjectId of the log entry to retrieve
                (24 hex characters).
        
        Returns:
            The LogEntry object with all available fields including 'id',
            'timestamp', 'msg', 'meta', and 'trace_id'.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                authorization, the log entry not being found (404),
                or server errors.
        
        Example:
            >>> log = await client.logs.get(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     log_entry_id="507f1f77bcf86cd799439012"
            ... )
            >>> print(f"Log message: {log.msg}")
        """
        data = await self._client._request(
            "GET",
            f"/v2.0/projects/{project_id}/logs/{log_entry_id}",
            **kwargs,
        )
        return LogEntry(**data)

    async def tail(
        self,
        project_id: str,
        limit: Optional[int] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[LogEntry]:
        """
        Get the latest log entries for a project.
        
        Retrieves the most recent log entries from the specified project
        asynchronously. This endpoint is optimized for retrieving real-time
        log data and supports cursor-based pagination for continuous tailing.
        
        Args:
            project_id: The ObjectId of the project to retrieve logs from
                (24 hex characters). Required parameter.
            limit: Maximum number of log entries to return. If not specified,
                uses the API default.
            next_cursor: Cursor for fetching the next page of results.
                Obtained from a previous tail response (24 hex characters).
            previous_cursor: Cursor for fetching the previous page of results.
                Obtained from a previous tail response (24 hex characters).
        
        Returns:
            List of LogEntry objects containing the latest log entries.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                authorization, or server errors.
        
        Example:
            >>> # Get the 10 most recent log entries
            >>> recent_logs = await client.logs.tail(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     limit=10
            ... )
            >>> for log in recent_logs:
            ...     print(f"[{log.timestamp}] {log.msg}")
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if next_cursor:
            params["next"] = next_cursor
        if previous_cursor:
            params["previous"] = previous_cursor

        data = await self._client._request(
            "GET",
            f"/v2.0/projects/{project_id}/logs/tail",
            params=params if params else None,
            **kwargs,
        )
        return [LogEntry(**item) for item in data.get("items", [])]
