"""
KnowledgeSources resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Knowledge Sources via the v2.0 API endpoints.

Knowledge sources are individual sources of content within a knowledge store
and are accessed through the hierarchical path:
/v2.0/knowledgestores/{knowledgeStoreId}/sources
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient
from ..models.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceCreate,
    KnowledgeSourceUpdate,
)
from ..validation import validate_create_update_data, build_list_params
from ..pagination import paginate_sync, paginate_async


class KnowledgeSourcesResource:
    """
    Synchronous resource for managing Cognigy Knowledge Sources.
    
    Provides methods to list, create, read, update, and delete knowledge sources
    using the Cognigy v2.0 API. Knowledge sources are accessed within the context
    of a knowledge store.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the KnowledgeSourcesResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def _build_base_path(self, knowledge_store_id: str) -> str:
        """
        Build the base API path for knowledge sources.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            
        Returns:
            The base API path string for knowledge sources endpoints.
        """
        return f"/v2.0/knowledgestores/{knowledge_store_id}/sources"

    def list(
        self,
        knowledge_store_id: str,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[KnowledgeSource]:
        """
        List knowledge sources within a knowledge store.
        
        Retrieves a list of knowledge sources from the specified knowledge store.
        Results can be paginated using cursor-based pagination.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            limit: Maximum number of sources to return. If not specified,
                   a default of 1 is used.
            skip: Number of sources to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of KnowledgeSource objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> sources = client.knowledge_sources.list(
            ...     knowledge_store_id="507f1f77bcf86cd799439011"
            ... )
            >>> for source in sources:
            ...     print(f"{source.name}: {source.type}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        path = self._build_base_path(knowledge_store_id)

        def make_request(p):
            return self._client._request("GET", path, params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [KnowledgeSource(**item) for item in items]

    def create(
        self,
        knowledge_store_id: str,
        data: KnowledgeSourceCreate,
        **kwargs: Any,
    ) -> KnowledgeSource:
        """
        Create a new knowledge source.
        
        Creates a new knowledge source in the specified knowledge store
        using the provided data.
        
        Note:
            - For type "url", provide the `url` field with the website URL to scrape.
            - For type "extension", provide the `connector_id` field with the UUID
              of the connector to use.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            data: KnowledgeSourceCreate model containing the source configuration.
                  Fields include 'name', 'description', 'type', 'meta_data',
                  'url' (for url type), and 'connector_id' (for extension type).
        
        Returns:
            The created KnowledgeSource object with all fields populated by the API,
            including the generated 'id', 'reference_id', 'status', timestamps,
            and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeSourceCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeSourceCreate, KnowledgeSourceType
            >>> new_source = KnowledgeSourceCreate(
            ...     name="Documentation",
            ...     description="Product documentation pages",
            ...     type=KnowledgeSourceType.URL,
            ...     url="https://docs.example.com/guide"
            ... )
            >>> source = client.knowledge_sources.create(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     data=new_source
            ... )
            >>> print(source.id)
        """
        data = validate_create_update_data(data, KnowledgeSourceCreate)
        path = self._build_base_path(knowledge_store_id)
        response = self._client._request("POST", path, data=data, **kwargs)
        # The API wraps the response in {"knowledgeSource": {...}}
        return KnowledgeSource(**response.get("knowledgeSource", response))

    def get(
        self,
        knowledge_store_id: str,
        source_id: str,
        **kwargs: Any,
    ) -> KnowledgeSource:
        """
        Get a knowledge source by ID.
        
        Retrieves a single knowledge source by its ObjectId within the specified
        knowledge store.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the source to retrieve (24 hex characters).
        
        Returns:
            The KnowledgeSource object with all available fields including 'id',
            'name', 'description', 'type', 'status', 'meta_data', 'data',
            'chunk_count', 'connector_reference', 'reference_id', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the source not being found (404),
                             or server errors.
        
        Example:
            >>> source = client.knowledge_sources.get(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012"
            ... )
            >>> print(f"Source: {source.name}, Status: {source.status}, Chunks: {source.chunk_count}")
        """
        path = f"{self._build_base_path(knowledge_store_id)}/{source_id}"
        response = self._client._request("GET", path, **kwargs)
        return KnowledgeSource(**response)

    def update(
        self,
        knowledge_store_id: str,
        source_id: str,
        data: KnowledgeSourceUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[KnowledgeSource]:
        """
        Update a knowledge source.
        
        Updates an existing knowledge source with the provided data. Only fields that
        are set in the KnowledgeSourceUpdate object will be modified.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the source to update (24 hex characters).
            data: KnowledgeSourceUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'description', 'status', and 'meta_data'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated source is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated KnowledgeSource object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the source not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeSourceUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeSourceUpdate, KnowledgeSourceStatus
            >>> update_data = KnowledgeSourceUpdate(
            ...     name="Updated Documentation",
            ...     status=KnowledgeSourceStatus.DISABLED
            ... )
            >>> source = client.knowledge_sources.update(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     data=update_data
            ... )
            >>> print(source.name)  # "Updated Documentation"
        """
        data = validate_create_update_data(data, KnowledgeSourceUpdate)
        path = f"{self._build_base_path(knowledge_store_id)}/{source_id}"
        response = self._client._request("PATCH", path, data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return self.get(knowledge_store_id, source_id, **kwargs)
            return None
        return KnowledgeSource(**response)

    def delete(
        self,
        knowledge_store_id: str,
        source_id: str,
        **kwargs: Any,
    ) -> None:
        """
        Delete a knowledge source.
        
        Permanently deletes a knowledge source by its ObjectId. This action cannot be undone.
        All chunks within the source will also be deleted.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the source to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the source not being found (404),
                             or server errors.
        
        Example:
            >>> client.knowledge_sources.delete(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012"
            ... )
            >>> # Source and all its chunks are now deleted
        """
        path = f"{self._build_base_path(knowledge_store_id)}/{source_id}"
        self._client._request("DELETE", path, **kwargs)


class AsyncKnowledgeSourcesResource:
    """
    Asynchronous resource for managing Cognigy Knowledge Sources.
    
    Provides async methods to list, create, read, update, and delete knowledge
    sources using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations. Knowledge sources are accessed within the
    context of a knowledge store.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncKnowledgeSourcesResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    def _build_base_path(self, knowledge_store_id: str) -> str:
        """
        Build the base API path for knowledge sources.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            
        Returns:
            The base API path string for knowledge sources endpoints.
        """
        return f"/v2.0/knowledgestores/{knowledge_store_id}/sources"

    async def list(
        self,
        knowledge_store_id: str,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[KnowledgeSource]:
        """
        List knowledge sources within a knowledge store.
        
        Retrieves a list of knowledge sources from the specified knowledge store
        asynchronously. Results can be paginated using cursor-based pagination.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            limit: Maximum number of sources to return. If not specified,
                   a default of 1 is used.
            skip: Number of sources to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of KnowledgeSource objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> sources = await client.knowledge_sources.list(
            ...     knowledge_store_id="507f1f77bcf86cd799439011"
            ... )
            >>> for source in sources:
            ...     print(f"{source.name}: {source.type}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        path = self._build_base_path(knowledge_store_id)

        async def make_request(p):
            return await self._client._request("GET", path, params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [KnowledgeSource(**item) for item in items]

    async def create(
        self,
        knowledge_store_id: str,
        data: KnowledgeSourceCreate,
        **kwargs: Any,
    ) -> KnowledgeSource:
        """
        Create a new knowledge source.
        
        Creates a new knowledge source in the specified knowledge store
        using the provided data asynchronously.
        
        Note:
            - For type "url", provide the `url` field with the website URL to scrape.
            - For type "extension", provide the `connector_id` field with the UUID
              of the connector to use.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            data: KnowledgeSourceCreate model containing the source configuration.
                  Fields include 'name', 'description', 'type', 'meta_data',
                  'url' (for url type), and 'connector_id' (for extension type).
        
        Returns:
            The created KnowledgeSource object with all fields populated by the API,
            including the generated 'id', 'reference_id', 'status', timestamps,
            and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeSourceCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeSourceCreate, KnowledgeSourceType
            >>> new_source = KnowledgeSourceCreate(
            ...     name="Documentation",
            ...     description="Product documentation pages",
            ...     type=KnowledgeSourceType.URL,
            ...     url="https://docs.example.com/guide"
            ... )
            >>> source = await client.knowledge_sources.create(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     data=new_source
            ... )
            >>> print(source.id)
        """
        data = validate_create_update_data(data, KnowledgeSourceCreate)
        path = self._build_base_path(knowledge_store_id)
        response = await self._client._request("POST", path, data=data, **kwargs)
        # The API wraps the response in {"knowledgeSource": {...}}
        return KnowledgeSource(**response.get("knowledgeSource", response))

    async def get(
        self,
        knowledge_store_id: str,
        source_id: str,
        **kwargs: Any,
    ) -> KnowledgeSource:
        """
        Get a knowledge source by ID.
        
        Retrieves a single knowledge source by its ObjectId asynchronously within
        the specified knowledge store.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the source to retrieve (24 hex characters).
        
        Returns:
            The KnowledgeSource object with all available fields including 'id',
            'name', 'description', 'type', 'status', 'meta_data', 'data',
            'chunk_count', 'connector_reference', 'reference_id', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the source not being found (404),
                             or server errors.
        
        Example:
            >>> source = await client.knowledge_sources.get(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012"
            ... )
            >>> print(f"Source: {source.name}, Status: {source.status}, Chunks: {source.chunk_count}")
        """
        path = f"{self._build_base_path(knowledge_store_id)}/{source_id}"
        response = await self._client._request("GET", path, **kwargs)
        return KnowledgeSource(**response)

    async def update(
        self,
        knowledge_store_id: str,
        source_id: str,
        data: KnowledgeSourceUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[KnowledgeSource]:
        """
        Update a knowledge source.
        
        Updates an existing knowledge source with the provided data asynchronously.
        Only fields that are set in the KnowledgeSourceUpdate object will be modified.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the source to update (24 hex characters).
            data: KnowledgeSourceUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'description', 'status', and 'meta_data'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated source is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated KnowledgeSource object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the source not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeSourceUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import KnowledgeSourceUpdate, KnowledgeSourceStatus
            >>> update_data = KnowledgeSourceUpdate(
            ...     name="Updated Documentation",
            ...     status=KnowledgeSourceStatus.DISABLED
            ... )
            >>> source = await client.knowledge_sources.update(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     data=update_data
            ... )
            >>> print(source.name)  # "Updated Documentation"
        """
        data = validate_create_update_data(data, KnowledgeSourceUpdate)
        path = f"{self._build_base_path(knowledge_store_id)}/{source_id}"
        response = await self._client._request("PATCH", path, data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return await self.get(knowledge_store_id, source_id, **kwargs)
            return None
        return KnowledgeSource(**response)

    async def delete(
        self,
        knowledge_store_id: str,
        source_id: str,
        **kwargs: Any,
    ) -> None:
        """
        Delete a knowledge source.
        
        Permanently deletes a knowledge source by its ObjectId asynchronously.
        This action cannot be undone. All chunks within the source will also be deleted.
        
        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the source to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the source not being found (404),
                             or server errors.
        
        Example:
            >>> await client.knowledge_sources.delete(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012"
            ... )
            >>> # Source and all its chunks are now deleted
        """
        path = f"{self._build_base_path(knowledge_store_id)}/{source_id}"
        await self._client._request("DELETE", path, **kwargs)
