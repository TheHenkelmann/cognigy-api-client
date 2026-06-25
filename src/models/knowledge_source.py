"""
KnowledgeSource models for the Cognigy API.

This module contains Pydantic models for KnowledgeSource resources including
response models, create/update request models, and related enums and nested models.

KnowledgeSources are the individual sources of knowledge within a KnowledgeStore,
such as URLs, PDFs, text files, or extension-based sources.
"""

import re
from enum import Enum
from typing import Any, Optional

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


def _validate_uuid(value: Optional[str], field_name: str) -> Optional[str]:
    """
    Validate that a string matches UUID format.

    Args:
        value: The string value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value if valid, None if value was None.

    Raises:
        ValueError: If the value doesn't match the UUID pattern.
    """
    if value is not None and not UUID_PATTERN.match(value):
        raise ValueError(
            f"Invalid UUID format for {field_name}: must be a valid UUID, got '{value}'"
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


class KnowledgeSourceType(str, Enum):
    """
    Type of knowledge source.

    Defines the source type which determines how content is ingested
    into the knowledge store.

    Attributes:
        URL: Web page URL to scrape content from.
        MANUAL: Manually created content.
        PDF: PDF document source.
        TXT: Plain text file source.
        CTXT: Cognigy text format source.
        EXTENSION: Extension-based source using a connector.
    """

    URL = "url"
    MANUAL = "manual"
    PDF = "pdf"
    TXT = "txt"
    CTXT = "ctxt"
    EXTENSION = "extension"


class KnowledgeSourceStatus(str, Enum):
    """
    Status of a knowledge source.

    Indicates the current processing state of the knowledge source.

    Attributes:
        READY: Source is fully processed and ready for use.
        INGESTING: Source is currently being processed.
        DISABLED: Source is disabled and not being used.
    """

    READY = "ready"
    INGESTING = "ingesting"
    DISABLED = "disabled"


class KnowledgeSourceMetaData(CognigyBaseModel):
    """
    Metadata for a knowledge source.

    Contains additional metadata that can be attached to a knowledge source,
    such as tags for categorization and filtering.

    Attributes:
        tags: List of string tags for categorization. Tags can be used
              to filter and organize knowledge sources.
    """

    tags: Optional[list[str]] = Field(
        None, description="List of tags for categorizing the knowledge source"
    )


class KnowledgeSource(CognigyBaseModel):
    """
    Response model for KnowledgeSource resources.

    Represents a knowledge source within a knowledge store. Knowledge sources
    contain the actual content that gets chunked and indexed for retrieval.
    Used for both GET single source and GET list responses.

    Attributes:
        id: MongoDB ObjectId of the knowledge source (24 hex characters).
        name: Name of the knowledge source.
        description: Description about what the knowledge source contains.
        type: Type of source (url, manual, pdf, txt, ctxt, extension).
        status: Current status of the source (ready, ingesting, disabled).
        meta_data: Metadata including tags for categorization.
        data: Custom metadata object for storing additional information.
        chunk_count: Number of chunks created from this source.
        connector_reference: UUID of the associated connector (for extension type only).
        reference_id: UUID reference for the knowledge source.
        created_at: Unix timestamp when source was created (0 to 2147483647).
        created_by: ObjectId of user who created the source.
        last_changed: Unix timestamp when source was last modified (0 to 2147483647).
        last_changed_by: ObjectId of user who last modified the source.
    """

    name: Optional[str] = Field(None, description="Name of the knowledge source")
    description: Optional[str] = Field(
        None, description="Description about what the knowledge source contains"
    )
    type: Optional[KnowledgeSourceType] = Field(
        None, description="Type of source: url, manual, pdf, txt, ctxt, or extension"
    )
    status: Optional[KnowledgeSourceStatus] = Field(
        None, description="Current status: ready, ingesting, or disabled"
    )
    meta_data: Optional[KnowledgeSourceMetaData] = Field(
        None, alias="metaData", description="Metadata including tags for categorization"
    )
    data: Optional[dict[str, Any]] = Field(
        None, description="Custom metadata object for storing additional information"
    )
    chunk_count: Optional[int] = Field(
        None, alias="chunkCount", description="Number of chunks created from this source"
    )
    connector_reference: Optional[str] = Field(
        None,
        alias="connectorReference",
        description="UUID of the associated connector (for extension type only)",
    )
    reference_id: Optional[str] = Field(
        None, alias="referenceId", description="UUID reference for the knowledge source"
    )
    created_at: Optional[int] = Field(
        None, alias="createdAt", description="Unix timestamp when source was created"
    )
    created_by: Optional[str] = Field(
        None, alias="createdBy", description="ObjectId of user who created the source"
    )
    last_changed: Optional[int] = Field(
        None, alias="lastChanged", description="Unix timestamp when source was last modified"
    )
    last_changed_by: Optional[str] = Field(
        None, alias="lastChangedBy", description="ObjectId of user who last modified the source"
    )

    @field_validator("chunk_count")
    @classmethod
    def validate_chunk_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate chunk_count is non-negative."""
        if v is not None and v < 0:
            raise ValueError(f"chunk_count must be non-negative, got {v}")
        return v

    @field_validator("connector_reference")
    @classmethod
    def validate_connector_reference(cls, v: Optional[str]) -> Optional[str]:
        """Validate connector_reference matches UUID format."""
        return _validate_uuid(v, "connector_reference")

    @field_validator("reference_id")
    @classmethod
    def validate_reference_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate reference_id matches UUID format."""
        return _validate_uuid(v, "reference_id")

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


class KnowledgeSourceCreate(CognigyBaseModel):
    """
    Input model for creating a KnowledgeSource.

    Contains the required and optional fields for creating a new knowledge source
    via the POST /v2.0/knowledgestores/{knowledgeStoreId}/sources endpoint.

    Note:
        - For type "url", the `url` field should be provided.
        - For type "extension", the `connector_id` field should be provided.

    Attributes:
        name: Name of the knowledge source.
        description: Description about what the knowledge source contains.
        type: Type of source (url, manual, pdf, txt, ctxt, extension).
        meta_data: Metadata including tags for categorization.
        url: URL to scrape content from (only for type "url").
        connector_id: UUID of the connector to use (only for type "extension").
    """

    name: Optional[str] = Field(None, description="Name of the knowledge source")
    description: Optional[str] = Field(
        None, description="Description about what the knowledge source contains"
    )
    type: Optional[KnowledgeSourceType] = Field(
        None, description="Type of source: url, manual, pdf, txt, ctxt, or extension"
    )
    meta_data: Optional[KnowledgeSourceMetaData] = Field(
        None, alias="metaData", description="Metadata including tags for categorization"
    )
    url: Optional[str] = Field(None, description="URL to scrape content from (only for type 'url')")
    connector_id: Optional[str] = Field(
        None,
        alias="connectorId",
        description="UUID of the connector to use (only for type 'extension')",
    )

    @field_validator("connector_id")
    @classmethod
    def validate_connector_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate connector_id matches UUID format."""
        return _validate_uuid(v, "connector_id")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate url is a valid URL format."""
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError(f"url must start with 'http://' or 'https://', got '{v}'")
        return v


class KnowledgeSourceUpdate(CognigyBaseModel):
    """
    Input model for updating a KnowledgeSource.

    Contains the optional fields for updating an existing knowledge source
    via the PATCH /v2.0/knowledgestores/{knowledgeStoreId}/sources/{sourceId} endpoint.
    Only provided fields will be updated.

    Attributes:
        name: New name for the knowledge source.
        description: New description for the knowledge source.
        status: New status for the knowledge source (ready, ingesting, disabled).
        meta_data: New metadata including tags for categorization.
    """

    name: Optional[str] = Field(None, description="New name for the knowledge source")
    description: Optional[str] = Field(None, description="New description for the knowledge source")
    status: Optional[KnowledgeSourceStatus] = Field(
        None, description="New status: ready, ingesting, or disabled"
    )
    meta_data: Optional[KnowledgeSourceMetaData] = Field(
        None, alias="metaData", description="New metadata including tags for categorization"
    )
