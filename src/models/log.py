"""
Log models for the Cognigy API.

This module contains Pydantic models for LogEntry resources
from the v2.0 API endpoints.
"""

import re
from datetime import datetime
from typing import Any, Optional

from pydantic import Field, field_validator

from .base import CognigyBaseModel

# Validation patterns
OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")


def _validate_object_id(value: Optional[str], field_name: str) -> Optional[str]:
    """
    Validate that a string matches MongoDB ObjectId format.

    Args:
        value: The string value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value if valid, None if value was None.

    Raises:
        ValueError: If the value doesn't match the ObjectId pattern.
    """
    if value is not None and not OBJECT_ID_PATTERN.match(value):
        raise ValueError(
            f"Invalid ObjectId format for {field_name}: "
            f"must be 24 lowercase hex characters, got '{value}'"
        )
    return value


class LogEntry(CognigyBaseModel):
    """
    Response model for LogEntry resources.

    Represents a Cognigy log entry containing runtime information
    from Flow executions and system events.
    Used for both GET single log entry and GET list responses.

    Attributes:
        id: MongoDB ObjectId of the log entry (24 hex characters).
        timestamp: ISO 8601 datetime string when the log entry was created.
        msg: The log message content.
        meta: Additional metadata associated with the log entry.
            May contain contextual information like flow_id, session_id, etc.
        trace_id: Trace identifier for correlating related log entries
            across distributed systems.

    Example:
        >>> log = LogEntry(
        ...     _id="507f1f77bcf86cd799439011",
        ...     timestamp="2024-01-15T10:30:00.000Z",
        ...     msg="Flow executed successfully",
        ...     meta={"flowId": "abc123", "sessionId": "xyz789"},
        ...     traceId="trace-123-456"
        ... )
        >>> print(log.msg)
        "Flow executed successfully"
    """

    timestamp: Optional[datetime] = Field(
        None, description="ISO 8601 datetime when the log entry was created"
    )
    msg: Optional[str] = Field(None, description="The log message content")
    meta: Optional[dict[str, Any]] = Field(
        None, description="Additional metadata associated with the log entry"
    )
    trace_id: Optional[str] = Field(
        None, alias="traceId", description="Trace identifier for correlating related log entries"
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate id matches ObjectId format."""
        return _validate_object_id(v, "id")
