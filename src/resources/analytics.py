"""
Analytics resource for the Cognigy API.

This module provides synchronous and asynchronous resource classes
for accessing Cognigy Analytics v3.0 API endpoints.

The Analytics API provides read-only access to call counter and
conversation counter metrics at both organization-wide and project levels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import CognigyClient
    from ..async_client import AsyncCognigyClient

from ..models.analytics import CallCounterMetric, ConversationCounterMetric


class AnalyticsResource:
    """
    Synchronous resource for accessing Cognigy Analytics.
    
    Provides methods to retrieve call counter and conversation counter
    metrics using the Cognigy v3.0 API. Metrics are available both
    organization-wide and per-project.
    
    Note:
        This is a read-only resource. Analytics data cannot be created,
        updated, or deleted via the API.
    
    Attributes:
        _client: The CognigyClient instance used for API requests.
    
    Example:
        >>> client = CognigyClient(api_key="your-api-key")
        >>> # Get org-wide call metrics for 2024
        >>> call_metrics = client.analytics.list_call_counter(year=2024)
        >>> for metric in call_metrics:
        ...     print(f"{metric.year}-{metric.month}-{metric.day}: {metric.processed_calls} calls")
    """
    
    def __init__(self, client: CognigyClient) -> None:
        """
        Initialize the AnalyticsResource.
        
        Args:
            client: The CognigyClient instance to use for API requests.
        """
        self._client = client

    def list_call_counter(
        self,
        year: int,
        month: Optional[int] = None,
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[CallCounterMetric]:
        """
        Get call counter metrics.
        
        Retrieves call counter metrics either organization-wide or for a specific
        project. Returns daily statistics including concurrent calls, call duration,
        processed calls, and billable calls.
        
        Args:
            year: The year to retrieve metrics for (required).
            month: The month to retrieve metrics for (1-12, optional).
                   If not provided, returns metrics for the entire year.
            project_id: The ObjectId of the project (24 hex characters, optional).
                        If not provided, returns organization-wide metrics.
        
        Returns:
            List of CallCounterMetric objects containing daily call statistics.
            Each entry represents metrics for a specific day.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, project not found (404), or server errors.
        
        Example:
            >>> # Org-wide metrics for January 2024
            >>> metrics = client.analytics.list_call_counter(year=2024, month=1)
            >>> for m in metrics:
            ...     print(f"{m.year}-{m.month:02d}-{m.day:02d}: "
            ...           f"{m.processed_calls} processed, {m.billable_calls} billable")
            >>> 
            >>> # Project-specific metrics for all of 2024
            >>> metrics = client.analytics.list_call_counter(
            ...     year=2024,
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> total_calls = sum(m.processed_calls or 0 for m in metrics)
            >>> print(f"Total processed calls: {total_calls}")
        """
        params: Dict[str, Any] = {"year": year}
        if month is not None:
            params["month"] = month
        
        if project_id:
            endpoint = f"/v3.0/projects/{project_id}/callcounter"
        else:
            endpoint = "/v3.0/callcounter"
        
        data = self._client._request("GET", endpoint, params=params, **kwargs)
        return [CallCounterMetric(**item) for item in data.get("items", [])]

    def list_conversation_counter(
        self,
        year: int,
        month: Optional[int] = None,
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[ConversationCounterMetric]:
        """
        Get conversation counter metrics.
        
        Retrieves conversation counter metrics either organization-wide or for
        a specific project. Returns daily statistics including total conversations
        and per-channel breakdown.
        
        Args:
            year: The year to retrieve metrics for (required).
            month: The month to retrieve metrics for (1-12, optional).
                   If not provided, returns metrics for the entire year.
            project_id: The ObjectId of the project (24 hex characters, optional).
                        If not provided, returns organization-wide metrics.
        
        Returns:
            List of ConversationCounterMetric objects containing daily
            conversation statistics. Each entry represents metrics for
            a specific day and includes per-channel breakdown.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, project not found (404), or server errors.
        
        Example:
            >>> # Org-wide metrics for 2024
            >>> metrics = client.analytics.list_conversation_counter(year=2024)
            >>> for m in metrics:
            ...     print(f"{m.year}-{m.month:02d}-{m.day:02d}: {m.conversations} total")
            ...     if m.per_channel:
            ...         for ch in m.per_channel:
            ...             print(f"  - {ch.channel}: {ch.conversations}")
            >>> 
            >>> # Project-specific metrics for March 2024
            >>> metrics = client.analytics.list_conversation_counter(
            ...     year=2024,
            ...     month=3,
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> for m in metrics:
            ...     if m.per_channel:
            ...         webchat = next(
            ...             (ch for ch in m.per_channel if ch.channel == "webchat"),
            ...             None
            ...         )
            ...         if webchat:
            ...             print(f"{m.day}/{m.month}: {webchat.conversations} webchat conversations")
        """
        params: Dict[str, Any] = {"year": year}
        if month is not None:
            params["month"] = month
        
        if project_id:
            endpoint = f"/v3.0/projects/{project_id}/conversationcounter"
        else:
            endpoint = "/v3.0/conversationcounter"
        
        data = self._client._request("GET", endpoint, params=params, **kwargs)
        return [ConversationCounterMetric(**item) for item in data.get("items", [])]


class AsyncAnalyticsResource:
    """
    Asynchronous resource for accessing Cognigy Analytics.
    
    Provides async methods to retrieve call counter and conversation counter
    metrics using the Cognigy v3.0 API. Use this class with AsyncCognigyClient
    for non-blocking API operations.
    
    Note:
        This is a read-only resource. Analytics data cannot be created,
        updated, or deleted via the API.
    
    Attributes:
        _client: The AsyncCognigyClient instance used for API requests.
    
    Example:
        >>> async with AsyncCognigyClient(api_key="your-api-key") as client:
        ...     call_metrics = await client.analytics.list_call_counter(year=2024)
        ...     for metric in call_metrics:
        ...         print(f"{metric.year}-{metric.month}-{metric.day}: {metric.processed_calls} calls")
    """
    
    def __init__(self, client: AsyncCognigyClient) -> None:
        """
        Initialize the AsyncAnalyticsResource.
        
        Args:
            client: The AsyncCognigyClient instance to use for API requests.
        """
        self._client = client

    async def list_call_counter(
        self,
        year: int,
        month: Optional[int] = None,
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[CallCounterMetric]:
        """
        Get call counter metrics asynchronously.
        
        Retrieves call counter metrics either organization-wide or for a specific
        project. Returns daily statistics including concurrent calls, call duration,
        processed calls, and billable calls.
        
        Args:
            year: The year to retrieve metrics for (required).
            month: The month to retrieve metrics for (1-12, optional).
                   If not provided, returns metrics for the entire year.
            project_id: The ObjectId of the project (24 hex characters, optional).
                        If not provided, returns organization-wide metrics.
        
        Returns:
            List of CallCounterMetric objects containing daily call statistics.
            Each entry represents metrics for a specific day.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, project not found (404), or server errors.
        
        Example:
            >>> # Org-wide metrics for January 2024
            >>> metrics = await client.analytics.list_call_counter(year=2024, month=1)
            >>> for m in metrics:
            ...     print(f"{m.year}-{m.month:02d}-{m.day:02d}: "
            ...           f"{m.processed_calls} processed, {m.billable_calls} billable")
            >>> 
            >>> # Project-specific metrics for all of 2024
            >>> metrics = await client.analytics.list_call_counter(
            ...     year=2024,
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> total_calls = sum(m.processed_calls or 0 for m in metrics)
            >>> print(f"Total processed calls: {total_calls}")
        """
        params: Dict[str, Any] = {"year": year}
        if month is not None:
            params["month"] = month
        
        if project_id:
            endpoint = f"/v3.0/projects/{project_id}/callcounter"
        else:
            endpoint = "/v3.0/callcounter"
        
        data = await self._client._request("GET", endpoint, params=params, **kwargs)
        return [CallCounterMetric(**item) for item in data.get("items", [])]

    async def list_conversation_counter(
        self,
        year: int,
        month: Optional[int] = None,
        project_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[ConversationCounterMetric]:
        """
        Get conversation counter metrics asynchronously.
        
        Retrieves conversation counter metrics either organization-wide or for
        a specific project. Returns daily statistics including total conversations
        and per-channel breakdown.
        
        Args:
            year: The year to retrieve metrics for (required).
            month: The month to retrieve metrics for (1-12, optional).
                   If not provided, returns metrics for the entire year.
            project_id: The ObjectId of the project (24 hex characters, optional).
                        If not provided, returns organization-wide metrics.
        
        Returns:
            List of ConversationCounterMetric objects containing daily
            conversation statistics. Each entry represents metrics for
            a specific day and includes per-channel breakdown.
        
        Raises:
            CognigyAPIError: If the API request fails due to authentication,
                             authorization, project not found (404), or server errors.
        
        Example:
            >>> # Org-wide metrics for 2024
            >>> metrics = await client.analytics.list_conversation_counter(year=2024)
            >>> for m in metrics:
            ...     print(f"{m.year}-{m.month:02d}-{m.day:02d}: {m.conversations} total")
            ...     if m.per_channel:
            ...         for ch in m.per_channel:
            ...             print(f"  - {ch.channel}: {ch.conversations}")
            >>> 
            >>> # Project-specific metrics for March 2024
            >>> metrics = await client.analytics.list_conversation_counter(
            ...     year=2024,
            ...     month=3,
            ...     project_id="507f1f77bcf86cd799439011"
            ... )
            >>> for m in metrics:
            ...     if m.per_channel:
            ...         webchat = next(
            ...             (ch for ch in m.per_channel if ch.channel == "webchat"),
            ...             None
            ...         )
            ...         if webchat:
            ...             print(f"{m.day}/{m.month}: {webchat.conversations} webchat conversations")
        """
        params: Dict[str, Any] = {"year": year}
        if month is not None:
            params["month"] = month
        
        if project_id:
            endpoint = f"/v3.0/projects/{project_id}/conversationcounter"
        else:
            endpoint = "/v3.0/conversationcounter"
        
        data = await self._client._request("GET", endpoint, params=params, **kwargs)
        return [ConversationCounterMetric(**item) for item in data.get("items", [])]
