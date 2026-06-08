"""
KnowledgeChunk models for the Cognigy API.

This module contains Pydantic models for KnowledgeChunk resources including
response models and create/update request models. Knowledge chunks are
individual pieces of content within a knowledge source.
"""

import re
from typing import Any, Dict, Optional
from pydantic import Field, field_validator
from .base import CognigyBaseModel


# Validation patterns
OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE
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
        ValueError: If the timestamp is outside the valid range (0 to 2147483647).
    """
    if value is not None and (value < 0 or value > 2147483647):
        raise ValueError(
            f"Unix timestamp for {field_name} must be between 0 and 2147483647, got {value}"
        )
    return value


class KnowledgeChunk(CognigyBaseModel):
    """
    Response model for KnowledgeChunk resources.
    
    Represents a single chunk of content within a knowledge source. Knowledge
    chunks are the individual pieces of text that make up a knowledge source
    and are used for AI-powered search and retrieval.
    
    Used for both GET single chunk and GET list (items) responses.
    
    Attributes:
        id: MongoDB ObjectId of the knowledge chunk (24 hex characters).
        order: The order/position of the chunk within the source.
        text: The actual text content of the chunk.
        data: Extended data associated with the chunk (arbitrary key-value pairs).
        disabled: Whether the knowledge chunk is disabled and excluded from search.
        reference_id: UUID reference for the knowledge chunk.
        created_at: Unix timestamp when the chunk was created (0 to 2147483647).
        created_by: ObjectId of user who created the chunk.
        last_changed: Unix timestamp when the chunk was last modified (0 to 2147483647).
        last_changed_by: ObjectId of user who last modified the chunk.
    """
    order: Optional[float] = Field(
        None,
        description="The order/position of the chunk within the source"
    )
    text: Optional[str] = Field(
        None,
        description="The actual text content of the chunk"
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Extended data associated with the chunk"
    )
    disabled: Optional[bool] = Field(
        None,
        description="Whether the knowledge chunk is disabled and excluded from search"
    )
    reference_id: Optional[str] = Field(
        None,
        alias="referenceId",
        description="UUID reference for the knowledge chunk"
    )
    created_at: Optional[int] = Field(
        None,
        alias="createdAt",
        description="Unix timestamp when the chunk was created"
    )
    created_by: Optional[str] = Field(
        None,
        alias="createdBy",
        description="ObjectId of user who created the chunk"
    )
    last_changed: Optional[int] = Field(
        None,
        alias="lastChanged",
        description="Unix timestamp when the chunk was last modified"
    )
    last_changed_by: Optional[str] = Field(
        None,
        alias="lastChangedBy",
        description="ObjectId of user who last modified the chunk"
    )

    @field_validator("reference_id")
    @classmethod
    def validate_reference_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate reference_id matches UUID format."""
        if v is not None and not UUID_PATTERN.match(v):
            raise ValueError(
                f"Invalid UUID format for reference_id: "
                f"must be a valid UUID, got '{v}'"
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


class KnowledgeChunkCreate(CognigyBaseModel):
    """
    Input model for creating a KnowledgeChunk.
    
    Contains the required and optional fields for creating a new knowledge chunk
    via the POST /v2.0/knowledgestores/{knowledgeStoreId}/sources/{sourceId}/chunks endpoint.
    
    Attributes:
        order: The order/position of the chunk within the source.
        text: The actual text content of the chunk.
        data: Extended data associated with the chunk (arbitrary key-value pairs).
    
    Example:
        >>> chunk_data = KnowledgeChunkCreate(
        ...     order=1,
        ...     text="This is a paragraph from an article"
        ... )
    """
    order: Optional[float] = Field(
        None,
        description="The order/position of the chunk within the source"
    )
    text: Optional[str] = Field(
        None,
        description="The actual text content of the chunk"
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Extended data associated with the chunk"
    )


class KnowledgeChunkUpdate(CognigyBaseModel):
    """
    Input model for updating a KnowledgeChunk.
    
    Contains the optional fields for updating an existing knowledge chunk
    via the PATCH /v2.0/knowledgestores/{knowledgeStoreId}/sources/{sourceId}/chunks/{chunkId} endpoint.
    Only provided fields will be updated.
    
    Attributes:
        order: New order/position of the chunk within the source.
        text: New text content of the chunk.
        data: New extended data associated with the chunk.
        disabled: Whether to disable/enable the knowledge chunk.
    
    Example:
        >>> update_data = KnowledgeChunkUpdate(
        ...     text="Updated paragraph text",
        ...     disabled=False
        ... )
    """
    order: Optional[float] = Field(
        None,
        description="New order/position of the chunk within the source"
    )
    text: Optional[str] = Field(
        None,
        description="New text content of the chunk"
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="New extended data associated with the chunk"
    )
    disabled: Optional[bool] = Field(
        None,
        description="Whether to disable/enable the knowledge chunk"
    )
