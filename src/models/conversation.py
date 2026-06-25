"""
Conversation models for the Cognigy API.

This module contains Pydantic models for Conversation resources including
list (summary) items and conversation detail (message) items per conversations v2.0 API.
"""

import re
from typing import Any, Optional

from pydantic import Field, field_validator

from .base import CognigyBaseModel

# Validation patterns
OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")

# Channel values from conversations_v2.0.md (GET list and GET single)
CHANNEL_VALUES = frozenset(
    {
        "facebook",
        "alexa",
        "slack",
        "generic",
        "inject",
        "rest",
        "realtime",
        "socket",
        "adminconsole",
        "webchat2",
        "dialogflow",
        "twilio",
        "twilio-sms",
        "line",
        "intercom",
        "microsoftBotFramework",
        "microsoftTeams",
        "sunshineConversations",
        "admin-webchat",
        "avaya",
        "nonConversational",
        "voiceGateway2",
        "amazonLex",
        "workplace",
        "webhook",
        "abstractRest",
        "userlike",
        "ringCentralEngage",
        "audioCodes",
        "bandwidth",
        "whatsapp",
        "eightByEight",
        "genesysBotConnector",
        "niceCXOne",
        "agentAssistVoice",
        "webchat3",
        "niceCXOneAAH",
        "zoomContactCenter",
    }
)

# Message type enum (GET single item)
MESSAGE_TYPE_VALUES = frozenset({"input", "output"})

# Message source enum (GET single item)
MESSAGE_SOURCE_VALUES = frozenset({"user", "bot", "agent", "suggestion"})


def _validate_object_id(value: Optional[str], field_name: str) -> Optional[str]:
    """
    Validate that a string matches MongoDB ObjectId format (24 lowercase hex).

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


def _validate_channel(value: Optional[str], field_name: str) -> Optional[str]:
    """
    Validate channel against the allowed enum from the API.

    Args:
        value: The channel string to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated value if valid, None if value was None.

    Raises:
        ValueError: If the value is not in the allowed channel set.
    """
    if value is not None and value not in CHANNEL_VALUES:
        raise ValueError(
            f"Invalid {field_name}: must be one of the documented channel values, got '{value}'"
        )
    return value


class Conversation(CognigyBaseModel):
    """
    Conversation summary model for LIST /v2.0/conversations.

    Represents a single conversation in the list response. Used when parsing
    GET /v2.0/conversations so that the response is returned as a list of
    Conversation instances (not a wrapper with items).

    Attributes:
        id: MongoDB ObjectId of the conversation (alias _id).
        contact_id: Contact identifier.
        channel: Channel name (e.g. webchat3); must match API enum.
        project_id: Project ObjectId (24 hex characters).
        project_name: Human-readable project name.
        flow_name: Name of the flow used in the conversation.
        messages: Number of messages in the conversation.
        start_time: Start time of the conversation.
        end_time: End time of the conversation.
        ratings: List of rating numbers.
        rating_comments: List of rating comment strings.
        endpoint_name: Name of the endpoint.
    """

    contact_id: Optional[str] = Field(
        None,
        alias="contactId",
        description="Contact identifier",
    )
    channel: Optional[str] = Field(
        None,
        description="Channel name (e.g. webchat3); must match API enum",
    )
    project_id: Optional[str] = Field(
        None,
        alias="projectId",
        description="Project ObjectId (24 hex characters)",
    )
    project_name: Optional[str] = Field(
        None,
        alias="projectName",
        description="Human-readable project name",
    )
    flow_name: Optional[str] = Field(
        None,
        alias="flowName",
        description="Name of the flow used in the conversation",
    )
    messages: Optional[int] = Field(
        None,
        description="Number of messages in the conversation",
    )
    start_time: Optional[str] = Field(
        None,
        alias="startTime",
        description="Start time of the conversation",
    )
    end_time: Optional[str] = Field(
        None,
        alias="endTime",
        description="End time of the conversation",
    )
    ratings: Optional[list[float]] = Field(
        None,
        description="List of rating numbers",
    )
    rating_comments: Optional[list[str]] = Field(
        None,
        alias="ratingComments",
        description="List of rating comment strings",
    )
    endpoint_name: Optional[str] = Field(
        None,
        alias="endpointName",
        description="Name of the endpoint",
    )

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate project_id matches ObjectId format (24 hex, min/max length 24)."""
        return _validate_object_id(v, "project_id")

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: Optional[str]) -> Optional[str]:
        """Validate channel is one of the documented enum values."""
        return _validate_channel(v, "channel")


class ConversationMessage(CognigyBaseModel):
    """
    Conversation detail (message) item for GET /v2.0/conversations/{sessionId}.

    Represents a single message/event in the conversation detail response.
    The GET response body has an "items" array and "total"; this model
    describes one element of "items". The resource returns a list of
    ConversationMessage instances (not a wrapper).

    Attributes:
        project_id: Project ObjectId (24 hex characters).
        project_name: Human-readable project name.
        input_id: Input identifier.
        session_id: Session identifier.
        contact_id: Contact identifier.
        organisation: Organisation ObjectId (24 hex characters).
        input_text: Text of the input.
        input_data: Arbitrary input data object.
        type: Message type; one of 'input', 'output'.
        source: Source of the message; one of 'user', 'bot', 'agent', 'suggestion'.
        flow_name: Name of the flow.
        flow_reference_id: Flow reference identifier.
        channel: Channel name; must match API enum.
        timestamp: Timestamp object.
        in_handover_request: Whether this is a handover request.
        in_handover_conversation: Whether in handover conversation.
        output_id: Output identifier.
        expires_at: Expiration timestamp object.
        endpoint_url_token: Endpoint URL token.
        endpoint_name: Name of the endpoint.
        locale_reference_id: Locale reference identifier.
        locale_name: Locale name.
        snapshot_id: Snapshot ObjectId (24 hex characters).
        snapshot_name: Snapshot name.
        rating: Rating number.
        rating_comment: Rating comment string.
    """

    project_id: Optional[str] = Field(
        None,
        alias="projectId",
        description="Project ObjectId (24 hex characters)",
    )
    project_name: Optional[str] = Field(
        None,
        alias="projectName",
        description="Human-readable project name",
    )
    input_id: Optional[str] = Field(
        None,
        alias="inputId",
        description="Input identifier",
    )
    session_id: Optional[str] = Field(
        None,
        alias="sessionId",
        description="Session identifier",
    )
    contact_id: Optional[str] = Field(
        None,
        alias="contactId",
        description="Contact identifier",
    )
    organisation: Optional[str] = Field(
        None,
        description="Organisation ObjectId (24 hex characters)",
    )
    input_text: Optional[str] = Field(
        None,
        alias="inputText",
        description="Text of the input",
    )
    input_data: Optional[dict[str, Any]] = Field(
        None,
        alias="inputData",
        description="Arbitrary input data object",
    )
    type: Optional[str] = Field(
        None,
        description="Message type: 'input' or 'output'",
    )
    source: Optional[str] = Field(
        None,
        description="Source: 'user', 'bot', 'agent', or 'suggestion'",
    )
    flow_name: Optional[str] = Field(
        None,
        alias="flowName",
        description="Name of the flow",
    )
    flow_reference_id: Optional[str] = Field(
        None,
        alias="flowReferenceId",
        description="Flow reference identifier",
    )
    channel: Optional[str] = Field(
        None,
        description="Channel name; must match API enum",
    )
    timestamp: Optional[dict[str, Any]] = Field(
        None,
        description="Timestamp object",
    )
    in_handover_request: Optional[bool] = Field(
        None,
        alias="inHandoverRequest",
        description="Whether this is a handover request",
    )
    in_handover_conversation: Optional[bool] = Field(
        None,
        alias="inHandoverConversation",
        description="Whether in handover conversation",
    )
    output_id: Optional[str] = Field(
        None,
        alias="outputId",
        description="Output identifier",
    )
    expires_at: Optional[dict[str, Any]] = Field(
        None,
        alias="expiresAt",
        description="Expiration timestamp object",
    )
    endpoint_url_token: Optional[str] = Field(
        None,
        alias="endpointUrlToken",
        description="End point URL token",
    )
    endpoint_name: Optional[str] = Field(
        None,
        alias="endpointName",
        description="Name of the endpoint",
    )
    locale_reference_id: Optional[str] = Field(
        None,
        alias="localeReferenceId",
        description="Locale reference identifier",
    )
    locale_name: Optional[str] = Field(
        None,
        alias="localeName",
        description="Locale name",
    )
    snapshot_id: Optional[str] = Field(
        None,
        alias="snapshotId",
        description="Snapshot ObjectId (24 hex characters)",
    )
    snapshot_name: Optional[str] = Field(
        None,
        alias="snapshotName",
        description="Snapshot name",
    )
    rating: Optional[float] = Field(
        None,
        description="Rating number",
    )
    rating_comment: Optional[str] = Field(
        None,
        alias="ratingComment",
        description="Rating comment string",
    )

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate project_id matches ObjectId format."""
        return _validate_object_id(v, "project_id")

    @field_validator("organisation")
    @classmethod
    def validate_organisation(cls, v: Optional[str]) -> Optional[str]:
        """Validate organisation matches ObjectId format."""
        return _validate_object_id(v, "organisation")

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: Optional[str]) -> Optional[str]:
        """Validate channel is one of the documented enum values."""
        return _validate_channel(v, "channel")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate type is 'input' or 'output'."""
        if v is not None and v not in MESSAGE_TYPE_VALUES:
            raise ValueError(f"Invalid type: must be 'input' or 'output', got '{v}'")
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        """Validate source is 'user', 'bot', 'agent', or 'suggestion'."""
        if v is not None and v not in MESSAGE_SOURCE_VALUES:
            raise ValueError(
                f"Invalid source: must be one of user, bot, agent, suggestion, got '{v}'"
            )
        return v

    @field_validator("snapshot_id")
    @classmethod
    def validate_snapshot_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate snapshot_id matches ObjectId format."""
        return _validate_object_id(v, "snapshot_id")
