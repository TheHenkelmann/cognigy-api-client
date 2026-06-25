"""
Conversations resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for managing Cognigy Conversations via the v2.0 API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..async_client import AsyncCognigyClient
    from ..client import CognigyClient

import builtins

from ..models.conversation import Conversation, ConversationMessage
from ..pagination import paginate_async, paginate_sync
from ..validation import build_list_params


class ConversationsResource:
    """
    Synchronous resource for managing Cognigy Conversations.

    Provides methods to list conversations, get a conversation's messages
    by session ID, and delete a conversation. Uses the Cognigy v2.0 API.

    Attributes:
        _client: The CognigyClient instance used for API requests.
    """

    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the ConversationsResource.

        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list(
        self,
        filter: str | None = None,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[Conversation]:
        """
        List conversations with optional filtering and pagination.

        Retrieves a list of conversation summaries from the Cognigy API.
        Results can be filtered and paginated using the provided parameters.

        Args:
            filter: Filter string for searching conversations.
            limit: Maximum number of conversations to return. If not specified,
                   a default of 1 is used.
            skip: Number of conversations to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
            previous_cursor: Cursor for fetching the previous page of results.

        Returns:
            List of Conversation objects.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> conversations = client.conversations.list()
            >>> for conv in conversations:
            ...     print(conv.id, conv.channel, conv.flow_name)
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        def make_request(p):
            return self._client._request("GET", "/v2.0/conversations", params=p, **kwargs)

        items = paginate_sync(make_request, params, user_limit=limit)
        return [Conversation(**item) for item in items]

    def get(self, session_id: str, **kwargs: Any) -> builtins.list[ConversationMessage]:
        """
        Get a conversation by session ID.

        Retrieves the detail of a single conversation: the list of
        message/event items for the given session. The response is
        parsed directly to a list of ConversationMessage objects
        (no wrapper with items/total).

        Args:
            session_id: The session ID of the conversation to retrieve.

        Returns:
            List of ConversationMessage objects for that conversation.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the conversation not being found (404),
                             or server errors.

        Example:
            >>> messages = client.conversations.get("my-session-id")
            >>> for msg in messages:
            ...     print(msg.source, msg.input_text)
        """
        data = self._client._request("GET", f"/v2.0/conversations/{session_id}", **kwargs)
        return [ConversationMessage(**item) for item in data.get("items", [])]

    def delete(self, session_id: str, **kwargs: Any) -> None:
        """
        Delete a conversation by session ID.

        Deletes the conversation for the given session. This action
        cannot be undone.

        Args:
            session_id: The session ID of the conversation to delete.

        Returns:
            None.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the conversation not being found (404),
                             or server errors.

        Example:
            >>> client.conversations.delete("my-session-id")
        """
        self._client._request("DELETE", f"/v2.0/conversations/{session_id}", **kwargs)


class AsyncConversationsResource:
    """
    Asynchronous resource for managing Cognigy Conversations.

    Provides async methods to list conversations, get a conversation's
    messages by session ID, and delete a conversation. Use this class
    with AsyncCognigyClient for non-blocking API operations.

    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    """

    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncConversationsResource.

        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list(
        self,
        filter: str | None = None,
        limit: int | None = None,
        skip: int | None = None,
        sort: str | None = None,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
        **kwargs: Any,
    ) -> builtins.list[Conversation]:
        """
        List conversations with optional filtering and pagination.

        Retrieves a list of conversation summaries from the Cognigy API
        asynchronously. Results can be filtered and paginated using the
        provided parameters.

        Args:
            filter: Filter string for searching conversations.
            limit: Maximum number of conversations to return. If not specified,
                   a default of 1 is used.
            skip: Number of conversations to skip for offset-based pagination.
            sort: Sort order string.
            next_cursor: Cursor for fetching the next page of results.
            previous_cursor: Cursor for fetching the previous page of results.

        Returns:
            List of Conversation objects.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, or server errors.

        Example:
            >>> conversations = await client.conversations.list()
            >>> for conv in conversations:
            ...     print(conv.id, conv.channel, conv.flow_name)
        """
        params = build_list_params(
            filter=filter,
            skip=skip,
            sort=sort,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        async def make_request(p):
            return await self._client._request("GET", "/v2.0/conversations", params=p, **kwargs)

        items = await paginate_async(make_request, params, user_limit=limit)
        return [Conversation(**item) for item in items]

    async def get(self, session_id: str, **kwargs: Any) -> builtins.list[ConversationMessage]:
        """
        Get a conversation by session ID.

        Retrieves the detail of a single conversation asynchronously:
        the list of message/event items for the given session. The
        response is parsed directly to a list of ConversationMessage
        objects (no wrapper with items/total).

        Args:
            session_id: The session ID of the conversation to retrieve.

        Returns:
            List of ConversationMessage objects for that conversation.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the conversation not being found (404),
                             or server errors.

        Example:
            >>> messages = await client.conversations.get("my-session-id")
            >>> for msg in messages:
            ...     print(msg.source, msg.input_text)
        """
        data = await self._client._request("GET", f"/v2.0/conversations/{session_id}", **kwargs)
        return [ConversationMessage(**item) for item in data.get("items", [])]

    async def delete(self, session_id: str, **kwargs: Any) -> None:
        """
        Delete a conversation by session ID.

        Deletes the conversation for the given session asynchronously.
        This action cannot be undone.

        Args:
            session_id: The session ID of the conversation to delete.

        Returns:
            None.

        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, the conversation not being found (404),
                             or server errors.

        Example:
            >>> await client.conversations.delete("my-session-id")
        """
        await self._client._request("DELETE", f"/v2.0/conversations/{session_id}", **kwargs)
