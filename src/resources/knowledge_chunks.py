"""
KnowledgeChunks resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Knowledge Chunks via the v2.0 API endpoints.

Knowledge chunks are individual pieces of content within a knowledge source
and are accessed through the hierarchical path:
/v2.0/knowledgestores/{knowledgeStoreId}/sources/{sourceId}/chunks
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient
import builtins

from ..models.knowledge_chunk import KnowledgeChunk, KnowledgeChunkCreate, KnowledgeChunkUpdate
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data


class KnowledgeChunksResource:
    """
    Synchronous resource for managing Cognigy Knowledge Chunks.

    Provides methods to list, create, read, update, and delete knowledge chunks
    using the Cognigy v2.0 API. Knowledge chunks are accessed within the context
    of a knowledge store and source.

    Attributes:
        _client: The CognigyClient instance used for API requests.
    """

    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the KnowledgeChunksResource.

        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def _build_base_path(self, knowledge_store_id: str, source_id: str) -> str:
        """
        Build the base API path for knowledge chunks.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).

        Returns:
            The base API path string for knowledge chunks endpoints.
        """
        return f"/v2.0/knowledgestores/{knowledge_store_id}/sources/{source_id}/chunks"

    def list(
        self,
        knowledge_store_id: str,
        source_id: str,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[KnowledgeChunk]:
        """
        List knowledge chunks within a knowledge source.

        Retrieves a list of knowledge chunks from the specified knowledge store
        and source. Results can be paginated using cursor-based pagination.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            limit: Maximum number of chunks to return. If not specified,
                   a default of 1 is used.
            skip: Number of chunks to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of KnowledgeChunk objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> chunks = client.knowledge_chunks.list(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012"
            ... )
            >>> for chunk in chunks:
            ...     print(chunk.text)
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        path = self._build_base_path(knowledge_store_id, source_id)

        def make_request(p):
            return self._client._request("GET", path, params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [KnowledgeChunk(**item) for item in items]

    def create(
        self,
        knowledge_store_id: str,
        source_id: str,
        data: KnowledgeChunkCreate,
        **kwargs: Any,
    ) -> KnowledgeChunk:
        """
        Create a new knowledge chunk.

        Creates a new knowledge chunk in the specified knowledge store and source
        using the provided data.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            data: KnowledgeChunkCreate model containing the chunk configuration.
                  Optional fields include 'order', 'text', and 'data'.

        Returns:
            The created KnowledgeChunk object with all fields populated by the API,
            including the generated 'id', 'reference_id', timestamps,
            and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeChunkCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeChunkCreate
            >>> new_chunk = KnowledgeChunkCreate(
            ...     order=1,
            ...     text="This is a paragraph from an article"
            ... )
            >>> chunk = client.knowledge_chunks.create(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     data=new_chunk
            ... )
            >>> print(chunk.id)
        """
        data = validate_create_update_data(data, KnowledgeChunkCreate)
        path = self._build_base_path(knowledge_store_id, source_id)
        response = self._client._request("POST", path, data=data, **kwargs)
        return KnowledgeChunk(**response)

    def get(
        self,
        knowledge_store_id: str,
        source_id: str,
        chunk_id: str,
        **kwargs: Any,
    ) -> KnowledgeChunk:
        """
        Get a knowledge chunk by ID.

        Retrieves a single knowledge chunk by its ObjectId within the specified
        knowledge store and source.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            chunk_id: The ObjectId of the chunk to retrieve (24 hex characters).

        Returns:
            The KnowledgeChunk object with all available fields including 'id',
            'order', 'text', 'data', 'disabled', 'reference_id', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the chunk not being found (404),
                             or server errors.

        Example:
            >>> chunk = client.knowledge_chunks.get(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     chunk_id="507f1f77bcf86cd799439013"
            ... )
            >>> print(f"Chunk: {chunk.text}, Disabled: {chunk.disabled}")
        """
        path = f"{self._build_base_path(knowledge_store_id, source_id)}/{chunk_id}"
        response = self._client._request("GET", path, **kwargs)
        return KnowledgeChunk(**response)

    def update(
        self,
        knowledge_store_id: str,
        source_id: str,
        chunk_id: str,
        data: KnowledgeChunkUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> KnowledgeChunk | None:
        """
        Update a knowledge chunk.

        Updates an existing knowledge chunk with the provided data. Only fields that
        are set in the KnowledgeChunkUpdate object will be modified.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            chunk_id: The ObjectId of the chunk to update (24 hex characters).
            data: KnowledgeChunkUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'order',
                  'text', 'data', and 'disabled'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated chunk is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated KnowledgeChunk object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the chunk not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeChunkUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeChunkUpdate
            >>> update_data = KnowledgeChunkUpdate(
            ...     text="Updated paragraph text",
            ...     disabled=False
            ... )
            >>> chunk = client.knowledge_chunks.update(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     chunk_id="507f1f77bcf86cd799439013",
            ...     data=update_data
            ... )
            >>> print(chunk.text)  # "Updated paragraph text"
        """
        data = validate_create_update_data(data, KnowledgeChunkUpdate)
        path = f"{self._build_base_path(knowledge_store_id, source_id)}/{chunk_id}"
        response = self._client._request("PATCH", path, data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return self.get(knowledge_store_id, source_id, chunk_id, **kwargs)
            return None
        return KnowledgeChunk(**response)

    def delete(
        self,
        knowledge_store_id: str,
        source_id: str,
        chunk_id: str,
        **kwargs: Any,
    ) -> None:
        """
        Delete a knowledge chunk.

        Permanently deletes a knowledge chunk by its ObjectId. This action cannot be undone.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            chunk_id: The ObjectId of the chunk to delete (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the chunk not being found (404),
                             or server errors.

        Example:
            >>> client.knowledge_chunks.delete(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     chunk_id="507f1f77bcf86cd799439013"
            ... )
            >>> # Chunk is now deleted
        """
        path = f"{self._build_base_path(knowledge_store_id, source_id)}/{chunk_id}"
        self._client._request("DELETE", path, **kwargs)


class AsyncKnowledgeChunksResource:
    """
    Asynchronous resource for managing Cognigy Knowledge Chunks.

    Provides async methods to list, create, read, update, and delete knowledge
    chunks using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations. Knowledge chunks are accessed within the
    context of a knowledge store and source.

    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """

    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncKnowledgeChunksResource.

        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    def _build_base_path(self, knowledge_store_id: str, source_id: str) -> str:
        """
        Build the base API path for knowledge chunks.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).

        Returns:
            The base API path string for knowledge chunks endpoints.
        """
        return f"/v2.0/knowledgestores/{knowledge_store_id}/sources/{source_id}/chunks"

    async def list(
        self,
        knowledge_store_id: str,
        source_id: str,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[KnowledgeChunk]:
        """
        List knowledge chunks within a knowledge source.

        Retrieves a list of knowledge chunks from the specified knowledge store
        and source asynchronously. Results can be paginated using cursor-based pagination.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            limit: Maximum number of chunks to return. If not specified,
                   a default of 1 is used.
            skip: Number of chunks to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of KnowledgeChunk objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> chunks = await client.knowledge_chunks.list(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012"
            ... )
            >>> for chunk in chunks:
            ...     print(chunk.text)
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        path = self._build_base_path(knowledge_store_id, source_id)

        async def make_request(p):
            return await self._client._request("GET", path, params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [KnowledgeChunk(**item) for item in items]

    async def create(
        self,
        knowledge_store_id: str,
        source_id: str,
        data: KnowledgeChunkCreate,
        **kwargs: Any,
    ) -> KnowledgeChunk:
        """
        Create a new knowledge chunk.

        Creates a new knowledge chunk in the specified knowledge store and source
        using the provided data asynchronously.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            data: KnowledgeChunkCreate model containing the chunk configuration.
                  Optional fields include 'order', 'text', and 'data'.

        Returns:
            The created KnowledgeChunk object with all fields populated by the API,
            including the generated 'id', 'reference_id', timestamps,
            and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeChunkCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeChunkCreate
            >>> new_chunk = KnowledgeChunkCreate(
            ...     order=1,
            ...     text="This is a paragraph from an article"
            ... )
            >>> chunk = await client.knowledge_chunks.create(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     data=new_chunk
            ... )
            >>> print(chunk.id)
        """
        data = validate_create_update_data(data, KnowledgeChunkCreate)
        path = self._build_base_path(knowledge_store_id, source_id)
        response = await self._client._request("POST", path, data=data, **kwargs)
        return KnowledgeChunk(**response)

    async def get(
        self,
        knowledge_store_id: str,
        source_id: str,
        chunk_id: str,
        **kwargs: Any,
    ) -> KnowledgeChunk:
        """
        Get a knowledge chunk by ID.

        Retrieves a single knowledge chunk by its ObjectId asynchronously within
        the specified knowledge store and source.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            chunk_id: The ObjectId of the chunk to retrieve (24 hex characters).

        Returns:
            The KnowledgeChunk object with all available fields including 'id',
            'order', 'text', 'data', 'disabled', 'reference_id', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the chunk not being found (404),
                             or server errors.

        Example:
            >>> chunk = await client.knowledge_chunks.get(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     chunk_id="507f1f77bcf86cd799439013"
            ... )
            >>> print(f"Chunk: {chunk.text}, Disabled: {chunk.disabled}")
        """
        path = f"{self._build_base_path(knowledge_store_id, source_id)}/{chunk_id}"
        response = await self._client._request("GET", path, **kwargs)
        return KnowledgeChunk(**response)

    async def update(
        self,
        knowledge_store_id: str,
        source_id: str,
        chunk_id: str,
        data: KnowledgeChunkUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> KnowledgeChunk | None:
        """
        Update a knowledge chunk.

        Updates an existing knowledge chunk with the provided data asynchronously.
        Only fields that are set in the KnowledgeChunkUpdate object will be modified.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            chunk_id: The ObjectId of the chunk to update (24 hex characters).
            data: KnowledgeChunkUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'order',
                  'text', 'data', and 'disabled'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated chunk is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated KnowledgeChunk object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the chunk not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeChunkUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeChunkUpdate
            >>> update_data = KnowledgeChunkUpdate(
            ...     text="Updated paragraph text",
            ...     disabled=False
            ... )
            >>> chunk = await client.knowledge_chunks.update(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     chunk_id="507f1f77bcf86cd799439013",
            ...     data=update_data
            ... )
            >>> print(chunk.text)  # "Updated paragraph text"
        """
        data = validate_create_update_data(data, KnowledgeChunkUpdate)
        path = f"{self._build_base_path(knowledge_store_id, source_id)}/{chunk_id}"
        response = await self._client._request("PATCH", path, data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return await self.get(knowledge_store_id, source_id, chunk_id, **kwargs)
            return None
        return KnowledgeChunk(**response)

    async def delete(
        self,
        knowledge_store_id: str,
        source_id: str,
        chunk_id: str,
        **kwargs: Any,
    ) -> None:
        """
        Delete a knowledge chunk.

        Permanently deletes a knowledge chunk by its ObjectId asynchronously.
        This action cannot be undone.

        Args:
            knowledge_store_id: The ObjectId of the knowledge store (24 hex characters).
            source_id: The ObjectId of the knowledge source (24 hex characters).
            chunk_id: The ObjectId of the chunk to delete (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the chunk not being found (404),
                             or server errors.

        Example:
            >>> await client.knowledge_chunks.delete(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     source_id="507f1f77bcf86cd799439012",
            ...     chunk_id="507f1f77bcf86cd799439013"
            ... )
            >>> # Chunk is now deleted
        """
        path = f"{self._build_base_path(knowledge_store_id, source_id)}/{chunk_id}"
        await self._client._request("DELETE", path, **kwargs)
