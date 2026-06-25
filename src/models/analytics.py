"""
Pydantic models for Cognigy Analytics v3.0 API.

This module provides data models for call counter and conversation counter
metrics returned by the Analytics API endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CallCounterMetric(BaseModel):
    """
    Represents a single call counter metric entry.

    Contains daily call statistics including concurrency, duration,
    and call counts.

    Attributes:
        day: Day of the month (1-31).
        month: Month of the year (1-12).
        year: Full year (e.g., 2024).
        max_concurrency: Maximum number of concurrent calls recorded.
        call_minutes: Total call duration in minutes.
        processed_calls: Total number of calls processed.
        billable_calls: Number of calls that are billable.

    Example:
        >>> metric = CallCounterMetric(
        ...     day=15, month=6, year=2024,
        ...     max_concurrency=10, call_minutes=125.5,
        ...     processed_calls=50, billable_calls=45
        ... )
    """

    day: int = Field(..., ge=1, le=31, description="Day of the month (1-31).")
    month: int = Field(..., ge=1, le=12, description="Month of the year (1-12).")
    year: int = Field(..., ge=2000, le=2100, description="Full year (e.g., 2024).")
    max_concurrency: float | None = Field(
        None,
        alias="maxConcurrency",
        ge=0,
        description="Maximum number of concurrent calls recorded.",
    )
    call_minutes: float | None = Field(
        None, alias="callMinutes", ge=0, description="Total call duration in minutes."
    )
    processed_calls: float | None = Field(
        None, alias="processedCalls", ge=0, description="Total number of calls processed."
    )
    billable_calls: float | None = Field(
        None, alias="billableCalls", ge=0, description="Number of calls that are billable."
    )

    model_config = {"populate_by_name": True, "extra": "ignore"}


class ChannelConversations(BaseModel):
    """
    Represents conversation count for a specific channel.

    Used within ConversationCounterMetric to break down conversations
    by communication channel.

    Attributes:
        channel: The name/identifier of the communication channel
                 (e.g., "webchat", "facebook", "whatsapp").
        conversations: Number of conversations on this channel.

    Example:
        >>> channel_data = ChannelConversations(
        ...     channel="webchat",
        ...     conversations=150
        ... )
    """

    channel: str = Field(
        ..., min_length=1, description="The name/identifier of the communication channel."
    )
    conversations: float = Field(..., ge=0, description="Number of conversations on this channel.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class ConversationCounterMetric(BaseModel):
    """
    Represents a single conversation counter metric entry.

    Contains daily conversation statistics including total count
    and per-channel breakdown.

    Attributes:
        day: Day of the month (1-31).
        month: Month of the year (1-12).
        year: Full year (e.g., 2024).
        conversations: Total number of conversations for this day.
        per_channel: Breakdown of conversations by channel.

    Example:
        >>> metric = ConversationCounterMetric(
        ...     day=15, month=6, year=2024,
        ...     conversations=500,
        ...     per_channel=[
        ...         ChannelConversations(channel="webchat", conversations=300),
        ...         ChannelConversations(channel="facebook", conversations=200)
        ...     ]
        ... )
    """

    day: int = Field(..., ge=1, le=31, description="Day of the month (1-31).")
    month: int = Field(..., ge=1, le=12, description="Month of the year (1-12).")
    year: int = Field(..., ge=2000, le=2100, description="Full year (e.g., 2024).")
    conversations: float | None = Field(
        None, ge=0, description="Total number of conversations for this day."
    )
    per_channel: list[ChannelConversations] | None = Field(
        None, alias="perChannel", description="Breakdown of conversations by channel."
    )

    model_config = {"populate_by_name": True, "extra": "ignore"}
