"""
LLM (large language model) models for the Cognigy API.

Covers v2.0 ``/largelanguagemodels`` list, create, read, update, delete, and test.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional, Union

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


def _validate_object_id(value: Optional[str], field_name: str) -> Optional[str]:
    if value is not None and not OBJECT_ID_PATTERN.match(value):
        raise ValueError(
            f"Invalid ObjectId format for {field_name}: "
            f"must be 24 lowercase hex characters, got {value!r}"
        )
    return value


def _validate_unix_timestamp(value: Optional[int], field_name: str) -> Optional[int]:
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

    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = Field(None, alias="modelType")
    model_group: Optional[str] = Field(None, alias="modelGroup")
    is_custom_model: Optional[bool] = Field(None, alias="isCustomModel")
    provider: Optional[str] = None
    connection_id: Optional[str] = Field(None, alias="connectionId")
    resource_level: Optional[Literal["project", "organisation"]] = Field(
        None, alias="resourceLevel"
    )
    is_default: Optional[bool] = Field(None, alias="isDefault")
    assigned_to_projects: Optional[List[str]] = Field(None, alias="assignedToProjects")
    fallbacks: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[int] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    last_changed: Optional[int] = Field(None, alias="lastChanged")
    last_changed_by: Optional[str] = Field(None, alias="lastChangedBy")

    @field_validator("created_at", "last_changed")
    @classmethod
    def _ts(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        return _validate_unix_timestamp(v, info.field_name)

    @field_validator("created_by", "last_changed_by")
    @classmethod
    def _oid(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        return _validate_object_id(v, info.field_name)

    @field_validator("connection_id")
    @classmethod
    def _uuid(cls, v: Optional[str]) -> Optional[str]:
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
    description: Optional[str] = None
    model_group: Optional[str] = Field(None, alias="modelGroup")
    is_custom_model: Optional[bool] = Field(None, alias="isCustomModel")
    resource_level: Literal["project"] = Field("project", alias="resourceLevel")
    is_default: Optional[bool] = Field(None, alias="isDefault")
    fallbacks: Optional[List[Dict[str, Any]]] = None
    open_ai: Optional[Dict[str, Any]] = Field(None, alias="openAI")
    anthropic: Optional[Dict[str, Any]] = None
    azure_open_ai: Optional[Dict[str, Any]] = Field(None, alias="azureOpenAI")
    google_vertex_ai: Optional[Dict[str, Any]] = Field(None, alias="googleVertexAI")
    google_gemini: Optional[Dict[str, Any]] = Field(None, alias="googleGemini")
    aleph_alpha: Optional[Dict[str, Any]] = Field(None, alias="alephAlpha")
    open_ai_compatible: Optional[Dict[str, Any]] = Field(None, alias="openAICompatible")

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
    description: Optional[str] = None
    model_group: Optional[str] = Field(None, alias="modelGroup")
    is_custom_model: Optional[bool] = Field(None, alias="isCustomModel")
    assigned_to_projects: Optional[List[str]] = Field(None, alias="assignedToProjects")
    open_ai: Optional[Dict[str, Any]] = Field(None, alias="openAI")
    anthropic: Optional[Dict[str, Any]] = None
    azure_open_ai: Optional[Dict[str, Any]] = Field(None, alias="azureOpenAI")
    google_vertex_ai: Optional[Dict[str, Any]] = Field(None, alias="googleVertexAI")
    google_gemini: Optional[Dict[str, Any]] = Field(None, alias="googleGemini")
    aleph_alpha: Optional[Dict[str, Any]] = Field(None, alias="alephAlpha")
    open_ai_compatible: Optional[Dict[str, Any]] = Field(None, alias="openAICompatible")

    @field_validator("connection_id")
    @classmethod
    def _cid(cls, v: str) -> str:
        if not UUID_PATTERN.match(v):
            raise ValueError(f"connection_id must be a UUID string, got {v!r}")
        return v


LLMCreate = Union[LLMCreateForProject, LLMCreateForOrganisation]


class LLMUpdate(CognigyCreateUpdateModel):
    """PATCH body for ``/v2.0/largelanguagemodels/{id}``."""

    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None
    connection_id: Optional[str] = Field(None, alias="connectionId")
    is_default: Optional[bool] = Field(None, alias="isDefault")

    @field_validator("connection_id")
    @classmethod
    def _cid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not UUID_PATTERN.match(v):
            raise ValueError(f"connection_id must be a UUID string, got {v!r}")
        return v


class LLMTestResult(BaseModel):
    """Response from ``POST .../largelanguagemodels/{id}/test`` (no request body)."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    voice_provider: Optional[str] = Field(None, alias="voiceProvider")
    is_credentials_valid: Optional[bool] = Field(None, alias="isCredentialsValid")
    msg: Optional[str] = None
    msg_err: Optional[str] = Field(None, alias="msgErr")
