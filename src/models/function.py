"""
Function models for the Cognigy API.

This module contains Pydantic models for Function resources including
response models and create/update request models.
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


class Function(CognigyBaseModel):
    """
    Response model for Function resources.

    Represents a Cognigy Function which contains JavaScript source code
    that can be executed in a Project. Used for both GET single function
    and GET list responses.

    Attributes:
        id: MongoDB ObjectId of the function (24 hex characters).
        name: Human-readable name of the function.
        code: JavaScript source code of the function.
        is_disabled: Whether the function is disabled (will not execute).
        reference_id: Reference UUID of the function (only present in list responses).
        created_at: Unix timestamp when the function was created (0 to 2147483647).
        created_by: ObjectId of the user who created the function.
        last_changed: Unix timestamp when the function was last modified (0 to 2147483647).
        last_changed_by: ObjectId of the user who last modified the function.
    """
    name: Optional[str] = Field(
        None,
        description="Human-readable name of the function"
    )
    code: Optional[str] = Field(
        None,
        description="JavaScript source code of the function"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether the function is disabled"
    )
    created_at: Optional[int] = Field(
        None,
        alias="createdAt",
        description="Unix timestamp when the function was created"
    )
    created_by: Optional[str] = Field(
        None,
        alias="createdBy",
        description="ObjectId of the user who created the function"
    )
    last_changed: Optional[int] = Field(
        None,
        alias="lastChanged",
        description="Unix timestamp when the function was last modified"
    )
    last_changed_by: Optional[str] = Field(
        None,
        alias="lastChangedBy",
        description="ObjectId of the user who last modified the function"
    )

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


class FunctionCreate(CognigyBaseModel):
    """
    Input model for creating a Function.

    Contains the required and optional fields for creating a new function
    via the POST /v2.0/functions endpoint.

    Attributes:
        project_id: ObjectId of the project to create the function in (required).
        name: Human-readable name of the function.
        code: JavaScript source code of the function.
        is_disabled: Whether the function should be created as disabled.

    Example:
        >>> from cognigy.models import FunctionCreate
        >>> function_data = FunctionCreate(
        ...     project_id="507f1f77bcf86cd799439011",
        ...     name="My Function",
        ...     code="console.log('Hello World');",
        ...     is_disabled=False
        ... )
    """
    project_id: str = Field(
        ...,
        alias="projectId",
        description="ObjectId of the project to create the function in"
    )
    name: Optional[str] = Field(
        None,
        description="Human-readable name of the function"
    )
    code: Optional[str] = Field(
        None,
        description="JavaScript source code of the function"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether the function should be created as disabled"
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


class FunctionUpdate(CognigyBaseModel):
    """
    Input model for updating a Function.

    Contains the optional fields for updating an existing function
    via the PATCH /v2.0/functions/{functionId} endpoint. Only provided
    fields will be updated.

    Attributes:
        name: New human-readable name of the function.
        code: New JavaScript source code of the function.
        is_disabled: Whether the function should be disabled.

    Example:
        >>> from cognigy.models import FunctionUpdate
        >>> update_data = FunctionUpdate(
        ...     name="Updated Function Name",
        ...     code="console.log('Updated');",
        ...     is_disabled=True
        ... )
    """
    name: Optional[str] = Field(
        None,
        description="New human-readable name of the function"
    )
    code: Optional[str] = Field(
        None,
        description="New JavaScript source code of the function"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether the function should be disabled"
    )
