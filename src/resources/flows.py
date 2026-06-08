"""
Flows resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Flows via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient

from ..models.flow import Flow, FlowCreate, FlowUpdate
from ..validation import validate_create_update_data, build_list_params
from ..pagination import paginate_sync, paginate_async


class FlowsResource:
    """
    Synchronous resource for managing Cognigy Flows.
    
    Provides methods to list, create, read, update, and delete flows
    using the Cognigy v2.0 API.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the FlowsResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        with_ai_agents: Optional[bool] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        preferred_locale_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Flow]:
        """
        List flows with optional filtering and pagination.
        
        Retrieves a list of flows from the Cognigy API. Results can be filtered
        and paginated using the provided parameters.
        
        Args:
            project_id: Filter flows by project ObjectId (24 hex characters).
            filter: Filter string for searching flows by name.
            with_ai_agents: If True, include AI agent information in response.
            limit: Maximum number of flows to return. If not specified,
                   uses the API default.
            skip: Number of flows to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
            preferred_locale_id: Preferred locale ObjectId for localized content
                                 (24 hex characters).
        
        Returns:
            List of Flow objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> flows = client.flows.list(project_id="507f1f77bcf86cd799439011")
            >>> for flow in flows:
            ...     print(flow.name)
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={
                **({"projectId": project_id} if project_id else {}),
                **({"withAiAgents": with_ai_agents} if with_ai_agents is not None else {}),
                **({"preferredLocaleId": preferred_locale_id} if preferred_locale_id else {}),
            },
        )

        def make_request(p):
            return self._client._request("GET", "/v2.0/flows", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Flow(**item) for item in items]

    def create(self, data: FlowCreate, **kwargs: Any) -> Flow:
        """
        Create a new flow.
        
        Creates a new flow in the specified project using the provided data.
        
        Args:
            data: FlowCreate model containing the flow configuration.
                  Must include 'name' and 'project_id'. Optional fields
                  include 'description', 'context', 'attached_flows',
                  'attached_lexicons', and 'img'.
        
        Returns:
            The created Flow object with all fields populated by the API,
            including the generated 'id', 'reference_id', timestamps,
            and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the FlowCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import FlowCreate
            >>> new_flow = FlowCreate(
            ...     name="My New Flow",
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> flow = client.flows.create(new_flow)
            >>> print(flow.id)
        """
        data = validate_create_update_data(data, FlowCreate)
        response = self._client._request("POST", "/v2.0/flows", data=data, **kwargs)
        return Flow(**response)

    def get(self, flow_id: str, preferred_locale_id: Optional[str] = None, **kwargs: Any) -> Flow:
        """
        Get a flow by ID.
        
        Retrieves a single flow by its ObjectId.
        
        Args:
            flow_id: The ObjectId of the flow to retrieve (24 hex characters).
            preferred_locale_id: Preferred locale ObjectId for localized content
                                 (24 hex characters). If specified, returns
                                 content in the preferred locale when available.
        
        Returns:
            The Flow object with all available fields including 'id', 'name',
            'description', 'reference_id', 'feedback_report', 'context',
            'attached_flows', 'attached_lexicons', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the flow not being found (404),
                             or server errors.
        
        Example:
            >>> flow = client.flows.get("507f1f77bcf86cd799439011")
            >>> print(f"Flow: {flow.name}, Training outdated: {flow.is_training_out_of_date}")
        """
        params = {}
        if preferred_locale_id:
            params["preferredLocaleId"] = preferred_locale_id

        data = self._client._request("GET", f"/v2.0/flows/{flow_id}", params=params if params else None, **kwargs)
        return Flow(**data)

    def update(
        self,
        flow_id: str,
        data: FlowUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Flow]:
        """
        Update a flow.

        Updates an existing flow with the provided data. Only fields that
        are set in the FlowUpdate object will be modified.
        
        Args:
            flow_id: The ObjectId of the flow to update (24 hex characters).
            data: FlowUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'description', 'context', 'attached_flows', 'attached_lexicons',
                  'img', and 'locale_id'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated flow is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Flow object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the flow not being found (404),
                             validation errors, or server errors.
            ValidationError: If the FlowUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import FlowUpdate
            >>> update_data = FlowUpdate(
            ...     name="Updated Flow Name",
            ...     description="New description"
            ... )
            >>> flow = client.flows.update("507f1f77bcf86cd799439011", update_data)
            >>> print(flow.name)  # "Updated Flow Name"
        """
        data = validate_create_update_data(data, FlowUpdate)
        response = self._client._request("PATCH", f"/v2.0/flows/{flow_id}", data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return self.get(flow_id, **kwargs)
            return None
        return Flow(**response)

    def delete(self, flow_id: str, **kwargs: Any) -> None:
        """
        Delete a flow.
        
        Permanently deletes a flow by its ObjectId. This action cannot be undone.
        
        Args:
            flow_id: The ObjectId of the flow to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the flow not being found (404),
                             or server errors.
        
        Example:
            >>> client.flows.delete("507f1f77bcf86cd799439011")
            >>> # Flow is now deleted
        """
        self._client._request("DELETE", f"/v2.0/flows/{flow_id}", **kwargs)


class AsyncFlowsResource:
    """
    Asynchronous resource for managing Cognigy Flows.
    
    Provides async methods to list, create, read, update, and delete flows
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncFlowsResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None,
        with_ai_agents: Optional[bool] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        preferred_locale_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Flow]:
        """
        List flows with optional filtering and pagination.

        Retrieves a list of flows from the Cognigy API asynchronously.
        Results can be filtered and paginated using the provided parameters.
        
        Args:
            project_id: Filter flows by project ObjectId (24 hex characters).
            filter: Filter string for searching flows by name.
            with_ai_agents: If True, include AI agent information in response.
            limit: Maximum number of flows to return. If not specified,
                   uses the API default.
            skip: Number of flows to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
            preferred_locale_id: Preferred locale ObjectId for localized content
                                 (24 hex characters).
        
        Returns:
            List of Flow objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> flows = await client.flows.list(project_id="507f1f77bcf86cd799439011")
            >>> for flow in flows:
            ...     print(flow.name)
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={
                **({"projectId": project_id} if project_id else {}),
                **({"withAiAgents": with_ai_agents} if with_ai_agents is not None else {}),
                **({"preferredLocaleId": preferred_locale_id} if preferred_locale_id else {}),
            },
        )

        async def make_request(p):
            return await self._client._request("GET", "/v2.0/flows", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Flow(**item) for item in items]

    async def create(self, data: FlowCreate, **kwargs: Any) -> Flow:
        """
        Create a new flow.
        
        Creates a new flow in the specified project using the provided data
        asynchronously.
        
        Args:
            data: FlowCreate model containing the flow configuration.
                  Must include 'name' and 'project_id'. Optional fields
                  include 'description', 'context', 'attached_flows',
                  'attached_lexicons', and 'img'.
        
        Returns:
            The created Flow object with all fields populated by the API,
            including the generated 'id', 'reference_id', timestamps,
            and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the FlowCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import FlowCreate
            >>> new_flow = FlowCreate(
            ...     name="My New Flow",
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> flow = await client.flows.create(new_flow)
            >>> print(flow.id)
        """
        data = validate_create_update_data(data, FlowCreate)
        response = await self._client._request("POST", "/v2.0/flows", data=data, **kwargs)
        return Flow(**response)

    async def get(self, flow_id: str, preferred_locale_id: Optional[str] = None, **kwargs: Any) -> Flow:
        """
        Get a flow by ID.
        
        Retrieves a single flow by its ObjectId asynchronously.
        
        Args:
            flow_id: The ObjectId of the flow to retrieve (24 hex characters).
            preferred_locale_id: Preferred locale ObjectId for localized content
                                 (24 hex characters). If specified, returns
                                 content in the preferred locale when available.
        
        Returns:
            The Flow object with all available fields including 'id', 'name',
            'description', 'reference_id', 'feedback_report', 'context',
            'attached_flows', 'attached_lexicons', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the flow not being found (404),
                             or server errors.
        
        Example:
            >>> flow = await client.flows.get("507f1f77bcf86cd799439011")
            >>> print(f"Flow: {flow.name}, Training outdated: {flow.is_training_out_of_date}")
        """
        params = {}
        if preferred_locale_id:
            params["preferredLocaleId"] = preferred_locale_id

        data = await self._client._request("GET", f"/v2.0/flows/{flow_id}", params=params if params else None, **kwargs)
        return Flow(**data)

    async def update(
        self,
        flow_id: str,
        data: FlowUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Flow]:
        """
        Update a flow.

        Updates an existing flow with the provided data asynchronously.
        Only fields that are set in the FlowUpdate object will be modified.
        
        Args:
            flow_id: The ObjectId of the flow to update (24 hex characters).
            data: FlowUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'description', 'context', 'attached_flows', 'attached_lexicons',
                  'img', and 'locale_id'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated flow is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Flow object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the flow not being found (404),
                             validation errors, or server errors.
            ValidationError: If the FlowUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import FlowUpdate
            >>> update_data = FlowUpdate(
            ...     name="Updated Flow Name",
            ...     description="New description"
            ... )
            >>> flow = await client.flows.update("507f1f77bcf86cd799439011", update_data)
            >>> print(flow.name)  # "Updated Flow Name"
        """
        data = validate_create_update_data(data, FlowUpdate)
        response = await self._client._request("PATCH", f"/v2.0/flows/{flow_id}", data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return await self.get(flow_id, **kwargs)
            return None
        return Flow(**response)

    async def delete(self, flow_id: str, **kwargs: Any) -> None:
        """
        Delete a flow.
        
        Permanently deletes a flow by its ObjectId asynchronously.
        This action cannot be undone.
        
        Args:
            flow_id: The ObjectId of the flow to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the flow not being found (404),
                             or server errors.
        
        Example:
            >>> await client.flows.delete("507f1f77bcf86cd799439011")
            >>> # Flow is now deleted
        """
        await self._client._request("DELETE", f"/v2.0/flows/{flow_id}", **kwargs)
