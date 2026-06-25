"""
AI Agents resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy AI Agents via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient

import builtins

from ..models.aiagent import (
    AIAgent,
    AIAgentCreate,
    AIAgentJob,
    AIAgentUpdate,
    AIAgentValidateNameRequest,
)
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params, validate_create_update_data


class AIAgentsResource:
    """
    Synchronous resource for managing Cognigy AI Agents.

    Provides methods to list, create, read, update, and delete AI Agents
    using the Cognigy v2.0 API. Also includes additional endpoints for
    jobs and name validation.

    Attributes:
        _client: The CognigyClient instance used for API requests.
    """

    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the AIAgentsResource.

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
    ) -> builtins.list[AIAgent]:
        """
        List AI Agents with optional filtering and pagination.

        Retrieves a list of AI Agents from the Cognigy API. Results can be
        filtered and paginated using the provided parameters.

        Args:
            project_id: Filter AI Agents by project ObjectId (24 hex characters).
            filter: Filter string for searching AI Agents by name.
            limit: Maximum number of AI Agents to return. If not specified,
                   uses the API default.
            skip: Number of AI Agents to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of AIAgent objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> agents = client.aiagents.list(project_id="507f1f77bcf86cd799439011")
            >>> for agent in agents:
            ...     print(agent.name)
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
            return self._client._request("GET", "/v2.0/aiagents", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [AIAgent(**item) for item in items]

    def create(self, data: AIAgentCreate, **kwargs: Any) -> AIAgent:
        """
        Create a new AI Agent.

        Creates a new AI Agent in the specified project using the provided data.

        Args:
            data: AIAgentCreate model containing the AI Agent configuration.
                  Must include 'project_id'. Optional fields include 'name',
                  'description', 'image', 'instructions', 'speaking_style',
                  'voice_configs', 'safety_settings', and more.

        Returns:
            The created AIAgent object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the AIAgentCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import AIAgentCreate
            >>> new_agent = AIAgentCreate(
            ...     name="My AI Agent",
            ...     project_id="507f1f77bcf86cd799439011",
            ...     description="A helpful assistant"
            ... )
            >>> agent = client.aiagents.create(new_agent)
            >>> print(agent.id)
        """
        data = validate_create_update_data(data, AIAgentCreate)
        response = self._client._request("POST", "/v2.0/aiagents", data=data, **kwargs)
        return AIAgent(**response)

    def get(self, ai_agent_id: str, **kwargs: Any) -> AIAgent:
        """
        Get an AI Agent by ID.

        Retrieves a single AI Agent by its ObjectId.

        Args:
            ai_agent_id: The ObjectId of the AI Agent to retrieve (24 hex characters).

        Returns:
            The AIAgent object with all available fields including 'id', 'name',
            'description', 'instructions', 'speaking_style', 'voice_configs',
            'safety_settings', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             or server errors.

        Example:
            >>> agent = client.aiagents.get("507f1f77bcf86cd799439011")
            >>> print(f"Agent: {agent.name}, Voice enabled: {agent.enable_voice_configs}")
        """
        data = self._client._request("GET", f"/v2.0/aiagents/{ai_agent_id}", **kwargs)
        return AIAgent(**data)

    def update(
        self,
        ai_agent_id: str,
        data: AIAgentUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> AIAgent | None:
        """
        Update an AI Agent.

        Updates an existing AI Agent with the provided data. Only fields that
        are set in the AIAgentUpdate object will be modified.

        Args:
            ai_agent_id: The ObjectId of the AI Agent to update (24 hex characters).
            data: AIAgentUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'description', 'image', 'instructions', 'speaking_style',
                  'voice_configs', 'safety_settings', and more.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated agent is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated AIAgent object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             validation errors, or server errors.
            ValidationError: If the AIAgentUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import AIAgentUpdate
            >>> update_data = AIAgentUpdate(
            ...     name="Updated Agent Name",
            ...     description="New description"
            ... )
            >>> agent = client.aiagents.update("507f1f77bcf86cd799439011", update_data)
            >>> print(agent.name)  # "Updated Agent Name"
        """
        data = validate_create_update_data(data, AIAgentUpdate)
        response = self._client._request(
            "PATCH", f"/v2.0/aiagents/{ai_agent_id}", data=data, **kwargs
        )
        if response is None:
            if fetch_updated:
                return self.get(ai_agent_id, **kwargs)
            return None
        return AIAgent(**response)

    def delete(self, ai_agent_id: str, **kwargs: Any) -> None:
        """
        Delete an AI Agent.

        Permanently deletes an AI Agent by its ObjectId. This action cannot be undone.

        Args:
            ai_agent_id: The ObjectId of the AI Agent to delete (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             or server errors.

        Example:
            >>> client.aiagents.delete("507f1f77bcf86cd799439011")
            >>> # AI Agent is now deleted
        """
        self._client._request("DELETE", f"/v2.0/aiagents/{ai_agent_id}", **kwargs)

    def get_jobs(self, ai_agent_id: str, **kwargs: Any) -> builtins.list[AIAgentJob]:
        """
        Get jobs and their tools for an AI Agent.

        Retrieves all jobs associated with an AI Agent, including
        the tools configured for each job.

        Args:
            ai_agent_id: The ObjectId of the AI Agent (24 hex characters).

        Returns:
            List of AIAgentJob objects, each containing job configuration
            and associated tools.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             or server errors.

        Example:
            >>> jobs = client.aiagents.get_jobs("507f1f77bcf86cd799439011")
            >>> for job in jobs:
            ...     print(f"Job: {job.label}, Tools: {len(job.tools or [])}")
        """
        data = self._client._request("GET", f"/v2.0/aiagents/{ai_agent_id}/jobs", **kwargs)
        return [AIAgentJob(**item) for item in data]

    def validate_name(self, name: str, project_id: str, **kwargs: Any) -> None:
        """
        Validate if an AI Agent name already exists in a project.

        Checks whether the specified name is already in use by another
        AI Agent in the given project. This is useful before creating
        a new AI Agent to avoid naming conflicts.

        Args:
            name: The AI Agent name to validate.
            project_id: The ObjectId of the project to check (24 hex characters).

        Returns:
            None if the name is valid and available.

        Raises:
            CognigyAPIError: If the name already exists (typically returns an error),
                             or if the request fails due to authentication,
                             authorization, or server errors.
            ValidationError: If the project_id format is invalid.

        Example:
            >>> try:
            ...     client.aiagents.validate_name("My Agent", "507f1f77bcf86cd799439011")
            ...     print("Name is available!")
            ... except CognigyAPIError:
            ...     print("Name already exists")
        """
        request_data = AIAgentValidateNameRequest(name=name, project_id=project_id)
        self._client._request("POST", "/v2.0/aiagents/validatename", data=request_data, **kwargs)


class AsyncAIAgentsResource:
    """
    Asynchronous resource for managing Cognigy AI Agents.

    Provides async methods to list, create, read, update, and delete AI Agents
    using the Cognigy v2.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations. Also includes additional endpoints for
    jobs and name validation.

    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """

    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncAIAgentsResource.

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
    ) -> builtins.list[AIAgent]:
        """
        List AI Agents with optional filtering and pagination.

        Retrieves a list of AI Agents from the Cognigy API asynchronously.
        Results can be filtered and paginated using the provided parameters.

        Args:
            project_id: Filter AI Agents by project ObjectId (24 hex characters).
            filter: Filter string for searching AI Agents by name.
            limit: Maximum number of AI Agents to return. If not specified,
                   uses the API default.
            skip: Number of AI Agents to skip for offset-based pagination.
            sort: Sort order string. Use field name for ascending order
                  (e.g., "name") or prefix with "-" for descending order
                  (e.g., "-createdAt").
            next_cursor: Cursor for fetching the next page of results.
                         Obtained from a previous list response.
            previous_cursor: Cursor for fetching the previous page of results.
                             Obtained from a previous list response.

        Returns:
            List of AIAgent objects matching the query parameters.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> agents = await client.aiagents.list(project_id="507f1f77bcf86cd799439011")
            >>> for agent in agents:
            ...     print(agent.name)
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
            return await self._client._request("GET", "/v2.0/aiagents", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [AIAgent(**item) for item in items]

    async def create(self, data: AIAgentCreate, **kwargs: Any) -> AIAgent:
        """
        Create a new AI Agent.

        Creates a new AI Agent in the specified project using the provided data
        asynchronously.

        Args:
            data: AIAgentCreate model containing the AI Agent configuration.
                  Must include 'project_id'. Optional fields include 'name',
                  'description', 'image', 'instructions', 'speaking_style',
                  'voice_configs', 'safety_settings', and more.

        Returns:
            The created AIAgent object with all fields populated by the API,
            including the generated 'id', timestamps, and creator information.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, validation errors, or server errors.
            ValidationError: If the AIAgentCreate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import AIAgentCreate
            >>> new_agent = AIAgentCreate(
            ...     name="My AI Agent",
            ...     project_id="507f1f77bcf86cd799439011",
            ...     description="A helpful assistant"
            ... )
            >>> agent = await client.aiagents.create(new_agent)
            >>> print(agent.id)
        """
        data = validate_create_update_data(data, AIAgentCreate)
        response = await self._client._request("POST", "/v2.0/aiagents", data=data, **kwargs)
        return AIAgent(**response)

    async def get(self, ai_agent_id: str, **kwargs: Any) -> AIAgent:
        """
        Get an AI Agent by ID.

        Retrieves a single AI Agent by its ObjectId asynchronously.

        Args:
            ai_agent_id: The ObjectId of the AI Agent to retrieve (24 hex characters).

        Returns:
            The AIAgent object with all available fields including 'id', 'name',
            'description', 'instructions', 'speaking_style', 'voice_configs',
            'safety_settings', and metadata fields.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             or server errors.

        Example:
            >>> agent = await client.aiagents.get("507f1f77bcf86cd799439011")
            >>> print(f"Agent: {agent.name}, Voice enabled: {agent.enable_voice_configs}")
        """
        data = await self._client._request("GET", f"/v2.0/aiagents/{ai_agent_id}", **kwargs)
        return AIAgent(**data)

    async def update(
        self,
        ai_agent_id: str,
        data: AIAgentUpdate,
        *,
        fetch_updated: bool = True,
        **kwargs: Any,
    ) -> AIAgent | None:
        """
        Update an AI Agent.

        Updates an existing AI Agent with the provided data asynchronously.
        Only fields that are set in the AIAgentUpdate object will be modified.

        Args:
            ai_agent_id: The ObjectId of the AI Agent to update (24 hex characters).
            data: AIAgentUpdate model containing the fields to update.
                  All fields are optional. Possible fields include 'name',
                  'description', 'image', 'instructions', 'speaking_style',
                  'voice_configs', 'safety_settings', and more.
            fetch_updated: If True (default), when the API returns no body a GET
                           is performed and the updated agent is returned. If False,
                           no GET is performed and None is returned when the API
                           returns no body.

        Returns:
            The updated AIAgent object with all fields reflecting the changes,
            or None if the API returned no body and fetch_updated=False.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             validation errors, or server errors.
            ValidationError: If the AIAgentUpdate data fails Pydantic validation.

        Example:
            >>> from cognigy.models import AIAgentUpdate
            >>> update_data = AIAgentUpdate(
            ...     name="Updated Agent Name",
            ...     description="New description"
            ... )
            >>> agent = await client.aiagents.update("507f1f77bcf86cd799439011", update_data)
            >>> print(agent.name)  # "Updated Agent Name"
        """
        data = validate_create_update_data(data, AIAgentUpdate)
        response = await self._client._request(
            "PATCH", f"/v2.0/aiagents/{ai_agent_id}", data=data, **kwargs
        )
        if response is None:
            if fetch_updated:
                return await self.get(ai_agent_id, **kwargs)
            return None
        return AIAgent(**response)

    async def delete(self, ai_agent_id: str, **kwargs: Any) -> None:
        """
        Delete an AI Agent.

        Permanently deletes an AI Agent by its ObjectId asynchronously.
        This action cannot be undone.

        Args:
            ai_agent_id: The ObjectId of the AI Agent to delete (24 hex characters).

        Returns:
            None

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             or server errors.

        Example:
            >>> await client.aiagents.delete("507f1f77bcf86cd799439011")
            >>> # AI Agent is now deleted
        """
        await self._client._request("DELETE", f"/v2.0/aiagents/{ai_agent_id}", **kwargs)

    async def get_jobs(self, ai_agent_id: str, **kwargs: Any) -> builtins.list[AIAgentJob]:
        """
        Get jobs and their tools for an AI Agent.

        Retrieves all jobs associated with an AI Agent asynchronously,
        including the tools configured for each job.

        Args:
            ai_agent_id: The ObjectId of the AI Agent (24 hex characters).

        Returns:
            List of AIAgentJob objects, each containing job configuration
            and associated tools.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the AI Agent not being found (404),
                             or server errors.

        Example:
            >>> jobs = await client.aiagents.get_jobs("507f1f77bcf86cd799439011")
            >>> for job in jobs:
            ...     print(f"Job: {job.label}, Tools: {len(job.tools or [])}")
        """
        data = await self._client._request("GET", f"/v2.0/aiagents/{ai_agent_id}/jobs", **kwargs)
        return [AIAgentJob(**item) for item in data]

    async def validate_name(self, name: str, project_id: str, **kwargs: Any) -> None:
        """
        Validate if an AI Agent name already exists in a project.

        Checks asynchronously whether the specified name is already in use
        by another AI Agent in the given project. This is useful before
        creating a new AI Agent to avoid naming conflicts.

        Args:
            name: The AI Agent name to validate.
            project_id: The ObjectId of the project to check (24 hex characters).

        Returns:
            None if the name is valid and available.

        Raises:
            CognigyAPIError: If the name already exists (typically returns an error),
                             or if the request fails due to authentication,
                             authorization, or server errors.
            ValidationError: If the project_id format is invalid.

        Example:
            >>> try:
            ...     await client.aiagents.validate_name("My Agent", "507f1f77bcf86cd799439011")
            ...     print("Name is available!")
            ... except CognigyAPIError:
            ...     print("Name already exists")
        """
        request_data = AIAgentValidateNameRequest(name=name, project_id=project_id)
        await self._client._request(
            "POST", "/v2.0/aiagents/validatename", data=request_data, **kwargs
        )
