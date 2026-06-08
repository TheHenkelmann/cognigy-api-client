"""
Nodes resource for the Cognigy Charts API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Chart Nodes via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient
from ..models.node import Node, NodeCreate, NodeMove, NodeUpdate, NodeSearchResult, Chart
from ..validation import validate_create_update_data, build_list_params
from ..pagination import paginate_sync, paginate_async


def _relations_map_from_chart_response(topology_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Build node_id -> {next, children} from GET /flows/{id}/chart ``relations``.

    Keys are normalized to ``str`` so they match ``_id`` / ``id`` from chart/nodes items.
    """
    relations_map: Dict[str, Dict[str, Any]] = {}
    for relation in topology_data.get("relations", []) or []:
        if not isinstance(relation, dict):
            continue
        raw_nid = relation.get("node")
        if not raw_nid:
            continue
        nid = str(raw_nid)
        relations_map[nid] = {
            "next": relation.get("next"),
            "children": list(relation.get("children") or []),
        }
    return relations_map


def _config_node_ids_from_items(configs: List[Dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for cn in configs:
        raw = cn.get("_id") or cn.get("id")
        if raw is not None:
            ids.add(str(raw))
    return ids


class NodesResource:
    """
    Synchronous resource for managing Cognigy Chart Nodes.
    
    Provides methods to list, create, read, update, and delete nodes
    using the Cognigy v2.0 Charts API. Also provides access to the
    full chart topology.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the NodesResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client
        
        
    def search(self, flow_id: str, filter: str, preferred_locale_id: Optional[str] = None, **kwargs: Any) -> List[NodeSearchResult]:
        """
        Search for nodes in a flow.

        Returns matching node ids, reference ids, and match locations (field type and path),
        not full node configuration. Use the node id to fetch full node details if needed.

        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            filter: Filter string to search for.
            preferred_locale_id: ObjectId of the preferred locale (24 hex characters). Default is None.

        Returns:
            List of NodeSearchResult (nodeId, nodeReferenceId, matches).
        """
        params: Dict[str, Any] = {"filter": filter}
        if preferred_locale_id:
            params["preferredLocaleId"] = preferred_locale_id
        # print(f"search params: {params}")
        # print(f"search url: /v2.0/flows/{flow_id}/chart/nodes/search")
        response = self._client._request(
            "GET",
            f"/v2.0/flows/{flow_id}/chart/nodes/search",
            params=params,
            **kwargs,
        )
        return [NodeSearchResult(**item) for item in response.get("items", [])]

    def get_all(self, flow_id: str, **kwargs: Any) -> List[Node]:
        """
        Get all nodes for a flow, merging topology and configuration.
        
        Retrieves all nodes from a flow with their full configuration data
        and topology information (next_node_id, child_node_ids) merged.
        This method makes multiple API calls: paginated ``GET .../chart/nodes`` for
        configurations, then ``GET .../chart`` for topology. **Chart is fetched after**
        all node pages so relations reflect the same revision as the node list (avoids
        stale topology right after creates/moves where an earlier chart read can miss
        new ``relations`` rows while ``chart/nodes`` already lists the new node).
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
        
        Returns:
            List of Node objects with topology information merged.
        
        Raises:
            CognigyAPIError: If the API request fails.
        
        Example:
            >>> nodes = client.nodes.get_all("507f1f77bcf86cd799439011")
            >>> for node in nodes:
            ...     print(f"{node.label}: next={node.next_node_id}, children={node.child_node_ids}")
        """
        # 1. Fetch all node configs first (paginated)
        nodes_configs: List[Dict[str, Any]] = []
        next_cursor = None

        while True:
            params = {"limit": 100}
            if next_cursor:
                params["next"] = next_cursor

            response = self._client._request(
                "GET", f"/v2.0/flows/{flow_id}/chart/nodes", params=params, **kwargs
            )
            items = response.get("items", [])
            nodes_configs.extend(items)

            next_cursor = response.get("nextCursor")
            if not next_cursor or not items:
                break

        # 2. Chart topology after node list so relations match committed chart state
        topology_data = self._client._request(
            "GET", f"/v2.0/flows/{flow_id}/chart", **kwargs
        )
        relations_map = _relations_map_from_chart_response(topology_data)

        # 2b. If API returned a relation set missing rows for some listed nodes, refresh chart once
        listed = _config_node_ids_from_items(nodes_configs)
        if listed and listed - set(relations_map.keys()):
            topology_data = self._client._request(
                "GET", f"/v2.0/flows/{flow_id}/chart", **kwargs
            )
            relations_map = _relations_map_from_chart_response(topology_data)

        # 3. Merge
        result_nodes: List[Node] = []
        for config_node in nodes_configs:
            raw_nid = config_node.get("_id") or config_node.get("id")
            node_id = str(raw_nid) if raw_nid is not None else None

            # Prepare data for model
            node_data = config_node.copy()

            # Inject topology info if available
            if node_id and node_id in relations_map:
                topology = relations_map[node_id]
                node_data["next_node_id"] = topology.get("next")
                node_data["child_node_ids"] = topology.get("children", [])

            result_nodes.append(Node(**node_data))

        return result_nodes

    def list(
        self,
        flow_id: str,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Node]:
        """
        List nodes in a flow with pagination.
        
        Retrieves nodes from the flow without topology merge. Uses cursor-based
        pagination. For nodes with topology information, use get_all() instead.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            limit: Maximum number of nodes to return. If not specified,
                   a default of 1 is used.
            skip: Number of nodes to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of Node objects.
        
        Raises:
            CognigyAPIError: If the API request fails.
        
        Example:
            >>> nodes = client.nodes.list("507f1f77bcf86cd799439011", limit=50)
            >>> for node in nodes:
            ...     print(f"{node.type}: {node.label}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        endpoint = f"/v2.0/flows/{flow_id}/chart/nodes"

        def make_request(p):
            return self._client._request("GET", endpoint, params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Node(**item) for item in items]

    def get(
        self,
        flow_id: str,
        node_id: str,
        include_conversion_metadata: Optional[bool] = None,
        **kwargs: Any,
    ) -> Node:
        """
        Get a single node by ID.
        
        Retrieves detailed information about a specific node in the flow.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node (24 hex characters).
            include_conversion_metadata: If True, includes conversion metadata
                                         in the response showing which fields
                                         were added, removed, or updated.
        
        Returns:
            Node object with full node details.
        
        Raises:
            CognigyAPIError: If the API request fails or node not found.
        
        Example:
            >>> node = client.nodes.get("507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012")
            >>> print(f"Node type: {node.type}, Label: {node.label}")
        """
        params = {}
        if include_conversion_metadata is not None:
            params["includeConversionMetadata"] = include_conversion_metadata
        
        response = self._client._request(
            "GET",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}",
            params=params if params else None,
            **kwargs
        )
        # return response
        return Node(**response)

    def create(self, flow_id: str, data: NodeCreate, **kwargs: Any) -> Node:
        """
        Create a new node in a flow.
        
        Creates a new chart node at the specified position in the flow.
        The node's position is determined by the target and mode parameters
        in the NodeCreate data.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            data: NodeCreate model with node configuration and placement.
                  Must include 'type', 'target', and 'mode'. The 'target'
                  is the ObjectId of the node to attach to, and 'mode'
                  determines the placement (append, prepend, appendChild,
                  prependChild, insertChildAt, insertAfter, insertBefore).
        
        Returns:
            The created Node object with all fields populated
            by the API, including the generated 'id'.
        
        Raises:
            CognigyAPIError: If the API request fails.
            ValidationError: If the NodeCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import NodeCreate
            >>> new_node = NodeCreate(
            ...     type="say",
            ...     target="507f1f77bcf86cd799439012",
            ...     mode="appendChild",
            ...     label="Greeting Node",
            ...     config={"text": "Hello!"}
            ... )
            >>> node = client.nodes.create("507f1f77bcf86cd799439011", new_node)
            >>> print(f"Created node: {node.id}")
        """
        data = validate_create_update_data(data, NodeCreate)
        response = self._client._request(
            "POST",
            f"/v2.0/flows/{flow_id}/chart/nodes",
            data=data,
            **kwargs,
        )
        return Node(**response)

    def move(
        self,
        flow_id: str,
        node_id: str,
        data: NodeMove,
        **kwargs: Any,
    ) -> None:
        """
        Move a node within the flow chart.

        Repositions the node relative to another node using the same placement
        modes as create (append, prepend, appendChild, prependChild,
        insertChildAt, insertAfter, insertBefore). Use ``position`` only with
        ``insertChildAt``.

        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node to move (24 hex characters).
            data: NodeMove with ``target`` (anchor node id) and ``mode``.

        Returns:
            None (API responds with 204 No Content).

        Raises:
            CognigyAPIError: If the API request fails.
            ValidationError: If the NodeMove data fails Pydantic validation.

        Example:
            >>> from cognigy.models import NodeMove
            >>> client.nodes.move(
            ...     "507f1f77bcf86cd799439011",
            ...     "507f1f77bcf86cd799439012",
            ...     NodeMove(target="507f1f77bcf86cd799439013", mode="appendChild"),
            ... )
        """
        data = validate_create_update_data(data, NodeMove)
        self._client._request(
            "POST",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}/move",
            data=data,
            **kwargs,
        )

    def update(
        self,
        flow_id: str,
        node_id: str,
        data: NodeUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Node]:
        """
        Update an existing node.
        
        Updates the specified node with the provided data. Only fields that
        are set in the NodeUpdate object will be modified.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node to update (24 hex characters).
            data: NodeUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'type',
                  'label', 'comment', 'config', 'is_disabled', etc.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated node is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Node object with all fields reflecting
            the changes, or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails or node not found.
            ValidationError: If the NodeUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import NodeUpdate
            >>> update_data = NodeUpdate(
            ...     label="Updated Greeting",
            ...     is_disabled=True
            ... )
            >>> node = client.nodes.update(
            ...     "507f1f77bcf86cd799439011",
            ...     "507f1f77bcf86cd799439012",
            ...     update_data
            ... )
            >>> print(f"Node is now disabled: {node.is_disabled}")
        """
        data = validate_create_update_data(data, NodeUpdate)
        response = self._client._request(
            "PATCH",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}",
            data=data,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return self.get(flow_id, node_id, **kwargs)
            return None
        return Node(**response)

    def delete(self, flow_id: str, node_id: str, **kwargs: Any) -> None:
        """
        Delete a node from a flow.
        
        Permanently removes the specified node from the flow.
        This action cannot be undone.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails or node not found.
        
        Example:
            >>> client.nodes.delete("507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012")
            >>> # Node is now deleted
        """
        self._client._request(
            "DELETE",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}",
            **kwargs,
        )

    def get_chart(self, flow_id: str, **kwargs: Any) -> Chart:
        """
        Get the full chart topology for a flow.
        
        Retrieves the chart containing node summaries and their relationships.
        This provides a lightweight view of the flow structure without full
        node configurations. For full node details with topology merged,
        use get_all() instead.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
        
        Returns:
            Chart object containing nodes (summaries) and relations.
        
        Raises:
            CognigyAPIError: If the API request fails.
        
        Example:
            >>> chart = client.nodes.get_chart("507f1f77bcf86cd799439011")
            >>> print(f"Flow has {len(chart.nodes)} nodes")
            >>> for relation in chart.relations:
            ...     print(f"Node {relation.node} -> next: {relation.next}, children: {relation.children}")
        """
        response = self._client._request("GET", f"/v2.0/flows/{flow_id}/chart", **kwargs)
        return Chart(**response)


class AsyncNodesResource:
    """
    Asynchronous resource for managing Cognigy Chart Nodes.
    
    Provides async methods to list, create, read, update, and delete nodes
    using the Cognigy v2.0 Charts API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncNodesResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def search(self, flow_id: str, filter: str, preferred_locale_id: Optional[str] = None, **kwargs: Any) -> List[NodeSearchResult]:
        """
        Search for nodes in a flow.

        Returns matching node ids, reference ids, and match locations (field type and path),
        not full node configuration. Use the node id to fetch full node details if needed.

        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            filter: Filter string to search for.
            preferred_locale_id: ObjectId of the preferred locale (24 hex characters). Default is None.

        Returns:
            List of NodeSearchResult (nodeId, nodeReferenceId, matches).
        """
        params: Dict[str, Any] = {"filter": filter}
        if preferred_locale_id:
            params["preferredLocaleId"] = preferred_locale_id
        response = await self._client._request(
            "GET",
            f"/v2.0/flows/{flow_id}/chart/nodes/search",
            params=params,
            **kwargs,
        )
        return [NodeSearchResult(**item) for item in response.get("items", [])]

    async def get_all(self, flow_id: str, **kwargs: Any) -> List[Node]:
        """
        Get all nodes for a flow, merging topology and configuration.

        Same ordering as :meth:`NodesResource.get_all`: paginated node configs first,
        then ``GET .../chart`` so relations match the node list revision.
        """
        # 1. Fetch all node configs first (paginated)
        nodes_configs: List[Dict[str, Any]] = []
        next_cursor = None

        while True:
            params = {"limit": 100}
            if next_cursor:
                params["next"] = next_cursor

            response = await self._client._request(
                "GET", f"/v2.0/flows/{flow_id}/chart/nodes", params=params, **kwargs
            )
            items = response.get("items", [])
            nodes_configs.extend(items)

            next_cursor = response.get("nextCursor")
            if not next_cursor or not items:
                break

        # 2. Chart topology after node list
        topology_data = await self._client._request(
            "GET", f"/v2.0/flows/{flow_id}/chart", **kwargs
        )
        relations_map = _relations_map_from_chart_response(topology_data)

        # 2b. Second chart read if relations omit some listed node ids
        listed = _config_node_ids_from_items(nodes_configs)
        if listed and listed - set(relations_map.keys()):
            topology_data = await self._client._request(
                "GET", f"/v2.0/flows/{flow_id}/chart", **kwargs
            )
            relations_map = _relations_map_from_chart_response(topology_data)

        # 3. Merge
        result_nodes: List[Node] = []
        for config_node in nodes_configs:
            raw_nid = config_node.get("_id") or config_node.get("id")
            node_id = str(raw_nid) if raw_nid is not None else None

            node_data = config_node.copy()

            if node_id and node_id in relations_map:
                topology = relations_map[node_id]
                node_data["next_node_id"] = topology.get("next")
                node_data["child_node_ids"] = topology.get("children", [])

            result_nodes.append(Node(**node_data))

        return result_nodes

    async def list(
        self,
        flow_id: str,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Node]:
        """
        List nodes in a flow with pagination.
        
        Retrieves nodes from the flow asynchronously without topology merge.
        Uses cursor-based pagination. For nodes with topology information,
        use get_all() instead.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            limit: Maximum number of nodes to return. If not specified,
                   a default of 1 is used.
            skip: Number of nodes to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of Node objects.
        
        Raises:
            CognigyAPIError: If the API request fails.
        
        Example:
            >>> nodes = await client.nodes.list("507f1f77bcf86cd799439011", limit=50)
            >>> for node in nodes:
            ...     print(f"{node.type}: {node.label}")
        """
        params = build_list_params(
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        endpoint = f"/v2.0/flows/{flow_id}/chart/nodes"

        async def make_request(p):
            return await self._client._request("GET", endpoint, params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Node(**item) for item in items]

    async def get(
        self,
        flow_id: str,
        node_id: str,
        include_conversion_metadata: Optional[bool] = None,
        **kwargs: Any,
    ) -> Node:
        """
        Get a single node by ID.
        
        Retrieves detailed information about a specific node in the flow
        asynchronously.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node (24 hex characters).
            include_conversion_metadata: If True, includes conversion metadata
                                         in the response showing which fields
                                         were added, removed, or updated.
        
        Returns:
            Node object with full node details.
        
        Raises:
            CognigyAPIError: If the API request fails or node not found.
        
        Example:
            >>> node = await client.nodes.get("507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012")
            >>> print(f"Node type: {node.type}, Label: {node.label}")
        """
        params = {}
        if include_conversion_metadata is not None:
            params["includeConversionMetadata"] = include_conversion_metadata
        
        response = await self._client._request(
            "GET",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}",
            params=params if params else None,
            **kwargs,
        )
        return Node(**response)

    async def create(self, flow_id: str, data: NodeCreate, **kwargs: Any) -> Node:
        """
        Create a new node in a flow.
        
        Creates a new chart node at the specified position in the flow
        asynchronously. The node's position is determined by the target
        and mode parameters in the NodeCreate data.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            data: NodeCreate model with node configuration and placement.
                  Must include 'type', 'target', and 'mode'. The 'target'
                  is the ObjectId of the node to attach to, and 'mode'
                  determines the placement (append, prepend, appendChild,
                  prependChild, insertChildAt, insertAfter, insertBefore).
        
        Returns:
            The created Node object with all fields populated
            by the API, including the generated 'id'.
        
        Raises:
            CognigyAPIError: If the API request fails.
            ValidationError: If the NodeCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import NodeCreate
            >>> new_node = NodeCreate(
            ...     type="say",
            ...     target="507f1f77bcf86cd799439012",
            ...     mode="appendChild",
            ...     label="Greeting Node",
            ...     config={"text": "Hello!"}
            ... )
            >>> node = await client.nodes.create("507f1f77bcf86cd799439011", new_node)
            >>> print(f"Created node: {node.id}")
        """
        data = validate_create_update_data(data, NodeCreate)
        response = await self._client._request(
            "POST",
            f"/v2.0/flows/{flow_id}/chart/nodes",
            data=data,
            **kwargs,
        )
        return Node(**response)

    async def move(
        self,
        flow_id: str,
        node_id: str,
        data: NodeMove,
        **kwargs: Any,
    ) -> None:
        """
        Move a node within the flow chart (async).

        Repositions the node relative to another node using the same placement
        modes as create (append, prepend, appendChild, prependChild,
        insertChildAt, insertAfter, insertBefore). Use ``position`` only with
        ``insertChildAt``.

        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node to move (24 hex characters).
            data: NodeMove with ``target`` (anchor node id) and ``mode``.

        Returns:
            None (API responds with 204 No Content).

        Raises:
            CognigyAPIError: If the API request fails.
            ValidationError: If the NodeMove data fails Pydantic validation.

        Example:
            >>> from cognigy.models import NodeMove
            >>> await client.nodes.move(
            ...     "507f1f77bcf86cd799439011",
            ...     "507f1f77bcf86cd799439012",
            ...     NodeMove(target="507f1f77bcf86cd799439013", mode="appendChild"),
            ... )
        """
        data = validate_create_update_data(data, NodeMove)
        await self._client._request(
            "POST",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}/move",
            data=data,
            **kwargs,
        )

    async def update(
        self,
        flow_id: str,
        node_id: str,
        data: NodeUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Node]:
        """
        Update an existing node.

        Updates the specified node with the provided data asynchronously.
        Only fields that are set in the NodeUpdate object will be modified.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node to update (24 hex characters).
            data: NodeUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'type',
                  'label', 'comment', 'config', 'is_disabled', etc.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated node is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Node object with all fields reflecting
            the changes, or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails or node not found.
            ValidationError: If the NodeUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import NodeUpdate
            >>> update_data = NodeUpdate(
            ...     label="Updated Greeting",
            ...     is_disabled=True
            ... )
            >>> node = await client.nodes.update(
            ...     "507f1f77bcf86cd799439011",
            ...     "507f1f77bcf86cd799439012",
            ...     update_data
            ... )
            >>> print(f"Node is now disabled: {node.is_disabled}")
        """
        data = validate_create_update_data(data, NodeUpdate)
        response = await self._client._request(
            "PATCH",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}",
            data=data,
            **kwargs,
        )
        if response is None:
            if fetch_updated:
                return await self.get(flow_id, node_id, **kwargs)
            return None
        return Node(**response)

    async def delete(self, flow_id: str, node_id: str, **kwargs: Any) -> None:
        """
        Delete a node from a flow.
        
        Permanently removes the specified node from the flow asynchronously.
        This action cannot be undone.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
            node_id: ObjectId of the node to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails or node not found.
        
        Example:
            >>> await client.nodes.delete("507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012")
            >>> # Node is now deleted
        """
        await self._client._request(
            "DELETE",
            f"/v2.0/flows/{flow_id}/chart/nodes/{node_id}",
            **kwargs,
        )

    async def get_chart(self, flow_id: str, **kwargs: Any) -> Chart:
        """
        Get the full chart topology for a flow.
        
        Retrieves the chart containing node summaries and their relationships
        asynchronously. This provides a lightweight view of the flow structure
        without full node configurations. For full node details with topology
        merged, use get_all() instead.
        
        Args:
            flow_id: ObjectId of the flow (24 hex characters).
        
        Returns:
            Chart object containing nodes (summaries) and relations.
        
        Raises:
            CognigyAPIError: If the API request fails.
        
        Example:
            >>> chart = await client.nodes.get_chart("507f1f77bcf86cd799439011")
            >>> print(f"Flow has {len(chart.nodes)} nodes")
            >>> for relation in chart.relations:
            ...     print(f"Node {relation.node} -> next: {relation.next}, children: {relation.children}")
        """
        response = await self._client._request("GET", f"/v2.0/flows/{flow_id}/chart", **kwargs)
        return Chart(**response)
