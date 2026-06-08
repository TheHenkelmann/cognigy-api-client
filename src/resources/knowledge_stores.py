"""
KnowledgeStores resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy KnowledgeStores via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient
from ..models.knowledge_store import KnowledgeStore, KnowledgeStoreCreate, KnowledgeStoreUpdate
from ..validation import validate_create_update_data, build_list_params
from ..pagination import paginate_sync, paginate_async


class KnowledgeStoresResource:
    """
    Synchronous resource for managing Cognigy KnowledgeStores.
    
    Provides methods to list, create, read, update, and delete knowledge stores
    using the Cognigy v2.0 API.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the KnowledgeStoresResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list(
        self,
        project_id: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[KnowledgeStore]:
        """
        List knowledge stores with optional filtering and pagination.
        
        Retrieves a list of knowledge stores from the Cognigy API. Results can
        be filtered and paginated using the provided parameters.
        
        Args:
            project_id: Filter knowledge stores by project ObjectId (24 hex characters).
            limit: Maximum number of knowledge stores to return. If not specified,
                   uses the API default.
            skip: Number of knowledge stores to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of KnowledgeStore objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> stores = client.knowledge_stores.list(project_id="507f1f77bcf86cd799439011")
            >>> for store in stores:
            ...     print(f"{store.name}: {store.status}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={"projectId": project_id} if project_id else None,
        )

        def make_request(p):
            return self._client._request("GET", "/v2.0/knowledgestores", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [KnowledgeStore(**item) for item in items]

    def create(self, data: KnowledgeStoreCreate, **kwargs: Any) -> KnowledgeStore:
        """
        Create a new knowledge store.
        
        Creates a new knowledge store in the specified project using the provided data.
        
        Args:
            data: KnowledgeStoreCreate model containing the knowledge store configuration.
                  Must include 'name' and 'project_id'. Optional fields include
                  'description'.
        
        Returns:
            The created KnowledgeStore object with all fields populated by the API,
            including the generated 'id', 'reference_id', timestamps, and creator
            information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeStoreCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeStoreCreate
            >>> new_store = KnowledgeStoreCreate(
            ...     name="Product Documentation",
            ...     project_id="507f1f77bcf86cd799439011",
            ...     description="Knowledge base for product FAQs"
            ... )
            >>> store = client.knowledge_stores.create(new_store)
            >>> print(store.id)
        """
        data = validate_create_update_data(data, KnowledgeStoreCreate)
        response = self._client._request("POST", "/v2.0/knowledgestores", data=data, **kwargs)
        return KnowledgeStore(**response)

    def get(self, knowledge_store_id: str, **kwargs: Any) -> KnowledgeStore:
        """
        Get a knowledge store by ID.
        
        Retrieves a single knowledge store by its ObjectId.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store to retrieve
                                (24 hex characters).
        
        Returns:
            The KnowledgeStore object with all available fields including 'id',
            'name', 'description', 'language', 'status', 'documents',
            'reference_id', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the knowledge store not being found (404),
                             or server errors.
        
        Example:
            >>> store = client.knowledge_stores.get("507f1f77bcf86cd799439011")
            >>> print(f"Store: {store.name}, Status: {store.status}")
        """
        data = self._client._request("GET", f"/v2.0/knowledgestores/{knowledge_store_id}", **kwargs)
        return KnowledgeStore(**data)

    def update(
        self,
        knowledge_store_id: str,
        data: KnowledgeStoreUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[KnowledgeStore]:
        """
        Update a knowledge store.
        
        Updates an existing knowledge store with the provided data. Only fields that
        are set in the KnowledgeStoreUpdate object will be modified.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store to update
                                (24 hex characters).
            data: KnowledgeStoreUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name' and
                  'description'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated store is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated KnowledgeStore object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the knowledge store not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeStoreUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeStoreUpdate
            >>> update_data = KnowledgeStoreUpdate(
            ...     name="Updated Knowledge Store",
            ...     description="New description for the store"
            ... )
            >>> store = client.knowledge_stores.update(
            ...     "507f1f77bcf86cd799439011", 
            ...     update_data
            ... )
            >>> print(store.name)  # "Updated Knowledge Store"
        """
        data = validate_create_update_data(data, KnowledgeStoreUpdate)
        response = self._client._request(
            "PATCH", 
            f"/v2.0/knowledgestores/{knowledge_store_id}", 
            data=data,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return self.get(knowledge_store_id, **kwargs)
            return None
        return KnowledgeStore(**response)

    def delete(self, knowledge_store_id: str, **kwargs: Any) -> None:
        """
        Delete a knowledge store.
        
        Permanently deletes a knowledge store by its ObjectId. This action cannot
        be undone. All associated knowledge sources and chunks will also be deleted.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store to delete
                                (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the knowledge store not being found (404),
                             or server errors.
        
        Example:
            >>> client.knowledge_stores.delete("507f1f77bcf86cd799439011")
            >>> # Knowledge store is now deleted
        """
        self._client._request("DELETE", f"/v2.0/knowledgestores/{knowledge_store_id}", **kwargs)


class AsyncKnowledgeStoresResource:
    """
    Asynchronous resource for managing Cognigy KnowledgeStores.
    
    Provides async methods to list, create, read, update, and delete knowledge stores
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncKnowledgeStoresResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list(
        self,
        project_id: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[KnowledgeStore]:
        """
        List knowledge stores with optional filtering and pagination.

        Retrieves a list of knowledge stores from the Cognigy API asynchronously.
        Results can be filtered and paginated using the provided parameters.
        
        Args:
            project_id: Filter knowledge stores by project ObjectId (24 hex characters).
            limit: Maximum number of knowledge stores to return. If not specified,
                   uses the API default.
            skip: Number of knowledge stores to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of KnowledgeStore objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> stores = await client.knowledge_stores.list(
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> for store in stores:
            ...     print(f"{store.name}: {store.status}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            extra={"projectId": project_id} if project_id else None,
        )

        async def make_request(p):
            return await self._client._request("GET", "/v2.0/knowledgestores", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [KnowledgeStore(**item) for item in items]

    async def create(self, data: KnowledgeStoreCreate, **kwargs: Any) -> KnowledgeStore:
        """
        Create a new knowledge store.
        
        Creates a new knowledge store in the specified project using the provided
        data asynchronously.
        
        Args:
            data: KnowledgeStoreCreate model containing the knowledge store configuration.
                  Must include 'name' and 'project_id'. Optional fields include
                  'description'.
        
        Returns:
            The created KnowledgeStore object with all fields populated by the API,
            including the generated 'id', 'reference_id', timestamps, and creator
            information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeStoreCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeStoreCreate
            >>> new_store = KnowledgeStoreCreate(
            ...     name="Product Documentation",
            ...     project_id="507f1f77bcf86cd799439011",
            ...     description="Knowledge base for product FAQs"
            ... )
            >>> store = await client.knowledge_stores.create(new_store)
            >>> print(store.id)
        """
        data = validate_create_update_data(data, KnowledgeStoreCreate)
        response = await self._client._request("POST", "/v2.0/knowledgestores", data=data, **kwargs)
        return KnowledgeStore(**response)

    async def get(self, knowledge_store_id: str, **kwargs: Any) -> KnowledgeStore:
        """
        Get a knowledge store by ID.
        
        Retrieves a single knowledge store by its ObjectId asynchronously.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store to retrieve
                                (24 hex characters).
        
        Returns:
            The KnowledgeStore object with all available fields including 'id',
            'name', 'description', 'language', 'status', 'documents',
            'reference_id', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the knowledge store not being found (404),
                             or server errors.
        
        Example:
            >>> store = await client.knowledge_stores.get("507f1f77bcf86cd799439011")
            >>> print(f"Store: {store.name}, Status: {store.status}")
        """
        data = await self._client._request(
            "GET", 
            f"/v2.0/knowledgestores/{knowledge_store_id}",
            **kwargs,
        )
        return KnowledgeStore(**data)

    async def update(
        self,
        knowledge_store_id: str,
        data: KnowledgeStoreUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[KnowledgeStore]:
        """
        Update a knowledge store.

        Updates an existing knowledge store with the provided data asynchronously.
        Only fields that are set in the KnowledgeStoreUpdate object will be modified.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store to update
                                (24 hex characters).
            data: KnowledgeStoreUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name' and
                  'description'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated store is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated KnowledgeStore object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the knowledge store not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeStoreUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeStoreUpdate
            >>> update_data = KnowledgeStoreUpdate(
            ...     name="Updated Knowledge Store",
            ...     description="New description for the store"
            ... )
            >>> store = await client.knowledge_stores.update(
            ...     "507f1f77bcf86cd799439011", 
            ...     update_data
            ... )
            >>> print(store.name)  # "Updated Knowledge Store"
        """
        data = validate_create_update_data(data, KnowledgeStoreUpdate)
        response = await self._client._request(
            "PATCH", 
            f"/v2.0/knowledgestores/{knowledge_store_id}", 
            data=data,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return await self.get(knowledge_store_id, **kwargs)
            return None
        return KnowledgeStore(**response)

    async def delete(self, knowledge_store_id: str, **kwargs: Any) -> None:
        """
        Delete a knowledge store.
        
        Permanently deletes a knowledge store by its ObjectId asynchronously.
        This action cannot be undone. All associated knowledge sources and chunks
        will also be deleted.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store to delete
                                (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the knowledge store not being found (404),
                             or server errors.
        
        Example:
            >>> await client.knowledge_stores.delete("507f1f77bcf86cd799439011")
            >>> # Knowledge store is now deleted
        """
        await self._client._request(
            "DELETE", 
            f"/v2.0/knowledgestores/{knowledge_store_id}",
            **kwargs,
        )
