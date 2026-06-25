"""
Functions resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Functions via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient
import builtins

from ..models.function import Function, FunctionCreate, FunctionUpdate
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data


class FunctionsResource:
    """
    Synchronous resource for managing Cognigy Functions.

    Provides methods to list, create, read, update, and delete functions
    using the Cognigy v2.0 API. Functions contain JavaScript source code
    that can be invoked from a Project.

    Attributes:
        _client: The CognigyClient instance used for API requests.
    """

    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the FunctionsResource.

        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list(
        self,
        project_id: str | None = None,
        filter: str | None = None,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[Function]:
        """
        List functions with optional filtering and pagination.

        Retrieves a list of functions from the Cognigy API. Results can be
        filtered and paginated using the provided parameters.

        Args:
            project_id: Filter functions by project ObjectId (24 hex characters).
            filter: Filter string for searching functions by name.
            limit: Maximum number of functions to return. If not specified,
                   uses the API default.
            skip: Number of functions to skip for offset-based pagination.
            sort: Sort order string. Use field name with direction
                  (e.g., "name:asc" or "createdAt:desc").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of Function objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> functions = client.functions.list(project_id="507f1f77bcf86cd799439011")
            >>> for fn in functions:
            ...     print(f"{fn.name}: {fn.id}")
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={"projectId": project_id} if project_id else None,
        )

        def make_request(p):
            return self._client._request("GET", "/v2.0/functions", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Function(**item) for item in items]

    def create(self, data: FunctionCreate, **kwargs: Any) -> Function:
        """
        Create a new function.

        Creates a new function in the specified project using the provided data.

        Args:
            data: FunctionCreate model containing the function configuration.
                  Must include 'project_id'. Optional fields include 'name',
                  'code', and 'is_disabled'.

        Returns:
            The created Function object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            CognigyValidationError: If the FunctionCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import FunctionCreate
            >>> new_function = FunctionCreate(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     name="My Function",
            ...     code="console.log('Hello World');"
            ... )
            >>> fn = client.functions.create(new_function)
            >>> print(fn.id)
        """
        data = validate_create_update_data(data, FunctionCreate)
        response = self._client._request("POST", "/v2.0/functions", data=data, **kwargs)
        return Function(**response)

    def get(self, function_id: str, **kwargs: Any) -> Function:
        """
        Get a function by ID.

        Retrieves a single function by its ObjectId.

        Args:
            function_id: The ObjectId of the function to retrieve (24 hex characters).

        Returns:
            The Function object with all available fields including 'id', 'name',
            'code', 'is_disabled', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the function not being found (404),
                             or server errors.

        Example:
            >>> fn = client.functions.get("507f1f77bcf86cd799439011")
            >>> print(f"Function: {fn.name}, Disabled: {fn.is_disabled}")
        """
        data = self._client._request("GET", f"/v2.0/functions/{function_id}", **kwargs)
        return Function(**data)

    def update(
        self,
        function_id: str,
        data: FunctionUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Function | None:
        """
        Update a function.

        Updates an existing function with the provided data. Only fields that
        are set in the FunctionUpdate object will be modified. Allows changing
        the name, source code, or enabled state. You can disable the function
        without deleting it.

        Args:
            function_id: The ObjectId of the function to update (24 hex characters).
            data: FunctionUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'code', and 'is_disabled'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated function is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated Function object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the function not being found (404),
                             validation errors, or server errors.
            CognigyValidationError: If the FunctionUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import FunctionUpdate
            >>> update_data = FunctionUpdate(
            ...     name="Updated Function Name",
            ...     is_disabled=True
            ... )
            >>> fn = client.functions.update("507f1f77bcf86cd799439011", update_data)
            >>> print(fn.name)  # "Updated Function Name"
        """
        data = validate_create_update_data(data, FunctionUpdate)
        response = self._client._request(
            "PATCH", f"/v2.0/functions/{function_id}", data=data, **kwargs
        )
        if response is None:
            if fetch_updated:
                return self.get(function_id, **kwargs)
            return None
        return Function(**response)

    def delete(self, function_id: str, **kwargs: Any) -> None:
        """
        Delete a function.

        Permanently deletes a function by its ObjectId. This action cannot
        be undone. The API kicks off the delete operation asynchronously
        (HTTP 202 Accepted).

        Args:
            function_id: The ObjectId of the function to delete (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the function not being found (404),
                             or server errors.

        Example:
            >>> client.functions.delete("507f1f77bcf86cd799439011")
            >>> # Function is now deleted
        """
        self._client._request("DELETE", f"/v2.0/functions/{function_id}", **kwargs)


class AsyncFunctionsResource:
    """
    Asynchronous resource for managing Cognigy Functions.

    Provides async methods to list, create, read, update, and delete functions
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.

    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """

    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncFunctionsResource.

        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list(
        self,
        project_id: str | None = None,
        filter: str | None = None,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[Function]:
        """
        List functions with optional filtering and pagination.

        Retrieves a list of functions from the Cognigy API asynchronously.
        Results can be filtered and paginated using the provided parameters.

        Args:
            project_id: Filter functions by project ObjectId (24 hex characters).
            filter: Filter string for searching functions by name.
            limit: Maximum number of functions to return. If not specified,
                   uses the API default.
            skip: Number of functions to skip for offset-based pagination.
            sort: Sort order string. Use field name with direction
                  (e.g., "name:asc" or "createdAt:desc").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of Function objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> functions = await client.functions.list(project_id="507f1f77bcf86cd799439011")
            >>> for fn in functions:
            ...     print(f"{fn.name}: {fn.id}")
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={"projectId": project_id} if project_id else None,
        )

        async def make_request(p):
            return await self._client._request("GET", "/v2.0/functions", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Function(**item) for item in items]

    async def create(self, data: FunctionCreate, **kwargs: Any) -> Function:
        """
        Create a new function.

        Creates a new function in the specified project using the provided data
        asynchronously.

        Args:
            data: FunctionCreate model containing the function configuration.
                  Must include 'project_id'. Optional fields include 'name',
                  'code', and 'is_disabled'.

        Returns:
            The created Function object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            CognigyValidationError: If the FunctionCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import FunctionCreate
            >>> new_function = FunctionCreate(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     name="My Function",
            ...     code="console.log('Hello World');"
            ... )
            >>> fn = await client.functions.create(new_function)
            >>> print(fn.id)
        """
        data = validate_create_update_data(data, FunctionCreate)
        response = await self._client._request("POST", "/v2.0/functions", data=data, **kwargs)
        return Function(**response)

    async def get(self, function_id: str, **kwargs: Any) -> Function:
        """
        Get a function by ID.

        Retrieves a single function by its ObjectId asynchronously.

        Args:
            function_id: The ObjectId of the function to retrieve (24 hex characters).

        Returns:
            The Function object with all available fields including 'id', 'name',
            'code', 'is_disabled', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the function not being found (404),
                             or server errors.

        Example:
            >>> fn = await client.functions.get("507f1f77bcf86cd799439011")
            >>> print(f"Function: {fn.name}, Disabled: {fn.is_disabled}")
        """
        data = await self._client._request("GET", f"/v2.0/functions/{function_id}", **kwargs)
        return Function(**data)

    async def update(
        self,
        function_id: str,
        data: FunctionUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Function | None:
        """
        Update a function.

        Updates an existing function with the provided data asynchronously.
        Only fields that are set in the FunctionUpdate object will be modified.
        Allows changing the name, source code, or enabled state. You can
        disable the function without deleting it.

        Args:
            function_id: The ObjectId of the function to update (24 hex characters).
            data: FunctionUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'code', and 'is_disabled'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated function is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated Function object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the function not being found (404),
                             validation errors, or server errors.
            CognigyValidationError: If the FunctionUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import FunctionUpdate
            >>> update_data = FunctionUpdate(
            ...     name="Updated Function Name",
            ...     is_disabled=True
            ... )
            >>> fn = await client.functions.update("507f1f77bcf86cd799439011", update_data)
            >>> print(fn.name)  # "Updated Function Name"
        """
        data = validate_create_update_data(data, FunctionUpdate)
        response = await self._client._request(
            "PATCH", f"/v2.0/functions/{function_id}", data=data, **kwargs
        )
        if response is None:
            if fetch_updated:
                return await self.get(function_id, **kwargs)
            return None
        return Function(**response)

    async def delete(self, function_id: str, **kwargs: Any) -> None:
        """
        Delete a function.

        Permanently deletes a function by its ObjectId asynchronously.
        This action cannot be undone. The API kicks off the delete operation
        asynchronously (HTTP 202 Accepted).

        Args:
            function_id: The ObjectId of the function to delete (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the function not being found (404),
                             or server errors.

        Example:
            >>> await client.functions.delete("507f1f77bcf86cd799439011")
            >>> # Function is now deleted
        """
        await self._client._request("DELETE", f"/v2.0/functions/{function_id}", **kwargs)
