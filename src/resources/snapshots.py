"""
Snapshots resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Snapshots via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient

import builtins

from ..models.snapshot import (
    Snapshot,
    SnapshotCreate,
    SnapshotDownloadLink,
    SnapshotDownloadLinkRequest,
    SnapshotResource,
    SnapshotRestoreRequest,
)
from ..models.task import Task
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data


class SnapshotsResource:
    """
    Synchronous resource for managing Cognigy Snapshots.

    Provides methods to list, create, read, and delete snapshots,
    as well as additional operations like packaging, downloading,
    and restoring snapshots using the Cognigy v2.0 API.

    Note that many snapshot operations (create, delete, package, restore)
    create background Tasks that perform the actual work asynchronously.

    Attributes:
        _client: The CognigyClient instance used for API requests.
    """

    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the SnapshotsResource.

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
    ) -> builtins.list[Snapshot]:
        """
        List snapshots with optional filtering and pagination.

        Retrieves a list of snapshots from the Cognigy API. Results can be filtered
        and paginated using the provided parameters.

        Args:
            project_id: Filter snapshots by project ObjectId (24 hex characters).
            filter: Filter string for searching snapshots by name.
            limit: Maximum number of snapshots to return. If not specified,
                   uses the API default.
            skip: Number of snapshots to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of Snapshot objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> snapshots = client.snapshots.list(project_id="507f1f77bcf86cd799439011")
            >>> for snapshot in snapshots:
            ...     print(f"{snapshot.name}: packaged={snapshot.is_packaged}")
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
            return self._client._request("GET", "/v2.0/snapshots", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Snapshot(**item) for item in items]

    def create(self, data: SnapshotCreate, **kwargs: Any) -> Task:
        """
        Create a new snapshot.

        Creates a background Task to create a new snapshot from the specified project.
        The snapshot creation is performed asynchronously.

        Args:
            data: SnapshotCreate model containing the snapshot configuration.
                  Must include 'project_id'. Optional fields include 'name'
                  and 'description'.

        Returns:
            A Task object representing the background snapshot creation job.
            Monitor the task status to know when the snapshot is ready.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the SnapshotCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import SnapshotCreate
            >>> new_snapshot = SnapshotCreate(
            ...     name="Version 1.0",
            ...     description="Production release",
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> task = client.snapshots.create(new_snapshot)
            >>> print(f"Task ID: {task.id}, Status: {task.status}")
        """
        data = validate_create_update_data(data, SnapshotCreate)
        response = self._client._request("POST", "/v2.0/snapshots", data=data, **kwargs)
        return Task(**response)

    def get(self, snapshot_id: str, **kwargs: Any) -> Snapshot:
        """
        Get a snapshot by ID.

        Retrieves a single snapshot by its ObjectId.

        Args:
            snapshot_id: The ObjectId of the snapshot to retrieve (24 hex characters).

        Returns:
            The Snapshot object with all available fields including 'id', 'name',
            'description', 'is_packaged', 'package_expires_at', 'hash',
            'created_by', and 'created_at'.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> snapshot = client.snapshots.get("507f1f77bcf86cd799439011")
            >>> print(f"Snapshot: {snapshot.name}, Hash: {snapshot.hash}")
        """
        data = self._client._request("GET", f"/v2.0/snapshots/{snapshot_id}", **kwargs)
        return Snapshot(**data)

    def delete(self, snapshot_id: str, **kwargs: Any) -> Task:
        """
        Delete a snapshot.

        Creates a background Task to delete a snapshot by its ObjectId.
        The deletion is performed asynchronously.

        Args:
            snapshot_id: The ObjectId of the snapshot to delete (24 hex characters).

        Returns:
            A Task object representing the background deletion job.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> task = client.snapshots.delete("507f1f77bcf86cd799439011")
            >>> print(f"Deletion task started: {task.id}")
        """
        response = self._client._request("DELETE", f"/v2.0/snapshots/{snapshot_id}", **kwargs)
        return Task(**response)

    def get_resources(
        self,
        snapshot_id: str,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[SnapshotResource]:
        """
        Get resources contained in a snapshot.

        Retrieves a list of resources (flows, lexicons, etc.) that are
        included in the specified snapshot.

        Args:
            snapshot_id: The ObjectId of the snapshot (24 hex characters).
            limit: Maximum number of resources to return.
            skip: Number of resources to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
            previous_cursor: Cursor for fetching the previous page of results.

        Returns:
            List of SnapshotResource objects representing the resources
            included in the snapshot.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> resources = client.snapshots.get_resources("507f1f77bcf86cd799439011")
            >>> for resource in resources:
            ...     print(f"{resource.name} ({resource.resource_type})")
        """
        params: dict[str, Any] = {}
        if limit:
            params["limit"] = limit
        if skip:
            params["skip"] = skip
        if sort:
            params["sort"] = sort
        if next_cursor:
            params["next"] = next_cursor
        if previous_cursor:
            params["previous"] = previous_cursor

        data = self._client._request(
            "GET",
            f"/v2.0/snapshots/{snapshot_id}/resources",
            params=params if params else None,
            **kwargs,
        )
        return [SnapshotResource(**item) for item in data.get("items", [])]

    def package(self, snapshot_id: str, **kwargs: Any) -> Task:
        """
        Package a snapshot for download.

        Creates a background Task to package a snapshot, making it available
        for download. The packaging is performed asynchronously.

        Args:
            snapshot_id: The ObjectId of the snapshot to package (24 hex characters).

        Returns:
            A Task object representing the background packaging job.
            Once complete, the snapshot's 'is_packaged' will be True.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> task = client.snapshots.package("507f1f77bcf86cd799439011")
            >>> print(f"Packaging task started: {task.id}")
        """
        response = self._client._request("POST", f"/v2.0/snapshots/{snapshot_id}/package", **kwargs)
        return Task(**response)

    def create_download_link(
        self,
        snapshot_id: str,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> SnapshotDownloadLink:
        """
        Create a download link for a packaged snapshot.

        Generates a temporary download URL for the snapshot package.
        The snapshot must be packaged first using the package() method.

        Args:
            snapshot_id: The ObjectId of the snapshot (24 hex characters).
            project_id: Optional ObjectId of the project (24 hex characters).

        Returns:
            A SnapshotDownloadLink object containing the download URL.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             the snapshot not being packaged, or server errors.

        Example:
            >>> link = client.snapshots.create_download_link("507f1f77bcf86cd799439011")
            >>> print(f"Download URL: {link.download_link}")
        """
        request_data = SnapshotDownloadLinkRequest(project_id=project_id) if project_id else None
        response = self._client._request(
            "POST",
            f"/v2.0/snapshots/{snapshot_id}/downloadlink",
            data=request_data,
            **kwargs,
        )
        return SnapshotDownloadLink(**response)

    def restore(self, snapshot_id: str, project_id: str, **kwargs: Any) -> Task:
        """
        Restore a snapshot to a project.

        Creates a background Task to restore a snapshot to the specified project.
        The restoration is performed asynchronously.

        Warning: Restoring a snapshot will replace the project's current resources
        with those from the snapshot.

        Args:
            snapshot_id: The ObjectId of the snapshot to restore (24 hex characters).
            project_id: The ObjectId of the target project (24 hex characters).

        Returns:
            A Task object representing the background restoration job.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> task = client.snapshots.restore(
            ...     snapshot_id="507f1f77bcf86cd799439011",
            ...     project_id="507f1f77bcf86cd799439022"
            ... )
            >>> print(f"Restoration task started: {task.id}")
        """
        request_data = SnapshotRestoreRequest(project_id=project_id)
        response = self._client._request(
            "POST",
            f"/v2.0/snapshots/{snapshot_id}/restore",
            data=request_data,
            **kwargs,
        )
        return Task(**response)


class AsyncSnapshotsResource:
    """
    Asynchronous resource for managing Cognigy Snapshots.

    Provides async methods to list, create, read, and delete snapshots,
    as well as additional operations like packaging, downloading,
    and restoring snapshots using the Cognigy v2.0 API.

    Note that many snapshot operations (create, delete, package, restore)
    create background Tasks that perform the actual work asynchronously.

    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """

    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncSnapshotsResource.

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
    ) -> builtins.list[Snapshot]:
        """
        List snapshots with optional filtering and pagination.

        Retrieves a list of snapshots from the Cognigy API asynchronously.
        Results can be filtered and paginated using the provided parameters.

        Args:
            project_id: Filter snapshots by project ObjectId (24 hex characters).
            filter: Filter string for searching snapshots by name.
            limit: Maximum number of snapshots to return. If not specified,
                   uses the API default.
            skip: Number of snapshots to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of Snapshot objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> snapshots = await client.snapshots.list(project_id="507f1f77bcf86cd799439011")
            >>> for snapshot in snapshots:
            ...     print(f"{snapshot.name}: packaged={snapshot.is_packaged}")
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
            return await self._client._request("GET", "/v2.0/snapshots", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Snapshot(**item) for item in items]

    async def create(self, data: SnapshotCreate, **kwargs: Any) -> Task:
        """
        Create a new snapshot.

        Creates a background Task to create a new snapshot from the specified project
        asynchronously. The snapshot creation is performed as a background job.

        Args:
            data: SnapshotCreate model containing the snapshot configuration.
                  Must include 'project_id'. Optional fields include 'name'
                  and 'description'.

        Returns:
            A Task object representing the background snapshot creation job.
            Monitor the task status to know when the snapshot is ready.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the SnapshotCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import SnapshotCreate
            >>> new_snapshot = SnapshotCreate(
            ...     name="Version 1.0",
            ...     description="Production release",
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> task = await client.snapshots.create(new_snapshot)
            >>> print(f"Task ID: {task.id}, Status: {task.status}")
        """
        data = validate_create_update_data(data, SnapshotCreate)
        response = await self._client._request("POST", "/v2.0/snapshots", data=data, **kwargs)
        return Task(**response)

    async def get(self, snapshot_id: str, **kwargs: Any) -> Snapshot:
        """
        Get a snapshot by ID.

        Retrieves a single snapshot by its ObjectId asynchronously.

        Args:
            snapshot_id: The ObjectId of the snapshot to retrieve (24 hex characters).

        Returns:
            The Snapshot object with all available fields including 'id', 'name',
            'description', 'is_packaged', 'package_expires_at', 'hash',
            'created_by', and 'created_at'.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> snapshot = await client.snapshots.get("507f1f77bcf86cd799439011")
            >>> print(f"Snapshot: {snapshot.name}, Hash: {snapshot.hash}")
        """
        data = await self._client._request("GET", f"/v2.0/snapshots/{snapshot_id}", **kwargs)
        return Snapshot(**data)

    async def delete(self, snapshot_id: str, **kwargs: Any) -> Task:
        """
        Delete a snapshot.

        Creates a background Task to delete a snapshot by its ObjectId asynchronously.
        The deletion is performed as a background job.

        Args:
            snapshot_id: The ObjectId of the snapshot to delete (24 hex characters).

        Returns:
            A Task object representing the background deletion job.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> task = await client.snapshots.delete("507f1f77bcf86cd799439011")
            >>> print(f"Deletion task started: {task.id}")
        """
        response = await self._client._request("DELETE", f"/v2.0/snapshots/{snapshot_id}", **kwargs)
        return Task(**response)

    async def get_resources(
        self,
        snapshot_id: str,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[SnapshotResource]:
        """
        Get resources contained in a snapshot.

        Retrieves a list of resources (flows, lexicons, etc.) that are
        included in the specified snapshot asynchronously.

        Args:
            snapshot_id: The ObjectId of the snapshot (24 hex characters).
            limit: Maximum number of resources to return.
            skip: Number of resources to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
            previous_cursor: Cursor for fetching the previous page of results.

        Returns:
            List of SnapshotResource objects representing the resources
            included in the snapshot.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> resources = await client.snapshots.get_resources("507f1f77bcf86cd799439011")
            >>> for resource in resources:
            ...     print(f"{resource.name} ({resource.resource_type})")
        """
        params: dict[str, Any] = {}
        if limit:
            params["limit"] = limit
        if skip:
            params["skip"] = skip
        if sort:
            params["sort"] = sort
        if next_cursor:
            params["next"] = next_cursor
        if previous_cursor:
            params["previous"] = previous_cursor

        data = await self._client._request(
            "GET",
            f"/v2.0/snapshots/{snapshot_id}/resources",
            params=params if params else None,
            **kwargs,
        )
        return [SnapshotResource(**item) for item in data.get("items", [])]

    async def package(self, snapshot_id: str, **kwargs: Any) -> Task:
        """
        Package a snapshot for download.

        Creates a background Task to package a snapshot asynchronously,
        making it available for download.

        Args:
            snapshot_id: The ObjectId of the snapshot to package (24 hex characters).

        Returns:
            A Task object representing the background packaging job.
            Once complete, the snapshot's 'is_packaged' will be True.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> task = await client.snapshots.package("507f1f77bcf86cd799439011")
            >>> print(f"Packaging task started: {task.id}")
        """
        response = await self._client._request(
            "POST", f"/v2.0/snapshots/{snapshot_id}/package", **kwargs
        )
        return Task(**response)

    async def create_download_link(
        self,
        snapshot_id: str,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> SnapshotDownloadLink:
        """
        Create a download link for a packaged snapshot.

        Generates a temporary download URL for the snapshot package asynchronously.
        The snapshot must be packaged first using the package() method.

        Args:
            snapshot_id: The ObjectId of the snapshot (24 hex characters).
            project_id: Optional ObjectId of the project (24 hex characters).

        Returns:
            A SnapshotDownloadLink object containing the download URL.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             the snapshot not being packaged, or server errors.

        Example:
            >>> link = await client.snapshots.create_download_link("507f1f77bcf86cd799439011")
            >>> print(f"Download URL: {link.download_link}")
        """
        request_data = SnapshotDownloadLinkRequest(project_id=project_id) if project_id else None
        response = await self._client._request(
            "POST",
            f"/v2.0/snapshots/{snapshot_id}/downloadlink",
            data=request_data,
            **kwargs,
        )
        return SnapshotDownloadLink(**response)

    async def restore(self, snapshot_id: str, project_id: str, **kwargs: Any) -> Task:
        """
        Restore a snapshot to a project.

        Creates a background Task to restore a snapshot to the specified project
        asynchronously. The restoration is performed as a background job.

        Warning: Restoring a snapshot will replace the project's current resources
        with those from the snapshot.

        Args:
            snapshot_id: The ObjectId of the snapshot to restore (24 hex characters).
            project_id: The ObjectId of the target project (24 hex characters).

        Returns:
            A Task object representing the background restoration job.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the snapshot not being found (404),
                             or server errors.

        Example:
            >>> task = await client.snapshots.restore(
            ...     snapshot_id="507f1f77bcf86cd799439011",
            ...     project_id="507f1f77bcf86cd799439022"
            ... )
            >>> print(f"Restoration task started: {task.id}")
        """
        request_data = SnapshotRestoreRequest(project_id=project_id)
        response = await self._client._request(
            "POST",
            f"/v2.0/snapshots/{snapshot_id}/restore",
            data=request_data,
            **kwargs,
        )
        return Task(**response)
