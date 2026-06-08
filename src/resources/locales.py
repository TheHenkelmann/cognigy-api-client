"""
Locales resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Locales via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient
from ..models.locale import Locale, LocaleCreate, LocaleUpdate
from ..validation import validate_create_update_data, build_list_params
from ..pagination import paginate_sync, paginate_async


class LocalesResource:
    """
    Synchronous resource for managing Cognigy Locales.
    
    Provides methods to list, create, read, update, and delete locales
    using the Cognigy v2.0 API. Locales define language configurations
    for multi-language virtual agent projects.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the LocalesResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
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
        **kwargs: Any,
    ) -> List[Locale]:
        """
        List locales with optional filtering and pagination.
        
        Retrieves a list of locales from the Cognigy API. Results can be filtered
        and paginated using the provided parameters.
        
        Args:
            project_id: Filter locales by project ObjectId (24 hex characters).
            filter: Filter string for searching locales by name.
            limit: Maximum number of locales to return. If not specified,
                   uses the API default.
            skip: Number of locales to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of Locale objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> locales = client.locales.list(project_id="507f1f77bcf86cd799439011")
            >>> for locale in locales:
            ...     print(f"{locale.name}: {locale.nlu_language}")
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
            return self._client._request("GET", "/v2.0/locales", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Locale(**item) for item in items]

    def create(self, data: LocaleCreate, **kwargs: Any) -> Locale:
        """
        Create a new locale.
        
        Creates a new locale in the specified project using the provided data.
        
        Args:
            data: LocaleCreate model containing the locale configuration.
                  Must include 'project_id'. Optional fields include 'name',
                  'primary', 'nlu_language', and 'fallback_locale_reference'.
        
        Returns:
            The created Locale object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the LocaleCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import LocaleCreate, NluLanguage
            >>> new_locale = LocaleCreate(
            ...     name="German",
            ...     project_id="507f1f77bcf86cd799439011",
            ...     nlu_language=NluLanguage.DE_DE
            ... )
            >>> locale = client.locales.create(new_locale)
            >>> print(locale.id)
        """
        data = validate_create_update_data(data, LocaleCreate)
        response = self._client._request("POST", "/v2.0/locales", data=data, **kwargs)
        return Locale(**response)

    def get(self, locale_id: str, **kwargs: Any) -> Locale:
        """
        Get a locale by ID.
        
        Retrieves a single locale by its ObjectId.
        
        Args:
            locale_id: The ObjectId of the locale to retrieve (24 hex characters).
        
        Returns:
            The Locale object with all available fields including 'id', 'name',
            'primary', 'nlu_language', 'fallback_locale_reference', and
            metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the locale not being found (404),
                             or server errors.
        
        Example:
            >>> locale = client.locales.get("507f1f77bcf86cd799439011")
            >>> print(f"Locale: {locale.name}, Primary: {locale.primary}")
        """
        data = self._client._request("GET", f"/v2.0/locales/{locale_id}", **kwargs)
        return Locale(**data)

    def update(
        self,
        locale_id: str,
        data: LocaleUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Locale]:
        """
        Update a locale.

        Updates an existing locale with the provided data. Only fields that
        are set in the LocaleUpdate object will be modified.
        
        Args:
            locale_id: The ObjectId of the locale to update (24 hex characters).
            data: LocaleUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'primary', 'nlu_language', and 'fallback_locale_reference'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated locale is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Locale object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the locale not being found (404),
                             validation errors, or server errors.
            ValidationError: If the LocaleUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import LocaleUpdate, NluLanguage
            >>> update_data = LocaleUpdate(
            ...     name="Updated Locale Name",
            ...     nlu_language=NluLanguage.EN_GB
            ... )
            >>> locale = client.locales.update("507f1f77bcf86cd799439011", update_data)
            >>> print(locale.name)  # "Updated Locale Name"
        """
        data = validate_create_update_data(data, LocaleUpdate)
        response = self._client._request("PATCH", f"/v2.0/locales/{locale_id}", data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return self.get(locale_id, **kwargs)
            return None
        return Locale(**response)

    def delete(self, locale_id: str, **kwargs: Any) -> None:
        """
        Delete a locale.
        
        Permanently deletes a locale by its ObjectId. This action cannot be undone.
        Note: You cannot delete the primary locale of a project.
        
        Args:
            locale_id: The ObjectId of the locale to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the locale not being found (404),
                             attempting to delete the primary locale, or
                             server errors.
        
        Example:
            >>> client.locales.delete("507f1f77bcf86cd799439011")
            >>> # Locale is now deleted
        """
        self._client._request("DELETE", f"/v2.0/locales/{locale_id}", **kwargs)


class AsyncLocalesResource:
    """
    Asynchronous resource for managing Cognigy Locales.
    
    Provides async methods to list, create, read, update, and delete locales
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncLocalesResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
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
        **kwargs: Any,
    ) -> List[Locale]:
        """
        List locales with optional filtering and pagination.

        Retrieves a list of locales from the Cognigy API asynchronously.
        Results can be filtered and paginated using the provided parameters.
        
        Args:
            project_id: Filter locales by project ObjectId (24 hex characters).
            filter: Filter string for searching locales by name.
            limit: Maximum number of locales to return. If not specified,
                   uses the API default.
            skip: Number of locales to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of Locale objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> locales = await client.locales.list(project_id="507f1f77bcf86cd799439011")
            >>> for locale in locales:
            ...     print(f"{locale.name}: {locale.nlu_language}")
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
            return await self._client._request("GET", "/v2.0/locales", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Locale(**item) for item in items]

    async def create(self, data: LocaleCreate, **kwargs: Any) -> Locale:
        """
        Create a new locale.
        
        Creates a new locale in the specified project using the provided data
        asynchronously.
        
        Args:
            data: LocaleCreate model containing the locale configuration.
                  Must include 'project_id'. Optional fields include 'name',
                  'primary', 'nlu_language', and 'fallback_locale_reference'.
        
        Returns:
            The created Locale object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the LocaleCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import LocaleCreate, NluLanguage
            >>> new_locale = LocaleCreate(
            ...     name="German",
            ...     project_id="507f1f77bcf86cd799439011",
            ...     nlu_language=NluLanguage.DE_DE
            ... )
            >>> locale = await client.locales.create(new_locale)
            >>> print(locale.id)
        """
        data = validate_create_update_data(data, LocaleCreate)
        response = await self._client._request("POST", "/v2.0/locales", data=data, **kwargs)
        return Locale(**response)

    async def get(self, locale_id: str, **kwargs: Any) -> Locale:
        """
        Get a locale by ID.
        
        Retrieves a single locale by its ObjectId asynchronously.
        
        Args:
            locale_id: The ObjectId of the locale to retrieve (24 hex characters).
        
        Returns:
            The Locale object with all available fields including 'id', 'name',
            'primary', 'nlu_language', 'fallback_locale_reference', and
            metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the locale not being found (404),
                             or server errors.
        
        Example:
            >>> locale = await client.locales.get("507f1f77bcf86cd799439011")
            >>> print(f"Locale: {locale.name}, Primary: {locale.primary}")
        """
        data = await self._client._request("GET", f"/v2.0/locales/{locale_id}", **kwargs)
        return Locale(**data)

    async def update(
        self,
        locale_id: str,
        data: LocaleUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Locale]:
        """
        Update a locale.

        Updates an existing locale with the provided data asynchronously.
        Only fields that are set in the LocaleUpdate object will be modified.
        
        Args:
            locale_id: The ObjectId of the locale to update (24 hex characters).
            data: LocaleUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'primary', 'nlu_language', and 'fallback_locale_reference'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated locale is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Locale object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the locale not being found (404),
                             validation errors, or server errors.
            ValidationError: If the LocaleUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import LocaleUpdate, NluLanguage
            >>> update_data = LocaleUpdate(
            ...     name="Updated Locale Name",
            ...     nlu_language=NluLanguage.EN_GB
            ... )
            >>> locale = await client.locales.update("507f1f77bcf86cd799439011", update_data)
            >>> print(locale.name)  # "Updated Locale Name"
        """
        data = validate_create_update_data(data, LocaleUpdate)
        response = await self._client._request("PATCH", f"/v2.0/locales/{locale_id}", data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return await self.get(locale_id, **kwargs)
            return None
        return Locale(**response)

    async def delete(self, locale_id: str, **kwargs: Any) -> None:
        """
        Delete a locale.
        
        Permanently deletes a locale by its ObjectId asynchronously.
        This action cannot be undone.
        Note: You cannot delete the primary locale of a project.
        
        Args:
            locale_id: The ObjectId of the locale to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the locale not being found (404),
                             attempting to delete the primary locale, or
                             server errors.
        
        Example:
            >>> await client.locales.delete("507f1f77bcf86cd799439011")
            >>> # Locale is now deleted
        """
        await self._client._request("DELETE", f"/v2.0/locales/{locale_id}", **kwargs)
