"""
Search resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for performing global searches via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient

from ..models.search import SearchResult
from ..pagination import paginate_sync, paginate_async


class SearchResource:
    """
    Synchronous resource for performing global searches in Cognigy.
    
    Provides methods to search across multiple resource types using
    the Cognigy v2.0 global search API. This is a read-only resource
    that only supports listing/searching.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the SearchResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def search(
        self,
        query: Optional[str] = None,
        project_id: Optional[str] = None,
        types: Optional[List[str]] = None,
        limit: Optional[int] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[SearchResult]:
        """
        Perform a global search across Cognigy resources.
        
        Searches for resources matching the specified criteria across multiple
        resource types including flows, endpoints, projects, extensions, 
        functions, lexicons, goals, handover providers, NLU connectors, 
        playbooks, and snapshots.
        
        Args:
            query: Search query string to filter resources by name.
                   If not specified, returns all accessible resources.
            project_id: Filter results by project ObjectId (24 hex characters).
                        If specified, only returns resources within that project.
            types: List of resource types to include in search results.
                   Valid values: 'endpoint', 'extension', 'flow', 'function',
                   'lexicon', 'goal', 'handoverProvider', 'nluconnector',
                   'playbook', 'project', 'snapshot'.
                   If not specified, searches all types.
            limit: Maximum number of results to return.
                   If not specified, uses the API default.
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous search response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous search response.
        
        Returns:
            List of SearchResult objects matching the query parameters.
            Each result contains the resource's id, name, type, optional
            subtype, project_id, and last_changed timestamp.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> # Search for all flows
            >>> results = client.search.search(types=["flow"])
            >>> for result in results:
            ...     print(f"{result.name} ({result.type})")
            
            >>> # Search by query in a specific project
            >>> results = client.search.search(
            ...     query="pizza",
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
        """
        params = {}
        if query:
            params["filter"] = query
        if project_id:
            params["projectId"] = project_id
        if types:
            params["type"] = types
        if next_cursor:
            params["next"] = next_cursor
        if previous_cursor:
            params["previous"] = previous_cursor

        def make_request(p):
            return self._client._request("GET", "/v2.0/search", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [SearchResult(**item) for item in items]

    def list(
        self,
        query: Optional[str] = None,
        filter: Optional[str] = None,
        project_id: Optional[str] = None,
        types: Optional[List[str]] = None,
        limit: Optional[int] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[SearchResult]:
        """
        Alias for search() method.
        
        Provided for consistency with other resource classes that use 'list'
        as the primary method name for retrieving multiple items.
        
        Args:
            query: Search query string to filter resources by name.
            filter: Alias for `query` to align with other list methods.
            project_id: Filter results by project ObjectId (24 hex characters).
            types: List of resource types to include in search results.
            limit: Maximum number of results to return.
            next_cursor: Cursor for fetching the next page of results.
            previous_cursor: Cursor for fetching the previous page of results.
        
        Returns:
            List of SearchResult objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails.
        
        See Also:
            search: The primary search method with full documentation.
        """
        effective_query = filter if filter is not None else query
        return self.search(
            query=effective_query,
            project_id=project_id,
            types=types,
            limit=limit,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            **kwargs,
        )


class AsyncSearchResource:
    """
    Asynchronous resource for performing global searches in Cognigy.
    
    Provides async methods to search across multiple resource types using
    the Cognigy v2.0 global search API. This is a read-only resource
    that only supports listing/searching. Use this class with 
    AsyncCognigyClient for non-blocking API operations.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncSearchResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def search(
        self,
        query: Optional[str] = None,
        project_id: Optional[str] = None,
        types: Optional[List[str]] = None,
        limit: Optional[int] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[SearchResult]:
        """
        Perform a global search across Cognigy resources asynchronously.
        
        Searches for resources matching the specified criteria across multiple
        resource types including flows, endpoints, projects, extensions, 
        functions, lexicons, goals, handover providers, NLU connectors, 
        playbooks, and snapshots.
        
        Args:
            query: Search query string to filter resources by name.
                   If not specified, returns all accessible resources.
            project_id: Filter results by project ObjectId (24 hex characters).
                        If specified, only returns resources within that project.
            types: List of resource types to include in search results.
                   Valid values: 'endpoint', 'extension', 'flow', 'function',
                   'lexicon', 'goal', 'handoverProvider', 'nluconnector',
                   'playbook', 'project', 'snapshot'.
                   If not specified, searches all types.
            limit: Maximum number of results to return.
                   If not specified, uses the API default.
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous search response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous search response.
        
        Returns:
            List of SearchResult objects matching the query parameters.
            Each result contains the resource's id, name, type, optional
            subtype, project_id, and last_changed timestamp.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> # Search for all flows
            >>> results = await client.search.search(types=["flow"])
            >>> for result in results:
            ...     print(f"{result.name} ({result.type})")
            
            >>> # Search by query in a specific project
            >>> results = await client.search.search(
            ...     query="pizza",
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
        """
        params = {}
        if query:
            params["filter"] = query
        if project_id:
            params["projectId"] = project_id
        if types:
            params["type"] = types
        if next_cursor:
            params["next"] = next_cursor
        if previous_cursor:
            params["previous"] = previous_cursor

        async def make_request(p):
            return await self._client._request("GET", "/v2.0/search", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [SearchResult(**item) for item in items]

    async def list(
        self,
        query: Optional[str] = None,
        filter: Optional[str] = None,
        project_id: Optional[str] = None,
        types: Optional[List[str]] = None,
        limit: Optional[int] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[SearchResult]:
        """
        Alias for search() method.
        
        Provided for consistency with other resource classes that use 'list'
        as the primary method name for retrieving multiple items.
        
        Args:
            query: Search query string to filter resources by name.
            filter: Alias for `query` to align with other list methods.
            project_id: Filter results by project ObjectId (24 hex characters).
            types: List of resource types to include in search results.
            limit: Maximum number of results to return.
            next_cursor: Cursor for fetching the next page of results.
            previous_cursor: Cursor for fetching the previous page of results.
        
        Returns:
            List of SearchResult objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails.
        
        See Also:
            search: The primary search method with full documentation.
        """
        effective_query = filter if filter is not None else query
        return await self.search(
            query=effective_query,
            project_id=project_id,
            types=types,
            limit=limit,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            **kwargs,
        )
