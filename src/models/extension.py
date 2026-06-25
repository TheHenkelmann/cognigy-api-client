"""
Extension models for the Cognigy API (v2.0 /extensions).
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import ConfigDict, Field, field_validator

from .base import CognigyBaseModel, CognigyCreateUpdateModel, to_camel
from .task import TaskStatus

OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")


def _validate_object_id(value: str | None, field_name: str) -> str | None:
    if value is not None and not OBJECT_ID_PATTERN.match(value):
        raise ValueError(
            f"Invalid ObjectId format for {field_name}: "
            f"must be 24 lowercase hex characters, got {value!r}"
        )
    return value


class ExtensionListItem(CognigyBaseModel):
    """Metadata for one extension in GET /v2.0/extensions list responses."""

    name: str | None = None
    label: str | None = None
    version: str | None = None
    image_url_token: str | None = None
    description: str | None = None
    trusted_code: bool | None = None
    created_at: int | None = None
    last_changed: int | None = None
    created_by: str | None = None
    last_changed_by: str | None = None

    @field_validator("created_by", "last_changed_by")
    @classmethod
    def validate_object_ids(cls, v: str | None, info) -> str | None:
        return _validate_object_id(v, info.field_name)


class Extension(CognigyBaseModel):
    """
    Full extension document from GET /v2.0/extensions/{extensionId}.

    The API returns a large nested structure; known fields are mapped and
    the rest are preserved via extra=\"allow\".
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        alias_generator=to_camel,
    )

    name: str | None = None
    label: str | None = None
    version: str | None = None
    image_url_token: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    author: str | None = None
    extension_type: str | None = None
    trusted_code: bool | None = None
    created_at: int | None = None
    last_changed: int | None = None
    created_by: str | None = None
    last_changed_by: str | None = None

    @field_validator("created_by", "last_changed_by")
    @classmethod
    def validate_object_ids(cls, v: str | None, info) -> str | None:
        return _validate_object_id(v, info.field_name)


class ExtensionSettingsUpdate(CognigyCreateUpdateModel):
    """PATCH /v2.0/extensions/{extensionId} body (trusted code)."""

    trusted_code: bool | None = Field(
        None,
        description="Whether to trust the code within this extension.",
    )


class ExtensionUploadByUrl(CognigyCreateUpdateModel):
    """JSON body for POST /v2.0/extensions/upload."""

    project_id: str = Field(
        ...,
        description="Project ObjectId (24 hex characters).",
    )
    url: str = Field(..., description="URL to a .tar.gz extension package.")
    name: str | None = Field(
        None,
        description="Optional name for task metadata.",
    )

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        _validate_object_id(v, "project_id")
        return v


class ExtensionUpdatePackageByUrl(CognigyCreateUpdateModel):
    """JSON body for POST /v2.0/extensions/update."""

    project_id: str = Field(..., description="Project ObjectId.")
    url: str = Field(..., description="URL to a .tar.gz extension package.")
    extension: str = Field(
        ...,
        description="Extension id or name to replace.",
    )

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        _validate_object_id(v, "project_id")
        return v


class ExtensionBackgroundTask(CognigyBaseModel):
    """Task object returned with HTTP 202 from upload/update extension endpoints."""

    status: TaskStatus | None = None
    type: str | None = None
    parameters: dict[str, Any] | None = None
    last_changed_at: float | None = Field(None, alias="lastChangedAt")
    last_created_at: float | None = Field(None, alias="lastCreatedAt")
    current_step: int | None = Field(None, alias="currentStep")
    total_step: int | None = Field(None, alias="totalStep")
