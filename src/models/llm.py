"""
LLM (large language model) models for the Cognigy API.

Covers v2.0 ``/largelanguagemodels`` list, create, read, update, delete, and test.
"""

from __future__ import annotations

import re
from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from .base import CognigyBaseModel, CognigyCreateUpdateModel, to_camel

_CREATE_CONFIG = ConfigDict(
    populate_by_name=True,
    alias_generator=to_camel,
    extra="forbid",
)

OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _validate_object_id(value: str | None, field_name: str) -> str | None:
    if value is not None and not OBJECT_ID_PATTERN.match(value):
        raise ValueError(
            f"Invalid ObjectId format for {field_name}: "
            f"must be 24 lowercase hex characters, got {value!r}"
        )
    return value


def _validate_unix_timestamp(value: int | None, field_name: str) -> int | None:
    if value is not None and (value < 0 or value > 2147483647):
        raise ValueError(
            f"Unix timestamp for {field_name} must be between 0 and 2147483647, got {value}"
        )
    return value


class LLM(CognigyBaseModel):
    """Response model for a Cognigy LLM (GET / list item)."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        alias_generator=to_camel,
    )

    name: str | None = None
    description: str | None = None
    model_type: str | None = Field(None, alias="modelType")
    model_group: str | None = Field(None, alias="modelGroup")
    is_custom_model: bool | None = Field(None, alias="isCustomModel")
    provider: str | None = None
    connection_id: str | None = Field(None, alias="connectionId")
    resource_level: Literal["project", "organisation"] | None = Field(None, alias="resourceLevel")
    is_default: bool | None = Field(None, alias="isDefault")
    assigned_to_projects: list[str] | None = Field(None, alias="assignedToProjects")
    fallbacks: list[dict[str, Any]] | None = None
    created_at: int | None = Field(None, alias="createdAt")
    created_by: str | None = Field(None, alias="createdBy")
    last_changed: int | None = Field(None, alias="lastChanged")
    last_changed_by: str | None = Field(None, alias="lastChangedBy")

    @field_validator("created_at", "last_changed")
    @classmethod
    def _ts(cls, v: int | None, info: ValidationInfo) -> int | None:
        field_name = info.field_name or "timestamp"
        return _validate_unix_timestamp(v, field_name)

    @field_validator("created_by", "last_changed_by")
    @classmethod
    def _oid(cls, v: str | None, info: ValidationInfo) -> str | None:
        field_name = info.field_name or "object_id"
        return _validate_object_id(v, field_name)

    @field_validator("connection_id")
    @classmethod
    def _uuid(cls, v: str | None) -> str | None:
        if v is not None and not UUID_PATTERN.match(v):
            raise ValueError(f"connection_id must be a UUID string, got {v!r}")
        return v


class LLMCreateForProject(CognigyCreateUpdateModel):
    """POST body for a project-scoped LLM (``projectId`` required)."""

    model_config = _CREATE_CONFIG

    name: str
    model_type: str = Field(..., alias="modelType")
    provider: str
    connection_id: str = Field(..., alias="connectionId")
    project_id: str = Field(..., alias="projectId")
    description: str | None = None
    model_group: str | None = Field(None, alias="modelGroup")
    is_custom_model: bool | None = Field(None, alias="isCustomModel")
    resource_level: Literal["project"] = Field("project", alias="resourceLevel")
    is_default: bool | None = Field(None, alias="isDefault")
    fallbacks: list[dict[str, Any]] | None = None
    open_ai: dict[str, Any] | None = Field(None, alias="openAI")
    anthropic: dict[str, Any] | None = None
    azure_open_ai: dict[str, Any] | None = Field(None, alias="azureOpenAI")
    google_vertex_ai: dict[str, Any] | None = Field(None, alias="googleVertexAI")
    google_gemini: dict[str, Any] | None = Field(None, alias="googleGemini")
    aleph_alpha: dict[str, Any] | None = Field(None, alias="alephAlpha")
    open_ai_compatible: dict[str, Any] | None = Field(None, alias="openAICompatible")

    @field_validator("project_id")
    @classmethod
    def _pid(cls, v: str) -> str:
        _validate_object_id(v, "project_id")
        return v

    @field_validator("connection_id")
    @classmethod
    def _cid(cls, v: str) -> str:
        if not UUID_PATTERN.match(v):
            raise ValueError(f"connection_id must be a UUID string, got {v!r}")
        return v


class LLMCreateForOrganisation(CognigyCreateUpdateModel):
    """POST body for an organisation-scoped (global) LLM."""

    model_config = _CREATE_CONFIG

    name: str
    model_type: str = Field(..., alias="modelType")
    provider: str
    connection_id: str = Field(..., alias="connectionId")
    resource_level: Literal["organisation"] = Field(..., alias="resourceLevel")
    description: str | None = None
    model_group: str | None = Field(None, alias="modelGroup")
    is_custom_model: bool | None = Field(None, alias="isCustomModel")
    assigned_to_projects: list[str] | None = Field(None, alias="assignedToProjects")
    open_ai: dict[str, Any] | None = Field(None, alias="openAI")
    anthropic: dict[str, Any] | None = None
    azure_open_ai: dict[str, Any] | None = Field(None, alias="azureOpenAI")
    google_vertex_ai: dict[str, Any] | None = Field(None, alias="googleVertexAI")
    google_gemini: dict[str, Any] | None = Field(None, alias="googleGemini")
    aleph_alpha: dict[str, Any] | None = Field(None, alias="alephAlpha")
    open_ai_compatible: dict[str, Any] | None = Field(None, alias="openAICompatible")

    @field_validator("connection_id")
    @classmethod
    def _cid(cls, v: str) -> str:
        if not UUID_PATTERN.match(v):
            raise ValueError(f"connection_id must be a UUID string, got {v!r}")
        return v


LLMCreate = Union[LLMCreateForProject, LLMCreateForOrganisation]


class LLMUpdate(CognigyCreateUpdateModel):
    """PATCH body for ``/v2.0/largelanguagemodels/{id}``."""

    name: str | None = None
    description: str | None = None
    provider: str | None = None
    connection_id: str | None = Field(None, alias="connectionId")
    is_default: bool | None = Field(None, alias="isDefault")

    @field_validator("connection_id")
    @classmethod
    def _cid(cls, v: str | None) -> str | None:
        if v is not None and not UUID_PATTERN.match(v):
            raise ValueError(f"connection_id must be a UUID string, got {v!r}")
        return v


class LLMTestResult(BaseModel):
    """Response from ``POST .../largelanguagemodels/{id}/test`` (no request body)."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    voice_provider: str | None = Field(None, alias="voiceProvider")
    is_credentials_valid: bool | None = Field(None, alias="isCredentialsValid")
    msg: str | None = None
    msg_err: str | None = Field(None, alias="msgErr")
