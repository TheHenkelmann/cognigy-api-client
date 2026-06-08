"""
Projects resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Projects via the v2.0 API endpoints.

Projects are the top-level organizational unit in Cognigy and serve
as containers for flows, intents, lexicons, endpoints, and other resources.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient
from ..models.project import Project, ProjectCreate, ProjectUpdate
from ..validation import validate_create_update_data, build_list_params
from ..pagination import paginate_sync, paginate_async


class ProjectsResource:
    """
    Synchronous resource for managing Cognigy Projects.
    
    Provides methods to list, create, read, update, and delete projects
    using the Cognigy v2.0 API.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    """

    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the ProjectsResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list(
        self,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Project]:
        """
        List all projects with optional filtering and pagination.
        
        Retrieves projects accessible to the authenticated user from the Cognigy API.
        Results can be filtered and paginated using the provided parameters.
        
        Args:
            filter: Filter string for searching projects by name.
            limit: Maximum number of projects to return. If not specified,
                   a default of 1 is used.
            skip: Number of projects to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of Project objects representing all accessible projects.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> projects = client.projects.list()
            >>> for project in projects:
            ...     print(f"{project.name} (ID: {project.id})")
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        def make_request(p):
            return self._client._request("GET", "/v2.0/projects", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Project(**item) for item in items]

    def create(self, data: ProjectCreate, **kwargs: Any) -> Project:
        """
        Create a new project.
        
        Creates a new project using the provided configuration data.
        
        Args:
            data: ProjectCreate model containing the project configuration.
                  Must include 'name'. Optional fields include 'color',
                  'locale', and 'handover_configuration'.
        
        Returns:
            The created Project object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the ProjectCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import ProjectCreate, ProjectLocale
            >>> new_project = ProjectCreate(
            ...     name="Customer Support Bot",
            ...     color="cognigyBlue",
            ...     locale=ProjectLocale.EN_US
            ... )
            >>> project = client.projects.create(new_project)
            >>> print(f"Created project: {project.id}")
        """
        data = validate_create_update_data(data, ProjectCreate)
        response = self._client._request("POST", "/v2.0/projects", data=data, **kwargs)
        return Project(**response)

    def get(self, project_id: str, **kwargs: Any) -> Project:
        """
        Get a project by ID.
        
        Retrieves a single project by its ObjectId.
        
        Args:
            project_id: The ObjectId of the project to retrieve (24 hex characters).
        
        Returns:
            The Project object with all available fields including 'id', 'name',
            'color', 'handover_configuration', 'live_agent_default_inbox',
            'primary_locale_reference', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the project not being found (404),
                             or server errors.
        
        Example:
            >>> project = client.projects.get("507f1f77bcf86cd799439011")
            >>> print(f"Project: {project.name}, Color: {project.color}")
        """
        data = self._client._request("GET", f"/v2.0/projects/{project_id}", **kwargs)
        return Project(**data)

    def update(
        self,
        project_id: str,
        data: ProjectUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Project]:
        """
        Update a project.
        
        Updates an existing project with the provided data. Only fields that
        are set in the ProjectUpdate object will be modified.
        
        Args:
            project_id: The ObjectId of the project to update (24 hex characters).
            data: ProjectUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'color', and 'handover_configuration'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated project is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Project object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the project not being found (404),
                             validation errors, or server errors.
            ValidationError: If the ProjectUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import ProjectUpdate
            >>> update_data = ProjectUpdate(
            ...     name="Updated Project Name",
            ...     color="deepPurple"
            ... )
            >>> project = client.projects.update("507f1f77bcf86cd799439011", update_data)
            >>> print(project.name)  # "Updated Project Name"
        """
        data = validate_create_update_data(data, ProjectUpdate)
        response = self._client._request("PATCH", f"/v2.0/projects/{project_id}", data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return self.get(project_id, **kwargs)
            return None
        return Project(**response)

    def delete(self, project_id: str, **kwargs: Any) -> None:
        """
        Delete a project.
        
        Permanently deletes a project by its ObjectId. This action cannot be undone.
        Deleting a project will also remove all associated resources including
        flows, intents, lexicons, and endpoints.
        
        Args:
            project_id: The ObjectId of the project to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the project not being found (404),
                             or server errors.
        
        Example:
            >>> client.projects.delete("507f1f77bcf86cd799439011")
            >>> # Project and all its resources are now deleted
        """
        self._client._request("DELETE", f"/v2.0/projects/{project_id}", **kwargs)


class AsyncProjectsResource:
    """
    Asynchronous resource for managing Cognigy Projects.
    
    Provides async methods to list, create, read, update, and delete projects
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """

    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncProjectsResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list(
        self,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[str] = None,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Project]:
        """
        List all projects with optional filtering and pagination.
        
        Retrieves projects accessible to the authenticated user from the Cognigy API
        asynchronously. Results can be filtered and paginated using the provided
        parameters.
        
        Args:
            filter: Filter string for searching projects by name.
            limit: Maximum number of projects to return. If not specified,
                   a default of 1 is used.
            skip: Number of projects to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.
        
        Returns:
            List of Project objects representing all accessible projects.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.
        
        Example:
            >>> projects = await client.projects.list()
            >>> for project in projects:
            ...     print(f"{project.name} (ID: {project.id})")
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        async def make_request(p):
            return await self._client._request("GET", "/v2.0/projects", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Project(**item) for item in items]

    async def create(self, data: ProjectCreate, **kwargs: Any) -> Project:
        """
        Create a new project.
        
        Creates a new project using the provided configuration data asynchronously.
        
        Args:
            data: ProjectCreate model containing the project configuration.
                  Must include 'name'. Optional fields include 'color',
                  'locale', and 'handover_configuration'.
        
        Returns:
            The created Project object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the ProjectCreate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import ProjectCreate, ProjectLocale
            >>> new_project = ProjectCreate(
            ...     name="Customer Support Bot",
            ...     color="cognigyBlue",
            ...     locale=ProjectLocale.EN_US
            ... )
            >>> project = await client.projects.create(new_project)
            >>> print(f"Created project: {project.id}")
        """
        data = validate_create_update_data(data, ProjectCreate)
        response = await self._client._request("POST", "/v2.0/projects", data=data, **kwargs)
        return Project(**response)

    async def get(self, project_id: str, **kwargs: Any) -> Project:
        """
        Get a project by ID.
        
        Retrieves a single project by its ObjectId asynchronously.
        
        Args:
            project_id: The ObjectId of the project to retrieve (24 hex characters).
        
        Returns:
            The Project object with all available fields including 'id', 'name',
            'color', 'handover_configuration', 'live_agent_default_inbox',
            'primary_locale_reference', and metadata fields.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the project not being found (404),
                             or server errors.
        
        Example:
            >>> project = await client.projects.get("507f1f77bcf86cd799439011")
            >>> print(f"Project: {project.name}, Color: {project.color}")
        """
        data = await self._client._request("GET", f"/v2.0/projects/{project_id}", **kwargs)
        return Project(**data)

    async def update(
        self,
        project_id: str,
        data: ProjectUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> Optional[Project]:
        """
        Update a project.

        Updates an existing project with the provided data asynchronously.
        Only fields that are set in the ProjectUpdate object will be modified.
        
        Args:
            project_id: The ObjectId of the project to update (24 hex characters).
            data: ProjectUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'color', and 'handover_configuration'.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated project is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.
        
        Returns:
            The updated Project object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the project not being found (404),
                             validation errors, or server errors.
            ValidationError: If the ProjectUpdate data fails Pydantic validation.
        
        Example:
            >>> from cognigy.models import ProjectUpdate
            >>> update_data = ProjectUpdate(
            ...     name="Updated Project Name",
            ...     color="deepPurple"
            ... )
            >>> project = await client.projects.update("507f1f77bcf86cd799439011", update_data)
            >>> print(project.name)  # "Updated Project Name"
        """
        data = validate_create_update_data(data, ProjectUpdate)
        response = await self._client._request("PATCH", f"/v2.0/projects/{project_id}", data=data, **kwargs)
        if response is None:
            if fetch_updated:
                return await self.get(project_id, **kwargs)
            return None
        return Project(**response)

    async def delete(self, project_id: str, **kwargs: Any) -> None:
        """
        Delete a project.
        
        Permanently deletes a project by its ObjectId asynchronously.
        This action cannot be undone. Deleting a project will also remove
        all associated resources including flows, intents, lexicons, and endpoints.
        
        Args:
            project_id: The ObjectId of the project to delete (24 hex characters).
        
        Returns:
            None
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the project not being found (404),
                             or server errors.
        
        Example:
            >>> await client.projects.delete("507f1f77bcf86cd799439011")
            >>> # Project and all its resources are now deleted
        """
        await self._client._request("DELETE", f"/v2.0/projects/{project_id}", **kwargs)
