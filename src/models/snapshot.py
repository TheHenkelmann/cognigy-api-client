"""
Snapshot models for the Cognigy API.

This module contains Pydantic models for Snapshot resources including
response models, create request models, and related nested models.
"""

import re
from typing import Optional
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


class Snapshot(CognigyBaseModel):
    """
    Response model for Snapshot resources.
    
    Represents a Cognigy Snapshot, which is a point-in-time backup of project resources.
    Used for both GET single snapshot and GET list responses.
    
    Attributes:
        id: MongoDB ObjectId of the snapshot (24 hex characters).
        name: Name of the snapshot.
        description: Optional description of the snapshot.
        is_packaged: Whether the snapshot has been packaged and is ready for download.
        package_expires_at: Unix timestamp when the downloadable package expires.
        hash: Hash identifying the contents of the snapshot.
        created_by: ObjectId of user who created the snapshot (24 hex characters).
        created_at: Unix timestamp when snapshot was created (0 to 2147483647).
    """
    name: Optional[str] = Field(
        None,
        description="Name of the snapshot"
    )
    description: Optional[str] = Field(
        None,
        description="Description of the snapshot"
    )
    is_packaged: Optional[bool] = Field(
        None,
        alias="isPackaged",
        description="Whether the snapshot has been packaged and is ready for download"
    )
    package_expires_at: Optional[int] = Field(
        None,
        alias="packageExpiresAt",
        description="Unix timestamp when the downloadable package expires"
    )
    hash: Optional[str] = Field(
        None,
        description="Hash identifying the contents of the snapshot"
    )
    created_by: Optional[str] = Field(
        None,
        alias="createdBy",
        description="ObjectId of user who created the snapshot"
    )
    created_at: Optional[int] = Field(
        None,
        alias="createdAt",
        description="Unix timestamp when snapshot was created"
    )

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate created_by matches ObjectId format."""
        return _validate_object_id(v, "created_by")

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: Optional[int]) -> Optional[int]:
        """Validate created_at is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "created_at")


class SnapshotCreate(CognigyBaseModel):
    """
    Input model for creating a Snapshot.
    
    Contains the required and optional fields for creating a new snapshot
    via the POST /v2.0/snapshots endpoint. Note that creating a snapshot
    creates a background Task that performs the actual snapshot creation.
    
    Attributes:
        name: Name of the snapshot.
        description: Optional description of the snapshot.
        project_id: ObjectId of the project to create the snapshot from (required).
    """
    name: Optional[str] = Field(
        None,
        description="Name of the snapshot"
    )
    description: Optional[str] = Field(
        None,
        description="Description of the snapshot"
    )
    project_id: str = Field(
        ...,
        alias="projectId",
        description="ObjectId of the project to create the snapshot from"
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


class SnapshotResource(CognigyBaseModel):
    """
    Response model for resources contained in a Snapshot.
    
    Represents a single resource item included in a snapshot.
    Used in the GET /v2.0/snapshots/{snapshotId}/resources response.
    
    Attributes:
        id: MongoDB ObjectId of the resource (24 hex characters).
        name: Name of the resource.
        reference_id: Reference ID of the resource.
        resource_type: Type of resource (e.g., 'flow', 'lexicon').
        created_by: ObjectId of user who created the resource (24 hex characters).
        created_at: Unix timestamp when resource was created (0 to 2147483647).
    """
    name: Optional[str] = Field(
        None,
        description="Name of the resource"
    )
    reference_id: Optional[str] = Field(
        None,
        alias="referenceId",
        description="Reference ID of the resource"
    )
    resource_type: Optional[str] = Field(
        None,
        alias="resourceType",
        description="Type of resource (e.g., 'flow', 'lexicon')"
    )
    created_by: Optional[str] = Field(
        None,
        alias="createdBy",
        description="ObjectId of user who created the resource"
    )
    created_at: Optional[int] = Field(
        None,
        alias="createdAt",
        description="Unix timestamp when resource was created"
    )

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate created_by matches ObjectId format."""
        return _validate_object_id(v, "created_by")

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: Optional[int]) -> Optional[int]:
        """Validate created_at is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "created_at")


class SnapshotDownloadLink(CognigyBaseModel):
    """
    Response model for snapshot download link creation.
    
    Returned by the POST /v2.0/snapshots/{snapshotId}/downloadlink endpoint.
    
    Attributes:
        download_link: URL to download the snapshot package.
    """
    download_link: str = Field(
        ...,
        alias="downloadLink",
        description="URL to download the snapshot package"
    )


class SnapshotRestoreRequest(CognigyBaseModel):
    """
    Input model for restoring a Snapshot.
    
    Contains the required fields for restoring a snapshot to a project
    via the POST /v2.0/snapshots/{snapshotId}/restore endpoint.
    Note that restoring a snapshot creates a background Task.
    
    Attributes:
        project_id: ObjectId of the project to restore the snapshot to (required).
    """
    project_id: str = Field(
        ...,
        alias="projectId",
        description="ObjectId of the project to restore the snapshot to"
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


class SnapshotDownloadLinkRequest(CognigyBaseModel):
    """
    Input model for creating a snapshot download link.
    
    Contains the optional fields for creating a download link
    via the POST /v2.0/snapshots/{snapshotId}/downloadlink endpoint.
    
    Attributes:
        project_id: Optional ObjectId of the project (24 hex characters).
    """
    project_id: Optional[str] = Field(
        None,
        alias="projectId",
        description="ObjectId of the project"
    )

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate project_id matches ObjectId format."""
        return _validate_object_id(v, "project_id")
