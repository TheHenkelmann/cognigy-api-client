"""
Knowledge Connectors resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Knowledge Connectors via the v2.0 API endpoints.
Knowledge Connectors integrate external data sources with Knowledge Stores.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient
import builtins

from ..models.knowledge_connector import (
    KnowledgeConnector,
    KnowledgeConnectorCreate,
    KnowledgeConnectorUpdate,
)
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data


class KnowledgeConnectorsResource:
    """
    Synchronous resource for managing Cognigy Knowledge Connectors.

    Provides methods to list, create, read, update, and delete Knowledge Connectors
    using the Cognigy v2.0 API. Knowledge Connectors are scoped to a Knowledge Store.

    Attributes:
        _client: The CognigyClient instance used for API requests.
    """

    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the KnowledgeConnectorsResource.

        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list(
        self,
        knowledge_store_id: str,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[KnowledgeConnector]:
        """
        List Knowledge Connectors in a Knowledge Store.

        Retrieves a list of Knowledge Connectors from the Cognigy API.
        Results can be paginated using the provided parameters.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            limit: Maximum number of connectors to return. If not specified,
                   uses the API default.
            skip: Number of connectors to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of KnowledgeConnector objects in the specified Knowledge Store.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> connectors = client.knowledge_connectors.list(
            ...     knowledge_store_id="507f1f77bcf86cd799439011"
            ... )
            >>> for connector in connectors:
            ...     print(f"{connector.name}: {connector.last_execution_status}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        endpoint = f"/v2.0/knowledgestores/{knowledge_store_id}/connectors"

        def make_request(p):
            return self._client._request("GET", endpoint, params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [KnowledgeConnector(**item) for item in items]

    def create(
        self,
        knowledge_store_id: str,
        data: KnowledgeConnectorCreate,
        **kwargs: Any,
    ) -> KnowledgeConnector:
        """
        Create a new Knowledge Connector.

        Creates a new Knowledge Connector in the specified Knowledge Store.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            data: KnowledgeConnectorCreate model containing the connector configuration.
                  Fields include 'extension', 'version', 'type', 'config', 'name',
                  and 'schedule'.

        Returns:
            The created KnowledgeConnector object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeConnectorCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeConnectorCreate, ConnectorSchedule
            >>> schedule = ConnectorSchedule(
            ...     enabled=True,
            ...     hour=2,
            ...     minute=0,
            ...     week_days=[0, 2, 4]  # Monday, Wednesday, Friday
            ... )
            >>> new_connector = KnowledgeConnectorCreate(
            ...     name="Confluence Sync",
            ...     extension="confluence",
            ...     version="1.1.0",
            ...     type="MyConfluenceConnector",
            ...     config={"baseUrl": "https://wiki.example.com"},
            ...     schedule=schedule
            ... )
            >>> connector = client.knowledge_connectors.create(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     data=new_connector
            ... )
            >>> print(connector.id)
        """
        data = validate_create_update_data(data, KnowledgeConnectorCreate)
        response = self._client._request(
            "POST",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors",
            data=data,
            **kwargs,
        )
        return KnowledgeConnector(**response)

    def get(
        self,
        knowledge_store_id: str,
        connector_id: str,
        **kwargs: Any,
    ) -> KnowledgeConnector:
        """
        Get a Knowledge Connector by ID.

        Retrieves a single Knowledge Connector by its ObjectId.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            connector_id: The ObjectId of the Knowledge Connector to retrieve
                          (24 hex characters).

        Returns:
            The KnowledgeConnector object with all available fields including
            'id', 'name', 'extension', 'version', 'type', 'config', 'schedule',
            'last_execution', 'last_execution_status', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the connector not being found (404),
                             or server errors.

        Example:
            >>> connector = client.knowledge_connectors.get(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     connector_id="60a1b2c3d4e5f6a7b8c9d0e1"
            ... )
            >>> print(f"Connector: {connector.name}")
            >>> print(f"Last status: {connector.last_execution_status}")
        """
        data = self._client._request(
            "GET",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors/{connector_id}",
            **kwargs,
        )
        return KnowledgeConnector(**data)

    def update(
        self,
        knowledge_store_id: str,
        connector_id: str,
        data: KnowledgeConnectorUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> KnowledgeConnector | None:
        """
        Update a Knowledge Connector.

        Updates an existing Knowledge Connector with the provided data.
        Only fields that are set in the KnowledgeConnectorUpdate object will be modified.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            connector_id: The ObjectId of the Knowledge Connector to update
                          (24 hex characters).
            data: KnowledgeConnectorUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'config', 'name',
                  and 'schedule'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated connector is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated KnowledgeConnector object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the connector not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeConnectorUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeConnectorUpdate, ConnectorSchedule
            >>> update_data = KnowledgeConnectorUpdate(
            ...     name="Updated Confluence Sync",
            ...     schedule=ConnectorSchedule(enabled=False)
            ... )
            >>> connector = client.knowledge_connectors.update(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     connector_id="60a1b2c3d4e5f6a7b8c9d0e1",
            ...     data=update_data
            ... )
            >>> print(connector.name)  # "Updated Confluence Sync"
        """
        data = validate_create_update_data(data, KnowledgeConnectorUpdate)
        response = self._client._request(
            "PATCH",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors/{connector_id}",
            data=data,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return self.get(knowledge_store_id, connector_id, **kwargs)
            return None
        return KnowledgeConnector(**response)

    def delete(
        self,
        knowledge_store_id: str,
        connector_id: str,
        **kwargs: Any,
    ) -> None:
        """
        Delete a Knowledge Connector.

        Permanently deletes a Knowledge Connector by its ObjectId.
        This action cannot be undone.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            connector_id: The ObjectId of the Knowledge Connector to delete
                          (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the connector not being found (404),
                             or server errors.

        Example:
            >>> client.knowledge_connectors.delete(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     connector_id="60a1b2c3d4e5f6a7b8c9d0e1"
            ... )
            >>> # Connector is now deleted
        """
        self._client._request(
            "DELETE",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors/{connector_id}",
            **kwargs,
        )


class AsyncKnowledgeConnectorsResource:
    """
    Asynchronous resource for managing Cognigy Knowledge Connectors.

    Provides async methods to list, create, read, update, and delete Knowledge Connectors
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations. Knowledge Connectors are scoped to a Knowledge Store.

    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """

    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncKnowledgeConnectorsResource.

        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list(
        self,
        knowledge_store_id: str,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[KnowledgeConnector]:
        """
        List Knowledge Connectors in a Knowledge Store.

        Retrieves a list of Knowledge Connectors from the Cognigy API asynchronously.
        Results can be paginated using the provided parameters.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            limit: Maximum number of connectors to return. If not specified,
                   uses the API default.
            skip: Number of connectors to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of KnowledgeConnector objects in the specified Knowledge Store.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> connectors = await client.knowledge_connectors.list(
            ...     knowledge_store_id="507f1f77bcf86cd799439011"
            ... )
            >>> for connector in connectors:
            ...     print(f"{connector.name}: {connector.last_execution_status}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        endpoint = f"/v2.0/knowledgestores/{knowledge_store_id}/connectors"

        async def make_request(p):
            return await self._client._request("GET", endpoint, params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [KnowledgeConnector(**item) for item in items]

    async def create(
        self,
        knowledge_store_id: str,
        data: KnowledgeConnectorCreate,
        **kwargs: Any,
    ) -> KnowledgeConnector:
        """
        Create a new Knowledge Connector.

        Creates a new Knowledge Connector in the specified Knowledge Store asynchronously.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            data: KnowledgeConnectorCreate model containing the connector configuration.
                  Fields include 'extension', 'version', 'type', 'config', 'name',
                  and 'schedule'.

        Returns:
            The created KnowledgeConnector object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the KnowledgeConnectorCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeConnectorCreate, ConnectorSchedule
            >>> schedule = ConnectorSchedule(
            ...     enabled=True,
            ...     hour=2,
            ...     minute=0,
            ...     week_days=[0, 2, 4]  # Monday, Wednesday, Friday
            ... )
            >>> new_connector = KnowledgeConnectorCreate(
            ...     name="Confluence Sync",
            ...     extension="confluence",
            ...     version="1.1.0",
            ...     type="MyConfluenceConnector",
            ...     config={"baseUrl": "https://wiki.example.com"},
            ...     schedule=schedule
            ... )
            >>> connector = await client.knowledge_connectors.create(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     data=new_connector
            ... )
            >>> print(connector.id)
        """
        data = validate_create_update_data(data, KnowledgeConnectorCreate)
        response = await self._client._request(
            "POST",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors",
            data=data,
            **kwargs,
        )
        return KnowledgeConnector(**response)

    async def get(
        self,
        knowledge_store_id: str,
        connector_id: str,
        **kwargs: Any,
    ) -> KnowledgeConnector:
        """
        Get a Knowledge Connector by ID.

        Retrieves a single Knowledge Connector by its ObjectId asynchronously.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            connector_id: The ObjectId of the Knowledge Connector to retrieve
                          (24 hex characters).

        Returns:
            The KnowledgeConnector object with all available fields including
            'id', 'name', 'extension', 'version', 'type', 'config', 'schedule',
            'last_execution', 'last_execution_status', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the connector not being found (404),
                             or server errors.

        Example:
            >>> connector = await client.knowledge_connectors.get(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     connector_id="60a1b2c3d4e5f6a7b8c9d0e1"
            ... )
            >>> print(f"Connector: {connector.name}")
            >>> print(f"Last status: {connector.last_execution_status}")
        """
        data = await self._client._request(
            "GET",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors/{connector_id}",
            **kwargs,
        )
        return KnowledgeConnector(**data)

    async def update(
        self,
        knowledge_store_id: str,
        connector_id: str,
        data: KnowledgeConnectorUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> KnowledgeConnector | None:
        """
        Update a Knowledge Connector.

        Updates an existing Knowledge Connector with the provided data asynchronously.
        Only fields that are set in the KnowledgeConnectorUpdate object will be modified.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            connector_id: The ObjectId of the Knowledge Connector to update
                          (24 hex characters).
            data: KnowledgeConnectorUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'config', 'name',
                  and 'schedule'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated connector is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated KnowledgeConnector object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the connector not being found (404),
                             validation errors, or server errors.
            ValidationError: If the KnowledgeConnectorUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import KnowledgeConnectorUpdate, ConnectorSchedule
            >>> update_data = KnowledgeConnectorUpdate(
            ...     name="Updated Confluence Sync",
            ...     schedule=ConnectorSchedule(enabled=False)
            ... )
            >>> connector = await client.knowledge_connectors.update(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     connector_id="60a1b2c3d4e5f6a7b8c9d0e1",
            ...     data=update_data
            ... )
            >>> print(connector.name)  # "Updated Confluence Sync"
        """
        data = validate_create_update_data(data, KnowledgeConnectorUpdate)
        response = await self._client._request(
            "PATCH",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors/{connector_id}",
            data=data,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return await self.get(knowledge_store_id, connector_id, **kwargs)
            return None
        return KnowledgeConnector(**response)

    async def delete(
        self,
        knowledge_store_id: str,
        connector_id: str,
        **kwargs: Any,
    ) -> None:
        """
        Delete a Knowledge Connector.

        Permanently deletes a Knowledge Connector by its ObjectId asynchronously.
        This action cannot be undone.

        Args:
            knowledge_store_id: The ObjectId of the Knowledge Store (24 hex characters).
            connector_id: The ObjectId of the Knowledge Connector to delete
                          (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the connector not being found (404),
                             or server errors.

        Example:
            >>> await client.knowledge_connectors.delete(
            ...     knowledge_store_id="507f1f77bcf86cd799439011",
            ...     connector_id="60a1b2c3d4e5f6a7b8c9d0e1"
            ... )
            >>> # Connector is now deleted
        """
        await self._client._request(
            "DELETE",
            f"/v2.0/knowledgestores/{knowledge_store_id}/connectors/{connector_id}",
            **kwargs,
        )
