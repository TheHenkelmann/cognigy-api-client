"""
Flow models for the Cognigy API.

This module contains Pydantic models for Flow resources including
response models, create/update request models, and related nested models.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import Field, field_validator

from .base import CognigyBaseModel

# Validation patterns
OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def _validate_object_id(value: str | None, field_name: str) -> str | None:
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


def _validate_object_id_list(values: list[str] | None, field_name: str) -> list[str] | None:
    """
    Validate that all strings in a list match MongoDB ObjectId format.

    Args:
        values: List of string values to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated list if all items are valid.

    Raises:
        ValueError: If any value doesn't match the ObjectId pattern.
    """
    if values is not None:
        for i, value in enumerate(values):
            if not OBJECT_ID_PATTERN.match(value):
                raise ValueError(
                    f"Invalid ObjectId format for {field_name}[{i}]: "
                    f"must be 24 lowercase hex characters, got '{value}'"
                )
    return values


def _validate_unix_timestamp(value: int | None, field_name: str) -> int | None:
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


class FeedbackReportInfo(CognigyBaseModel):
    """
    Information section of a feedback report.

    Contains metrics about the training quality.

    Attributes:
        f_score: F-score metric indicating model accuracy (0.0 to 1.0).
    """

    f_score: float | None = Field(None, alias="fScore", description="F-score metric (0.0 to 1.0)")


class LowDataIntent(CognigyBaseModel):
    """
    Intent information in low data findings.

    Contains details about intents that have insufficient training data.
    This information is included in feedback reports when the finding type
    is 'lowDataIntents'.

    Attributes:
        intent_reference_id: Reference ID of the intent.
        intent_name: Human-readable name of the intent.
        intent_id: MongoDB ObjectId of the intent (24 hex characters).
        flow_name: Name of the flow containing the intent.
        flow_id: MongoDB ObjectId of the flow (24 hex characters).
    """

    intent_reference_id: str | None = Field(
        None, alias="intentReferenceId", description="Reference ID of the intent"
    )
    intent_name: str | None = Field(
        None, alias="intentName", description="Human-readable name of the intent"
    )
    intent_id: str | None = Field(
        None, alias="intentId", description="MongoDB ObjectId of the intent"
    )
    flow_name: str | None = Field(
        None, alias="flowName", description="Name of the flow containing the intent"
    )
    flow_id: str | None = Field(None, alias="flowId", description="MongoDB ObjectId of the flow")

    @field_validator("intent_id")
    @classmethod
    def validate_intent_id(cls, v: str | None) -> str | None:
        """Validate intent_id matches ObjectId format."""
        return _validate_object_id(v, "intent_id")

    @field_validator("flow_id")
    @classmethod
    def validate_flow_id(cls, v: str | None) -> str | None:
        """Validate flow_id matches ObjectId format."""
        return _validate_object_id(v, "flow_id")


class FeedbackReportFinding(CognigyBaseModel):
    """
    A finding from the feedback report.

    Represents a single finding in the training feedback report.
    The type indicates what kind of finding it is, and for 'lowDataIntents'
    type, additional intent information is provided.

    Attributes:
        type: Type of finding. One of: 'poorAccuracy', 'fairAccuracy',
              'goodAccuracy', 'lowDataIntents'.
        intents: List of intents with low training data. Only present
                 when type is 'lowDataIntents'.
    """

    type: str | None = Field(
        None,
        description="Type of finding: poorAccuracy, fairAccuracy, goodAccuracy, lowDataIntents",
    )
    intents: list[LowDataIntent] | None = Field(
        None, description="List of intents with low data (only for lowDataIntents type)"
    )


class FeedbackReport(CognigyBaseModel):
    """
    Training feedback report for a Flow.

    Contains findings about the quality of intent training and
    metrics about model accuracy.

    Attributes:
        findings: List of findings from the training analysis.
        info: Additional information including accuracy metrics.
    """

    findings: list[FeedbackReportFinding] | None = Field(
        None, description="List of findings from training analysis"
    )
    info: FeedbackReportInfo | None = Field(None, description="Training metrics information")


class Flow(CognigyBaseModel):
    """
    Response model for Flow resources.

    Represents a Cognigy Flow containing conversational logic.
    Used for both GET single flow and GET list responses.

    Attributes:
        id: MongoDB ObjectId of the flow (24 hex characters).
        name: Name of the flow.
        description: Optional description of the flow.
        reference_id: UUID reference for the flow.
        intent_train_group_reference: ObjectId of the intent training group.
        feedback_report: Training feedback report with accuracy findings.
        is_training_out_of_date: Whether the flow needs retraining.
        context: Default context object for the flow.
        attached_flows: List of ObjectIds of attached flows.
        attached_lexicons: List of ObjectIds of attached lexicons.
        img: Optional image URL for the flow.
        created_at: Unix timestamp when flow was created (0 to 2147483647).
        created_by: ObjectId of user who created the flow.
        last_changed: Unix timestamp when flow was last modified (0 to 2147483647).
        last_changed_by: ObjectId of user who last modified the flow.
    """

    name: str = Field(..., description="Name of the flow")
    description: str | None = Field(None, description="Description of the flow")
    reference_id: str | None = Field(
        None, alias="referenceId", description="UUID reference for the flow"
    )
    intent_train_group_reference: str | None = Field(
        None, alias="intentTrainGroupReference", description="ObjectId of the intent training group"
    )
    feedback_report: FeedbackReport | None = Field(
        None, alias="feedbackReport", description="Training feedback report"
    )
    is_training_out_of_date: bool | None = Field(
        None, alias="isTrainingOutOfDate", description="Whether the flow needs retraining"
    )
    context: dict[str, Any] | None = Field(None, description="Default context object for the flow")
    attached_flows: list[str] | None = Field(
        None, alias="attachedFlows", description="List of ObjectIds of attached flows"
    )
    attached_lexicons: list[str] | None = Field(
        None, alias="attachedLexicons", description="List of ObjectIds of attached lexicons"
    )
    img: str | None = Field(None, description="Image URL for the flow")
    created_at: int | None = Field(
        None, alias="createdAt", description="Unix timestamp when flow was created"
    )
    created_by: str | None = Field(
        None, alias="createdBy", description="ObjectId of user who created the flow"
    )
    last_changed: int | None = Field(
        None, alias="lastChanged", description="Unix timestamp when flow was last modified"
    )
    last_changed_by: str | None = Field(
        None, alias="lastChangedBy", description="ObjectId of user who last modified the flow"
    )

    @field_validator("intent_train_group_reference")
    @classmethod
    def validate_intent_train_group_reference(cls, v: str | None) -> str | None:
        """Validate intent_train_group_reference matches ObjectId format."""
        return _validate_object_id(v, "intent_train_group_reference")

    @field_validator("attached_flows")
    @classmethod
    def validate_attached_flows(cls, v: list[str] | None) -> list[str] | None:
        """Validate all attached_flows match ObjectId format."""
        return _validate_object_id_list(v, "attached_flows")

    @field_validator("attached_lexicons")
    @classmethod
    def validate_attached_lexicons(cls, v: list[str] | None) -> list[str] | None:
        """Validate all attached_lexicons match ObjectId format."""
        return _validate_object_id_list(v, "attached_lexicons")

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: int | None) -> int | None:
        """Validate created_at is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "created_at")

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, v: str | None) -> str | None:
        """Validate created_by matches ObjectId format."""
        return _validate_object_id(v, "created_by")

    @field_validator("last_changed")
    @classmethod
    def validate_last_changed(cls, v: int | None) -> int | None:
        """Validate last_changed is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "last_changed")

    @field_validator("last_changed_by")
    @classmethod
    def validate_last_changed_by(cls, v: str | None) -> str | None:
        """Validate last_changed_by matches ObjectId format."""
        return _validate_object_id(v, "last_changed_by")


class FlowCreate(CognigyBaseModel):
    """
    Input model for creating a Flow.

    Contains the required and optional fields for creating a new flow
    via the POST /v2.0/flows endpoint.

    Attributes:
        name: Name of the flow (required).
        project_id: ObjectId of the project to create the flow in (required).
        description: Optional description of the flow.
        context: Optional default context object for the flow.
        attached_flows: Optional list of ObjectIds of flows to attach.
        attached_lexicons: Optional list of ObjectIds of lexicons to attach.
        img: Optional image URL for the flow.
    """

    name: str = Field(..., description="Name of the flow")
    project_id: str = Field(
        ..., alias="projectId", description="ObjectId of the project to create the flow in"
    )
    description: str | None = Field(None, description="Description of the flow")
    context: dict[str, Any] | None = Field(None, description="Default context object for the flow")
    attached_flows: list[str] | None = Field(
        None, alias="attachedFlows", description="List of ObjectIds of flows to attach"
    )
    attached_lexicons: list[str] | None = Field(
        None, alias="attachedLexicons", description="List of ObjectIds of lexicons to attach"
    )
    img: str | None = Field(None, description="Image URL for the flow")

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

    @field_validator("attached_flows")
    @classmethod
    def validate_attached_flows(cls, v: list[str] | None) -> list[str] | None:
        """Validate all attached_flows match ObjectId format."""
        return _validate_object_id_list(v, "attached_flows")

    @field_validator("attached_lexicons")
    @classmethod
    def validate_attached_lexicons(cls, v: list[str] | None) -> list[str] | None:
        """Validate all attached_lexicons match ObjectId format."""
        return _validate_object_id_list(v, "attached_lexicons")


class FlowUpdate(CognigyBaseModel):
    """
    Input model for updating a Flow.

    Contains the optional fields for updating an existing flow
    via the PATCH /v2.0/flows/{flowId} endpoint. Only provided
    fields will be updated.

    Attributes:
        name: New name for the flow.
        description: New description for the flow.
        context: New default context object for the flow.
        attached_flows: New list of ObjectIds of flows to attach.
        attached_lexicons: New list of ObjectIds of lexicons to attach.
        img: New image URL for the flow.
        locale_id: ObjectId of the locale for localized updates.
    """

    name: str | None = Field(None, description="New name for the flow")
    description: str | None = Field(None, description="New description for the flow")
    context: dict[str, Any] | None = Field(
        None, description="New default context object for the flow"
    )
    attached_flows: list[str] | None = Field(
        None, alias="attachedFlows", description="New list of ObjectIds of flows to attach"
    )
    attached_lexicons: list[str] | None = Field(
        None, alias="attachedLexicons", description="New list of ObjectIds of lexicons to attach"
    )
    img: str | None = Field(None, description="New image URL for the flow")
    locale_id: str | None = Field(
        None, alias="localeId", description="ObjectId of the locale for localized updates"
    )

    @field_validator("attached_flows")
    @classmethod
    def validate_attached_flows(cls, v: list[str] | None) -> list[str] | None:
        """Validate all attached_flows match ObjectId format."""
        return _validate_object_id_list(v, "attached_flows")

    @field_validator("attached_lexicons")
    @classmethod
    def validate_attached_lexicons(cls, v: list[str] | None) -> list[str] | None:
        """Validate all attached_lexicons match ObjectId format."""
        return _validate_object_id_list(v, "attached_lexicons")

    @field_validator("locale_id")
    @classmethod
    def validate_locale_id(cls, v: str | None) -> str | None:
        """Validate locale_id matches ObjectId format."""
        return _validate_object_id(v, "locale_id")
