"""
KnowledgeStore models for the Cognigy API.

This module contains Pydantic models for KnowledgeStore resources including
response models, create/update request models, and related enums.
"""

import re
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from .base import CognigyBaseModel

# Validation patterns
OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


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


class KnowledgeStoreStatus(str, Enum):
    """
    Status of a KnowledgeStore.

    Attributes:
        READY: The knowledge store is ready for use.
        WARNING: The knowledge store has warnings that may need attention.
    """

    READY = "ready"
    WARNING = "warning"


class KnowledgeStore(CognigyBaseModel):
    """
    Response model for KnowledgeStore resources.

    Represents a Cognigy KnowledgeStore containing knowledge sources for
    AI-powered search and retrieval. Used for both GET single store and
    GET list responses.

    Attributes:
        id: MongoDB ObjectId of the knowledge store (24 hex characters).
        name: Name of the knowledge store.
        description: Description about what the knowledge store contains.
        language: Language code of the knowledge store (e.g., "en-US").
        status: Current status of the knowledge store ("ready" or "warning").
        documents: List of document URLs or file names ingested into the store.
        reference_id: UUID reference for the knowledge store.
        created_at: Unix timestamp when the store was created (0 to 2147483647).
        created_by: ObjectId of user who created the store.
        last_changed: Unix timestamp when the store was last modified (0 to 2147483647).
        last_changed_by: ObjectId of user who last modified the store.
    """

    name: str = Field(..., description="Name of the knowledge store")
    description: Optional[str] = Field(
        None, description="Description about what the knowledge store contains"
    )
    language: Optional[str] = Field(
        None, description="Language code of the knowledge store (e.g., 'en-US')"
    )
    status: Optional[KnowledgeStoreStatus] = Field(
        None, description="Current status of the knowledge store"
    )
    documents: Optional[list[str]] = Field(
        None, description="List of document URLs or file names ingested into the store"
    )
    reference_id: Optional[str] = Field(
        None, alias="referenceId", description="UUID reference for the knowledge store"
    )
    created_at: Optional[int] = Field(
        None, alias="createdAt", description="Unix timestamp when the store was created"
    )
    created_by: Optional[str] = Field(
        None, alias="createdBy", description="ObjectId of user who created the store"
    )
    last_changed: Optional[int] = Field(
        None, alias="lastChanged", description="Unix timestamp when the store was last modified"
    )
    last_changed_by: Optional[str] = Field(
        None, alias="lastChangedBy", description="ObjectId of user who last modified the store"
    )

    @field_validator("reference_id")
    @classmethod
    def validate_reference_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate reference_id matches UUID format."""
        if v is not None and not UUID_PATTERN.match(v):
            raise ValueError(
                f"Invalid UUID format for reference_id: must be a valid UUID, got '{v}'"
            )
        return v

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


class KnowledgeStoreCreate(CognigyBaseModel):
    """
    Input model for creating a KnowledgeStore.

    Contains the required and optional fields for creating a new knowledge store
    via the POST /v2.0/knowledgestores endpoint.

    Attributes:
        name: Name of the knowledge store (required).
        project_id: ObjectId of the project to create the store in (required).
        description: Optional description about what the knowledge store contains.
    """

    name: str = Field(..., description="Name of the knowledge store")
    project_id: str = Field(
        ...,
        alias="projectId",
        description="ObjectId of the project to create the knowledge store in",
    )
    description: Optional[str] = Field(
        None, description="Description about what the knowledge store contains"
    )

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """Validate project_id matches ObjectId format."""
        if not OBJECT_ID_PATTERN.match(v):
            raise ValueError(
                f"Invalid ObjectId format for project_id: "
                f"must be 24 lowercase hex characters, got '{v}'"
            )
        return v


class KnowledgeStoreUpdate(CognigyBaseModel):
    """
    Input model for updating a KnowledgeStore.

    Contains the optional fields for updating an existing knowledge store
    via the PATCH /v2.0/knowledgestores/{knowledgeStoreId} endpoint.
    Only provided fields will be updated.

    Attributes:
        name: New name for the knowledge store.
        description: New description for the knowledge store.
    """

    name: Optional[str] = Field(None, description="New name for the knowledge store")
    description: Optional[str] = Field(None, description="New description for the knowledge store")
