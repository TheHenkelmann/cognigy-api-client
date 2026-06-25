"""
Connection models for the Cognigy API (v2.0 /connections).

This module contains Pydantic models for Connection resources including
response models, create/update request models, batch operation models,
and Connection schema metadata.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any, Literal, Union

from pydantic import ConfigDict, Field, field_validator

from .base import CognigyBaseModel, CognigyCreateUpdateModel, to_camel

OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")


def _validate_object_id(value: str | None, field_name: str) -> str | None:
    if value is not None and not OBJECT_ID_PATTERN.match(value):
        raise ValueError(
            f"Invalid ObjectId format for {field_name}: "
            f"must be 24 lowercase hex characters, got {value!r}"
        )
    return value


class ResourceLevel(str, Enum):
    """Scope of a Connection resource."""

    ORGANISATION = "organisation"
    PROJECT = "project"


class ConnectionSchemaRef(CognigyBaseModel):
    """Inline connection schema reference returned on list items."""

    extension: str | None = Field(None, description="The package-name of the extension.")
    type: str | None = Field(None, description="The type of connection.")


class ConnectionListItem(CognigyBaseModel):
    """Metadata for one Connection in GET /v2.0/connections list responses."""

    name: str | None = None
    is_deprecated: bool | None = None
    connection_schema: ConnectionSchemaRef | None = None
    created_at: int | None = None
    last_changed: int | None = None
    created_by: str | None = None
    last_changed_by: str | None = None

    @field_validator("created_by", "last_changed_by")
    @classmethod
    def _validate_object_ids(cls, v: str | None, info) -> str | None:
        return _validate_object_id(v, info.field_name)


class Connection(CognigyBaseModel):
    """
    Full Connection document (GET /v2.0/connections/{connectionId}).

    The API returns a nested Connection object; known fields are mapped and
    any additional fields are preserved via ``extra="allow"``.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        alias_generator=to_camel,
    )

    name: str | None = None
    is_deprecated: bool | None = None
    type: str | None = None
    extension: str | None = None
    fields: dict[str, Any] | None = Field(
        None,
        description="Key-Value pairs matching the connection schema.",
    )
    connection_schema: ConnectionSchemaRef | None = None
    resource_level: ResourceLevel | None = None
    created_at: int | None = None
    last_changed: int | None = None
    created_by: str | None = None
    last_changed_by: str | None = None

    @field_validator("created_by", "last_changed_by")
    @classmethod
    def _validate_object_ids(cls, v: str | None, info) -> str | None:
        return _validate_object_id(v, info.field_name)


class ConnectionCreate(CognigyCreateUpdateModel):
    """
    POST /v2.0/connections body.

    Either ``project_id`` or ``resource_level=ResourceLevel.ORGANISATION``
    must be set.
    """

    name: str = Field(..., description="The human-readable Connection name.")
    type: str = Field(
        ...,
        description="Connection type (e.g. 'http_basic'). Must match the schema.",
    )
    extension: str = Field(
        ...,
        description="The extension providing the connection type (e.g. '@cognigy/basic-nodes').",
    )
    fields: dict[str, Any] = Field(
        ...,
        description="Key-Value pairs for the connection fields (1..10 entries).",
        min_length=1,
        max_length=10,
    )
    is_deprecated: bool | None = Field(None, description="Mark the connection type as deprecated.")
    project_id: str | None = Field(
        None,
        description="Project ObjectId. Required when not using resource_level='organisation'.",
    )
    resource_level: ResourceLevel | None = Field(
        None,
        description="Set to ResourceLevel.ORGANISATION for organisation-scoped connections.",
    )

    @field_validator("project_id")
    @classmethod
    def _validate_project_id(cls, v: str | None) -> str | None:
        return _validate_object_id(v, "project_id")


class ConnectionUpdate(CognigyCreateUpdateModel):
    """PATCH /v2.0/connections/{connectionId} body."""

    fields: dict[str, Any] = Field(
        ...,
        description="Key-Value pairs for the connection fields (1..10 entries).",
        min_length=1,
        max_length=10,
    )


class ConnectionFieldCreate(CognigyCreateUpdateModel):
    """POST /v2.0/connections/{connectionId}/fields body."""

    key: str = Field(..., description="The field key from the connection schema.")
    value: str = Field(..., description="The field value.")


class ConnectionBatchCreateValue(CognigyCreateUpdateModel):
    """The ``value`` payload of a batch ``create`` operation."""

    name: str = Field(...)
    type: str = Field(...)
    extension: str = Field(...)
    fields: dict[str, Any] = Field(..., min_length=1, max_length=10)
    is_deprecated: bool | None = None


class ConnectionBatchUpdateValue(CognigyCreateUpdateModel):
    """The ``value`` payload of a batch ``update`` operation."""

    fields: dict[str, Any] = Field(..., min_length=1, max_length=10)


class ConnectionBatchDeleteOp(CognigyCreateUpdateModel):
    """Delete operation entry for batch requests."""

    op: Literal["delete"] = "delete"
    id: str = Field(..., description="Connection ObjectId to delete.")

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        _validate_object_id(v, "id")
        return v


class ConnectionBatchCreateOp(CognigyCreateUpdateModel):
    """Create operation entry for batch requests."""

    op: Literal["create"] = "create"
    value: ConnectionBatchCreateValue


class ConnectionBatchUpdateOp(CognigyCreateUpdateModel):
    """Update operation entry for batch requests."""

    op: Literal["update"] = "update"
    id: str = Field(..., description="Connection ObjectId to update.")
    value: ConnectionBatchUpdateValue

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        _validate_object_id(v, "id")
        return v


ConnectionBatchOperation = Union[
    ConnectionBatchCreateOp,
    ConnectionBatchUpdateOp,
    ConnectionBatchDeleteOp,
]


class ConnectionBatchRequest(CognigyCreateUpdateModel):
    """PATCH /v2.0/connections body (batch operations)."""

    operations: list[ConnectionBatchOperation] = Field(
        ...,
        description="Ordered list of create/update/delete operations.",
    )


class ConnectionBatchResult(CognigyBaseModel):
    """Response body of PATCH /v2.0/connections."""

    created: list[str] | None = None
    updated: list[str] | None = None
    deleted: list[str] | None = None


class ConnectionSchemaItem(CognigyBaseModel):
    """
    Metadata for one Connection schema in GET /v2.0/connections/schemas
    list responses.

    Additional fields (``type``, ``label``, ``fields`` definitions, ...) are
    preserved via ``extra='allow'`` so callers can inspect the raw schema.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        alias_generator=to_camel,
    )

    extension: str | None = Field(
        None,
        description="The package name of the extension providing this schema.",
    )
    created_at: int | None = None
    last_changed: int | None = None
    created_by: str | None = None
    last_changed_by: str | None = None

    @field_validator("created_by", "last_changed_by")
    @classmethod
    def _validate_object_ids(cls, v: str | None, info) -> str | None:
        return _validate_object_id(v, info.field_name)
