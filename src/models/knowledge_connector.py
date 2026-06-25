"""
Knowledge Connector models for the Cognigy API.

This module contains Pydantic models for Knowledge Connector resources including
response models, create/update request models, and related nested models.
Knowledge Connectors allow external data sources to be integrated with Knowledge Stores.
"""

import re
from enum import Enum
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


def _validate_unix_timestamp(value: Optional[int], field_name: str) -> Optional[int]:
    """
    Validate Unix timestamp is within valid range.

    Args:
        value: The timestamp value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value if valid.

    Raises:
        ValueError: If the timestamp is outside the valid range.
    """
    if value is not None and (value < 0 or value > 2147483647):
        raise ValueError(
            f"Unix timestamp for {field_name} must be between 0 and 2147483647, got {value}"
        )
    return value


class KnowledgeConnectorExecutionStatus(str, Enum):
    """
    Execution status of a Knowledge Connector.

    Attributes:
        NONE: No execution has occurred yet.
        QUEUED: Execution is queued and waiting to start.
        ACTIVE: Execution is currently in progress.
        DONE: Execution completed successfully.
        ERROR: Execution failed with an error.
    """

    NONE = "none"
    QUEUED = "queued"
    ACTIVE = "active"
    DONE = "done"
    ERROR = "error"


class ConnectorSchedule(CognigyBaseModel):
    """
    Schedule configuration for automatic Knowledge Connector execution.

    Defines when and how often a Knowledge Connector should automatically
    sync data from its external source.

    Attributes:
        enabled: Whether scheduled execution is enabled.
        start: Unix timestamp for the start date/time to calculate scheduled execution.
               Must be between 0 and 2147483647.
        hour: Hour of the day to start execution (0-23).
        minute: Minute of the hour to start execution (0-59).
        week_days: Days of the week to run the connector.
                   Uses zero-based indexing: Monday=0, Tuesday=1, ..., Sunday=6.
    """

    id: Optional[str] = Field(
        None, alias="_id", exclude=True
    )  # Override base, schedules don't have IDs

    enabled: Optional[bool] = Field(None, description="Whether scheduled execution is enabled")
    start: Optional[int] = Field(
        None,
        description="Unix timestamp for start date/time to calculate scheduled execution",
        ge=0,
        le=2147483647,
    )
    hour: Optional[int] = Field(
        None, description="Hour of the day to start execution (0-23)", ge=0, le=23
    )
    minute: Optional[int] = Field(
        None, description="Minute of the hour to start execution (0-59)", ge=0, le=59
    )
    week_days: Optional[list[int]] = Field(
        None,
        alias="weekDays",
        description="Days of the week to run (Monday=0, Tuesday=1, ..., Sunday=6)",
    )

    @field_validator("start")
    @classmethod
    def validate_start(cls, v: Optional[int]) -> Optional[int]:
        """Validate start is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "start")

    @field_validator("week_days")
    @classmethod
    def validate_week_days(cls, v: Optional[list[int]]) -> Optional[list[int]]:
        """Validate all week_days are valid day indices (0-6)."""
        if v is not None:
            for i, day in enumerate(v):
                if not isinstance(day, int) or day < 0 or day > 6:
                    raise ValueError(
                        f"Invalid weekDay value at index {i}: "
                        f"must be an integer between 0 (Monday) and 6 (Sunday), got {day}"
                    )
        return v


class KnowledgeConnector(CognigyBaseModel):
    """
    Response model for Knowledge Connector resources.

    Represents a Cognigy Knowledge Connector that integrates external data sources
    with Knowledge Stores. Used for both GET single connector and GET list responses.

    Attributes:
        id: MongoDB ObjectId of the connector (24 hex characters).
        extension: Name of the extension providing the connector (e.g., "confluence").
        version: Version of the extension identifier (e.g., "1.1.0").
        type: The Knowledge Connector type identifier within the extension.
        config: Configuration object for the Knowledge Connector.
        name: Human-readable name of the Knowledge Connector.
        schedule: Schedule configuration for automatic execution.
        last_execution: Unix timestamp when the last execution was triggered.
        last_execution_status: Status of the last execution.
        created_at: Unix timestamp when connector was created (0 to 2147483647).
        created_by: ObjectId of user who created the connector.
        last_changed: Unix timestamp when connector was last modified (0 to 2147483647).
        last_changed_by: ObjectId of user who last modified the connector.
    """

    extension: Optional[str] = Field(
        None, description="Name of the extension providing the connector (e.g., 'confluence')"
    )
    version: Optional[str] = Field(
        None, description="Version of the extension identifier (e.g., '1.1.0')"
    )
    type: Optional[str] = Field(
        None, description="The Knowledge Connector type identifier within the extension"
    )
    config: Optional[dict[str, Any]] = Field(
        None, description="Configuration object for the Knowledge Connector"
    )
    name: Optional[str] = Field(None, description="Human-readable name of the Knowledge Connector")
    schedule: Optional[ConnectorSchedule] = Field(
        None, description="Schedule configuration for automatic execution"
    )
    last_execution: Optional[int] = Field(
        None,
        alias="lastExecution",
        description="Unix timestamp when the last execution was triggered",
    )
    last_execution_status: Optional[KnowledgeConnectorExecutionStatus] = Field(
        None, alias="lastExecutionStatus", description="Status of the last execution"
    )
    created_at: Optional[int] = Field(
        None, alias="createdAt", description="Unix timestamp when connector was created"
    )
    created_by: Optional[str] = Field(
        None, alias="createdBy", description="ObjectId of user who created the connector"
    )
    last_changed: Optional[int] = Field(
        None, alias="lastChanged", description="Unix timestamp when connector was last modified"
    )
    last_changed_by: Optional[str] = Field(
        None, alias="lastChangedBy", description="ObjectId of user who last modified the connector"
    )

    @field_validator("last_execution")
    @classmethod
    def validate_last_execution(cls, v: Optional[int]) -> Optional[int]:
        """Validate last_execution is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "last_execution")

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: Optional[int]) -> Optional[int]:
        """Validate created_at is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "created_at")

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate created_by matches ObjectId format."""
        return _validate_object_id(v, "created_by")

    @field_validator("last_changed")
    @classmethod
    def validate_last_changed(cls, v: Optional[int]) -> Optional[int]:
        """Validate last_changed is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "last_changed")

    @field_validator("last_changed_by")
    @classmethod
    def validate_last_changed_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate last_changed_by matches ObjectId format."""
        return _validate_object_id(v, "last_changed_by")


class KnowledgeConnectorCreate(CognigyBaseModel):
    """
    Input model for creating a Knowledge Connector.

    Contains the fields for creating a new Knowledge Connector
    via the POST /v2.0/knowledgestores/{knowledgeStoreId}/connectors endpoint.

    Attributes:
        extension: Name of the extension providing the connector (e.g., "confluence").
        version: Version of the extension identifier (e.g., "1.1.0").
        type: The Knowledge Connector type identifier within the extension.
        config: Configuration object for the Knowledge Connector.
        name: Human-readable name of the Knowledge Connector.
        schedule: Schedule configuration for automatic execution.
    """

    id: Optional[str] = Field(
        None, alias="_id", exclude=True
    )  # Override base, create doesn't have ID

    extension: Optional[str] = Field(
        None, description="Name of the extension providing the connector (e.g., 'confluence')"
    )
    version: Optional[str] = Field(
        None, description="Version of the extension identifier (e.g., '1.1.0')"
    )
    type: Optional[str] = Field(
        None, description="The Knowledge Connector type identifier within the extension"
    )
    config: Optional[dict[str, Any]] = Field(
        None, description="Configuration object for the Knowledge Connector"
    )
    name: Optional[str] = Field(None, description="Human-readable name of the Knowledge Connector")
    schedule: Optional[ConnectorSchedule] = Field(
        None, description="Schedule configuration for automatic execution"
    )


class KnowledgeConnectorUpdate(CognigyBaseModel):
    """
    Input model for updating a Knowledge Connector.

    Contains the optional fields for updating an existing Knowledge Connector
    via the PATCH /v2.0/knowledgestores/{knowledgeStoreId}/connectors/{connectorId} endpoint.
    Only provided fields will be updated.

    Attributes:
        config: New configuration object for the Knowledge Connector.
        name: New human-readable name for the Knowledge Connector.
        schedule: New schedule configuration for automatic execution.
    """

    id: Optional[str] = Field(
        None, alias="_id", exclude=True
    )  # Override base, update doesn't use ID in body

    config: Optional[dict[str, Any]] = Field(
        None, description="New configuration object for the Knowledge Connector"
    )
    name: Optional[str] = Field(
        None, description="New human-readable name for the Knowledge Connector"
    )
    schedule: Optional[ConnectorSchedule] = Field(
        None, description="New schedule configuration for automatic execution"
    )
