"""
Tasks resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Tasks via the v2.0 API endpoints.

Tasks represent asynchronous operations in the Cognigy system. They are
typically created by other API operations (like imports, exports, training)
and can be monitored and cancelled through this resource.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient

from ..models.task import Task
from ..validation import build_list_params
from ..pagination import paginate_sync, paginate_async


class TasksResource:
    """
    Synchronous resource for managing Cognigy Tasks.
    
    Provides methods to list, retrieve, and cancel tasks
    using the Cognigy v2.0 API.
    
    Tasks are asynchronous operations that run in the background.
    They are created by other API operations and this resource
    allows monitoring and cancellation.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    
    Example:
        >>> # List all active tasks
        >>> tasks = client.tasks.list()
        >>> for task in tasks:
        ...     if task.is_running:
        ...         print(f"{task.name}: {task.progress_percent}%")
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the TasksResource.
        
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
    ) -> List[Task]:
        """
        List tasks with optional pagination.
        
        Retrieves a list of tasks from the Cognigy API. Results can be
        paginated using the provided parameters.
        
        Args:
            filter: Filter string for searching tasks (e.g. by name).
            limit: Maximum number of tasks to return. If not specified,
                   uses the API default.
            skip: Number of tasks to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
            project_id: The ObjectId of the project (24 hex characters, optional).
                        If provided, restricts results to tasks for that project.
        
        Returns:
            List of Task objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> # Get all tasks
            >>> tasks = client.tasks.list()
            >>> for task in tasks:
            ...     print(f"{task.name}: {task.status.value}")
            
            >>> # Get running tasks for a project, sorted by creation date
            >>> tasks = client.tasks.list(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     sort="-createdAt",
            ...     limit=10
            ... )
            >>> running = [t for t in tasks if t.is_running]
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
            return self._client._request("GET", "/v2.0/tasks", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Task(**item) for item in items]

    def get(self, task_id: str, **kwargs: Any) -> Task:
        """
        Get a task by ID.
        
        Retrieves a single task by its ObjectId.
        
        Args:
            task_id: The ObjectId of the task to retrieve (24 hex characters).
        
        Returns:
            The Task object with all available fields including status,
            progress information, and metadata.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the task not being found (404),
                             or server errors.
        
        Example:
            >>> task = client.tasks.get("507f1f77bcf86cd799439011")
            >>> print(f"Task: {task.name}")
            >>> print(f"Status: {task.status.value}")
            >>> if task.progress_percent is not None:
            ...     print(f"Progress: {task.progress_percent:.1f}%")
            >>> if task.fail_reason:
            ...     print(f"Error: {task.fail_reason}")
        """
        data = self._client._request("GET", f"/v2.0/tasks/{task_id}", **kwargs)
        return Task(**data)

    def cancel(self, task_id: str, **kwargs: Any) -> None:
        """
        Cancel a task.
        
        Requests cancellation of a running task. The task will transition
        to 'cancelling' status and then to 'cancelled' once the operation
        completes. Not all tasks support cancellation.
        
        Args:
            task_id: The ObjectId of the task to cancel (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the task not being found (404),
                             or if the task cannot be cancelled.
        
        Note:
            Cancellation is asynchronous. After calling this method,
            poll the task status using get() to confirm cancellation.
        
        Example:
            >>> # Cancel a task and wait for completion
            >>> client.tasks.cancel("507f1f77bcf86cd799439011")
            >>> 
            >>> import time
            >>> while True:
            ...     task = client.tasks.get("507f1f77bcf86cd799439011")
            ...     if task.is_complete:
            ...         print(f"Task ended with status: {task.status.value}")
            ...         break
            ...     time.sleep(1)
        """
        self._client._request("POST", f"/v2.0/tasks/{task_id}/cancel", **kwargs)


class AsyncTasksResource:
    """
    Asynchronous resource for managing Cognigy Tasks.
    
    Provides async methods to list, retrieve, and cancel tasks
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    Tasks are asynchronous operations that run in the background.
    They are created by other API operations and this resource
    allows monitoring and cancellation.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    
    Example:
        >>> # List all active tasks
        >>> tasks = await client.tasks.list()
        >>> for task in tasks:
        ...     if task.is_running:
        ...         print(f"{task.name}: {task.progress_percent}%")
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncTasksResource.
        
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
    ) -> List[Task]:
        """
        List tasks with optional pagination.

        Retrieves a list of tasks from the Cognigy API asynchronously.
        Results can be paginated using the provided parameters.
        
        Args:
            filter: Filter string for searching tasks (e.g. by name).
            limit: Maximum number of tasks to return. If not specified,
                   uses the API default.
            skip: Number of tasks to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
            project_id: The ObjectId of the project (24 hex characters, optional).
                        If provided, restricts results to tasks for that project.
        
        Returns:
            List of Task objects matching the query parameters.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> # Get all tasks
            >>> tasks = await client.tasks.list()
            >>> for task in tasks:
            ...     print(f"{task.name}: {task.status.value}")
            
            >>> # Get running tasks for a project, sorted by creation date
            >>> tasks = await client.tasks.list(
            ...     project_id="507f1f77bcf86cd799439011",
            ...     sort="-createdAt",
            ...     limit=10
            ... )
            >>> running = [t for t in tasks if t.is_running]
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
            return await self._client._request("GET", "/v2.0/tasks", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Task(**item) for item in items]

    async def get(self, task_id: str, **kwargs: Any) -> Task:
        """
        Get a task by ID.
        
        Retrieves a single task by its ObjectId asynchronously.
        
        Args:
            task_id: The ObjectId of the task to retrieve (24 hex characters).
        
        Returns:
            The Task object with all available fields including status,
            progress information, and metadata.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the task not being found (404),
                             or server errors.
        
        Example:
            >>> task = await client.tasks.get("507f1f77bcf86cd799439011")
            >>> print(f"Task: {task.name}")
            >>> print(f"Status: {task.status.value}")
            >>> if task.progress_percent is not None:
            ...     print(f"Progress: {task.progress_percent:.1f}%")
            >>> if task.fail_reason:
            ...     print(f"Error: {task.fail_reason}")
        """
        data = await self._client._request("GET", f"/v2.0/tasks/{task_id}", **kwargs)
        return Task(**data)

    async def cancel(self, task_id: str, **kwargs: Any) -> None:
        """
        Cancel a task.
        
        Requests cancellation of a running task asynchronously. The task 
        will transition to 'cancelling' status and then to 'cancelled' 
        once the operation completes. Not all tasks support cancellation.
        
        Args:
            task_id: The ObjectId of the task to cancel (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the task not being found (404),
                             or if the task cannot be cancelled.
        
        Note:
            Cancellation is asynchronous. After calling this method,
            poll the task status using get() to confirm cancellation.
        
        Example:
            >>> import asyncio
            >>> 
            >>> # Cancel a task and wait for completion
            >>> await client.tasks.cancel("507f1f77bcf86cd799439011")
            >>> 
            >>> while True:
            ...     task = await client.tasks.get("507f1f77bcf86cd799439011")
            ...     if task.is_complete:
            ...         print(f"Task ended with status: {task.status.value}")
            ...         break
            ...     await asyncio.sleep(1)
        """
        await self._client._request("POST", f"/v2.0/tasks/{task_id}/cancel", **kwargs)
