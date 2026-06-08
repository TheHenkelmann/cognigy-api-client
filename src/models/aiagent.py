"""
AI Agent models for the Cognigy API.

This module contains Pydantic models for AI Agent resources including
response models, create/update request models, and related nested models.
"""

import re
from typing import Optional, List, Dict, Any, Literal
from pydantic import Field, field_validator, model_validator
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
            f"Invalid UUID format for {field_name}: "
            f"must be a valid UUID, got '{value}'"
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


# Type definitions for enums
TTSVendor = Literal[
    "aws", "deepgram", "elevenlabs", "google", 
    "microsoft", "nuance", "default", "custom", "none"
]

ContactProfilesOption = Literal[
    "none", "selectedProfileFields", "completeProfile", "profileMemoriesOnly"
]


class SpeakingStyle(CognigyBaseModel):
    """
    Speaking style configuration for an AI Agent.
    
    Defines how the AI Agent should communicate in terms of
    completeness and formality.
    
    Attributes:
        completeness: How complete the responses should be
            (e.g., 'concise', 'detailed').
        formality: The formality level of responses
            (e.g., 'formal', 'informal').
    """
    id: Optional[str] = Field(None, alias="_id", exclude=True)
    completeness: Optional[str] = Field(
        None,
        description="How complete the responses should be (e.g., 'concise', 'detailed')"
    )
    formality: Optional[str] = Field(
        None,
        description="The formality level of responses (e.g., 'formal', 'informal')"
    )


class VoiceConfigs(CognigyBaseModel):
    """
    Voice configuration for text-to-speech functionality.
    
    Configures the TTS settings for voice-enabled AI Agents.
    
    Attributes:
        tts_voice: The voice identifier to use for TTS.
        tts_language: The language code for TTS (e.g., 'en', 'de', 'zh').
        tts_vendor: The TTS vendor to use. One of: aws, deepgram, 
            elevenlabs, google, microsoft, nuance, default, custom, none.
        tts_model: The specific TTS model to use (vendor-specific).
        tts_label: A label for the TTS configuration.
        tts_disable_cache: Whether to disable TTS caching.
    """
    id: Optional[str] = Field(None, alias="_id", exclude=True)
    tts_voice: Optional[str] = Field(
        None,
        alias="ttsVoice",
        description="The voice identifier to use for TTS"
    )
    tts_language: Optional[str] = Field(
        None,
        alias="ttsLanguage",
        description="The language code for TTS (e.g., 'en', 'de', 'zh')"
    )
    tts_vendor: Optional[TTSVendor] = Field(
        None,
        alias="ttsVendor",
        description="The TTS vendor: aws, deepgram, elevenlabs, google, microsoft, nuance, default, custom, none"
    )
    tts_model: Optional[str] = Field(
        None,
        alias="ttsModel",
        description="The specific TTS model to use (vendor-specific)"
    )
    tts_label: Optional[str] = Field(
        None,
        alias="ttsLabel",
        description="A label for the TTS configuration"
    )
    tts_disable_cache: Optional[bool] = Field(
        None,
        alias="ttsDisableCache",
        description="Whether to disable TTS caching"
    )


class SafetySettings(CognigyBaseModel):
    """
    Safety settings for AI Agent responses.
    
    Configures various safety guardrails to control
    the AI Agent's output behavior.
    
    Attributes:
        avoid_harmful_content: Whether to filter harmful content from responses.
        avoid_ungrounded_content: Whether to avoid responses not grounded in knowledge.
        avoid_copyright_infringements: Whether to avoid potential copyright issues.
        prevent_jailbreak_and_manipulation: Whether to prevent jailbreak attempts.
    """
    id: Optional[str] = Field(None, alias="_id", exclude=True)
    avoid_harmful_content: Optional[bool] = Field(
        None,
        alias="avoidHarmfulContent",
        description="Whether to filter harmful content from responses"
    )
    avoid_ungrounded_content: Optional[bool] = Field(
        None,
        alias="avoidUngroundedContent",
        description="Whether to avoid responses not grounded in knowledge"
    )
    avoid_copyright_infringements: Optional[bool] = Field(
        None,
        alias="avoidCopyrightInfringements",
        description="Whether to avoid potential copyright issues"
    )
    prevent_jailbreak_and_manipulation: Optional[bool] = Field(
        None,
        alias="preventJailbreakAndManipulation",
        description="Whether to prevent jailbreak attempts"
    )


class AIAgentTool(CognigyBaseModel):
    """
    Tool configuration within an AI Agent Job.
    
    Represents a tool that can be used by a job in an AI Agent.
    
    Attributes:
        id: MongoDB ObjectId of the tool (24 hex characters).
        reference_id: Reference identifier for the tool.
        type: Type of the tool node.
        label: Human-readable label for the tool.
        comment: Optional comment describing the tool.
        comment_color: Color for the comment display.
        analytics_label: Label used for analytics tracking.
        is_disabled: Whether the tool is currently disabled.
        is_entry_point: Whether this tool is an entry point.
        extension: Extension identifier if tool is from an extension.
        config: Tool-specific configuration object.
    """
    reference_id: Optional[str] = Field(
        None,
        alias="referenceId",
        description="Reference identifier for the tool"
    )
    type: Optional[str] = Field(
        None,
        description="Type of the tool node"
    )
    label: Optional[str] = Field(
        None,
        description="Human-readable label for the tool"
    )
    comment: Optional[str] = Field(
        None,
        description="Optional comment describing the tool"
    )
    comment_color: Optional[str] = Field(
        None,
        alias="commentColor",
        description="Color for the comment display"
    )
    analytics_label: Optional[str] = Field(
        None,
        alias="analyticsLabel",
        description="Label used for analytics tracking"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether the tool is currently disabled"
    )
    is_entry_point: Optional[bool] = Field(
        None,
        alias="isEntryPoint",
        description="Whether this tool is an entry point"
    )
    extension: Optional[str] = Field(
        None,
        description="Extension identifier if tool is from an extension"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Tool-specific configuration object"
    )


class AIAgentJob(CognigyBaseModel):
    """
    Job configuration for an AI Agent.
    
    Represents a job that defines specific tasks or capabilities
    of an AI Agent, including its associated tools.
    
    Attributes:
        id: MongoDB ObjectId of the job (24 hex characters).
        reference_id: Reference identifier for the job.
        type: Type of the job (typically 'aiAgentJob').
        label: Human-readable label for the job.
        comment: Optional comment describing the job.
        comment_color: Color for the comment display.
        analytics_label: Label used for analytics tracking.
        is_disabled: Whether the job is currently disabled.
        is_entry_point: Whether this job is an entry point.
        extension: Extension identifier if job is from an extension.
        config: Job-specific configuration object.
        tools: List of tools available to this job.
    """
    reference_id: Optional[str] = Field(
        None,
        alias="referenceId",
        description="Reference identifier for the job"
    )
    type: Optional[str] = Field(
        None,
        description="Type of the job (typically 'aiAgentJob')"
    )
    label: Optional[str] = Field(
        None,
        description="Human-readable label for the job"
    )
    comment: Optional[str] = Field(
        None,
        description="Optional comment describing the job"
    )
    comment_color: Optional[str] = Field(
        None,
        alias="commentColor",
        description="Color for the comment display"
    )
    analytics_label: Optional[str] = Field(
        None,
        alias="analyticsLabel",
        description="Label used for analytics tracking"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether the job is currently disabled"
    )
    is_entry_point: Optional[bool] = Field(
        None,
        alias="isEntryPoint",
        description="Whether this job is an entry point"
    )
    extension: Optional[str] = Field(
        None,
        description="Extension identifier if job is from an extension"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Job-specific configuration object"
    )
    tools: Optional[List[AIAgentTool]] = Field(
        None,
        description="List of tools available to this job"
    )


class AIAgent(CognigyBaseModel):
    """
    Response model for AI Agent resources.
    
    Represents a Cognigy AI Agent with all its configuration.
    Used for both GET single AI agent and GET list responses.
    
    Attributes:
        id: MongoDB ObjectId of the AI Agent (24 hex characters).
        name: Name of the AI Agent.
        image: URL to the avatar image of the AI Agent.
        image_optimized_format: Whether the optimized image format is used.
        knowledge_reference_id: UUID of the Knowledge Store to use, or None.
        description: Short description of the AI Agent (max 1000 characters).
        speaking_style: Configuration for response completeness and formality.
        voice_configs: Text-to-speech configuration.
        enable_voice_configs: Whether voice configuration is enabled.
        safety_settings: Safety guardrail settings.
        contact_profiles_option: How contact profiles are used.
        contact_profiles_selected: Selected profile fields when option is 'selectedProfileFields'.
        instructions: Instructions for the AI Agent (max 1000 characters).
        created_at: Unix timestamp when the AI Agent was created.
        created_by: ObjectId of user who created the AI Agent.
        last_changed: Unix timestamp when the AI Agent was last modified.
        last_changed_by: ObjectId of user who last modified the AI Agent.
    """
    name: Optional[str] = Field(
        None,
        description="Name of the AI Agent"
    )
    image: Optional[str] = Field(
        None,
        description="URL to the avatar image of the AI Agent"
    )
    image_optimized_format: Optional[bool] = Field(
        None,
        alias="imageOptimizedFormat",
        description="Whether the optimized image format defined by Cognigy is used"
    )
    knowledge_reference_id: Optional[str] = Field(
        None,
        alias="knowledgeReferenceId",
        description="UUID of the Knowledge Store to use as base knowledge, or null"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Short description of the AI Agent (max 1000 characters)"
    )
    speaking_style: Optional[SpeakingStyle] = Field(
        None,
        alias="speakingStyle",
        description="Configuration for response completeness and formality"
    )
    voice_configs: Optional[VoiceConfigs] = Field(
        None,
        alias="voiceConfigs",
        description="Text-to-speech configuration"
    )
    enable_voice_configs: Optional[bool] = Field(
        None,
        alias="enableVoiceConfigs",
        description="Whether voice configuration is enabled"
    )
    safety_settings: Optional[SafetySettings] = Field(
        None,
        alias="safetySettings",
        description="Safety guardrail settings"
    )
    contact_profiles_option: Optional[ContactProfilesOption] = Field(
        None,
        alias="contactProfilesOption",
        description="How contact profiles are used: none, selectedProfileFields, completeProfile, profileMemoriesOnly"
    )
    contact_profiles_selected: Optional[List[str]] = Field(
        None,
        alias="contactProfilesSelected",
        description="Selected profile fields when contactProfilesOption is 'selectedProfileFields'"
    )
    instructions: Optional[str] = Field(
        None,
        max_length=1000,
        description="Instructions for the AI Agent (max 1000 characters)"
    )
    created_at: Optional[int] = Field(
        None,
        alias="createdAt",
        description="Unix timestamp when the AI Agent was created"
    )
    created_by: Optional[str] = Field(
        None,
        alias="createdBy",
        description="ObjectId of user who created the AI Agent"
    )
    last_changed: Optional[int] = Field(
        None,
        alias="lastChanged",
        description="Unix timestamp when the AI Agent was last modified"
    )
    last_changed_by: Optional[str] = Field(
        None,
        alias="lastChangedBy",
        description="ObjectId of user who last modified the AI Agent"
    )

    @field_validator("knowledge_reference_id")
    @classmethod
    def validate_knowledge_reference_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate knowledge_reference_id matches UUID format."""
        return _validate_uuid(v, "knowledge_reference_id")

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate description does not exceed 1000 characters."""
        if v is not None and len(v) > 1000:
            raise ValueError(
                f"description must be at most 1000 characters, got {len(v)}"
            )
        return v

    @field_validator("instructions")
    @classmethod
    def validate_instructions_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate instructions does not exceed 1000 characters."""
        if v is not None and len(v) > 1000:
            raise ValueError(
                f"instructions must be at most 1000 characters, got {len(v)}"
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


class AIAgentCreate(CognigyBaseModel):
    """
    Input model for creating an AI Agent.
    
    Contains the required and optional fields for creating a new AI Agent
    via the POST /v2.0/aiagents endpoint.
    
    Attributes:
        name: Name of the AI Agent (required for identification).
        project_id: ObjectId of the project to create the AI Agent in (required).
        image: URL to the avatar image of the AI Agent.
        image_optimized_format: Whether to use Cognigy's optimized image format.
        knowledge_reference_id: UUID of a Knowledge Store to use, or None.
        description: Short description (max 1000 characters).
        speaking_style: Configuration for response completeness and formality.
        voice_configs: Text-to-speech configuration.
        enable_voice_configs: Whether to enable voice configuration.
        safety_settings: Safety guardrail settings.
        contact_profiles_option: How contact profiles should be used.
        contact_profiles_selected: Profile fields to select (when option is 'selectedProfileFields').
        instructions: Instructions for the AI Agent (max 1000 characters).
    """
    id: Optional[str] = Field(None, alias="_id", exclude=True)
    name: Optional[str] = Field(
        None,
        description="Name of the AI Agent"
    )
    project_id: str = Field(
        ...,
        alias="projectId",
        description="ObjectId of the project to create the AI Agent in"
    )
    image: Optional[str] = Field(
        None,
        description="URL to the avatar image of the AI Agent"
    )
    image_optimized_format: Optional[bool] = Field(
        None,
        alias="imageOptimizedFormat",
        description="Whether to use Cognigy's optimized image format"
    )
    knowledge_reference_id: Optional[str] = Field(
        None,
        alias="knowledgeReferenceId",
        description="UUID of a Knowledge Store to use as base knowledge, or null"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Short description of the AI Agent (max 1000 characters)"
    )
    speaking_style: Optional[SpeakingStyle] = Field(
        None,
        alias="speakingStyle",
        description="Configuration for response completeness and formality"
    )
    voice_configs: Optional[VoiceConfigs] = Field(
        None,
        alias="voiceConfigs",
        description="Text-to-speech configuration"
    )
    enable_voice_configs: Optional[bool] = Field(
        None,
        alias="enableVoiceConfigs",
        description="Whether to enable voice configuration"
    )
    safety_settings: Optional[SafetySettings] = Field(
        None,
        alias="safetySettings",
        description="Safety guardrail settings"
    )
    contact_profiles_option: Optional[ContactProfilesOption] = Field(
        None,
        alias="contactProfilesOption",
        description="How contact profiles should be used"
    )
    contact_profiles_selected: Optional[List[str]] = Field(
        None,
        alias="contactProfilesSelected",
        description="Profile fields to select when option is 'selectedProfileFields'"
    )
    instructions: Optional[str] = Field(
        None,
        max_length=1000,
        description="Instructions for the AI Agent (max 1000 characters)"
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

    @field_validator("knowledge_reference_id")
    @classmethod
    def validate_knowledge_reference_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate knowledge_reference_id matches UUID format."""
        return _validate_uuid(v, "knowledge_reference_id")

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate description does not exceed 1000 characters."""
        if v is not None and len(v) > 1000:
            raise ValueError(
                f"description must be at most 1000 characters, got {len(v)}"
            )
        return v

    @field_validator("instructions")
    @classmethod
    def validate_instructions_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate instructions does not exceed 1000 characters."""
        if v is not None and len(v) > 1000:
            raise ValueError(
                f"instructions must be at most 1000 characters, got {len(v)}"
            )
        return v

    @model_validator(mode="after")
    def validate_contact_profiles_selected(self):
        """
        Validate that contact_profiles_selected is only set when 
        contact_profiles_option is 'selectedProfileFields'.
        """
        if (
            self.contact_profiles_selected is not None
            and self.contact_profiles_option != "selectedProfileFields"
        ):
            raise ValueError(
                "contact_profiles_selected can only be set when "
                "contact_profiles_option is 'selectedProfileFields'"
            )
        return self


class AIAgentUpdate(CognigyBaseModel):
    """
    Input model for updating an AI Agent.
    
    Contains the optional fields for updating an existing AI Agent
    via the PATCH /v2.0/aiagents/{aiAgentId} endpoint.
    Only provided fields will be updated.
    
    Attributes:
        name: New name for the AI Agent.
        image: New avatar image URL.
        image_optimized_format: Whether to use Cognigy's optimized image format.
        knowledge_reference_id: UUID of a Knowledge Store to use, or None.
        description: New description (max 1000 characters).
        speaking_style: New speaking style configuration.
        voice_configs: New voice configuration.
        enable_voice_configs: Whether to enable voice configuration.
        safety_settings: New safety settings.
        contact_profiles_option: New contact profiles option.
        contact_profiles_selected: New selected profile fields.
        instructions: New instructions (max 1000 characters).
    """
    id: Optional[str] = Field(None, alias="_id", exclude=True)
    name: Optional[str] = Field(
        None,
        description="New name for the AI Agent"
    )
    image: Optional[str] = Field(
        None,
        description="New avatar image URL"
    )
    image_optimized_format: Optional[bool] = Field(
        None,
        alias="imageOptimizedFormat",
        description="Whether to use Cognigy's optimized image format"
    )
    knowledge_reference_id: Optional[str] = Field(
        None,
        alias="knowledgeReferenceId",
        description="UUID of a Knowledge Store to use, or null"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="New description (max 1000 characters)"
    )
    speaking_style: Optional[SpeakingStyle] = Field(
        None,
        alias="speakingStyle",
        description="New speaking style configuration"
    )
    voice_configs: Optional[VoiceConfigs] = Field(
        None,
        alias="voiceConfigs",
        description="New voice configuration"
    )
    enable_voice_configs: Optional[bool] = Field(
        None,
        alias="enableVoiceConfigs",
        description="Whether to enable voice configuration"
    )
    safety_settings: Optional[SafetySettings] = Field(
        None,
        alias="safetySettings",
        description="New safety settings"
    )
    contact_profiles_option: Optional[ContactProfilesOption] = Field(
        None,
        alias="contactProfilesOption",
        description="New contact profiles option"
    )
    contact_profiles_selected: Optional[List[str]] = Field(
        None,
        alias="contactProfilesSelected",
        description="New selected profile fields"
    )
    instructions: Optional[str] = Field(
        None,
        max_length=1000,
        description="New instructions (max 1000 characters)"
    )

    @field_validator("knowledge_reference_id")
    @classmethod
    def validate_knowledge_reference_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate knowledge_reference_id matches UUID format."""
        return _validate_uuid(v, "knowledge_reference_id")

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate description does not exceed 1000 characters."""
        if v is not None and len(v) > 1000:
            raise ValueError(
                f"description must be at most 1000 characters, got {len(v)}"
            )
        return v

    @field_validator("instructions")
    @classmethod
    def validate_instructions_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate instructions does not exceed 1000 characters."""
        if v is not None and len(v) > 1000:
            raise ValueError(
                f"instructions must be at most 1000 characters, got {len(v)}"
            )
        return v


class AIAgentValidateNameRequest(CognigyBaseModel):
    """
    Request model for validating an AI Agent name.
    
    Used to check if an AI Agent name already exists in a project
    via the POST /v2.0/aiagents/validatename endpoint.
    
    Attributes:
        name: The AI Agent name to validate.
        project_id: ObjectId of the project to check the name in.
    """
    id: Optional[str] = Field(None, alias="_id", exclude=True)
    name: str = Field(
        ...,
        description="The AI Agent name to validate"
    )
    project_id: str = Field(
        ...,
        alias="projectId",
        description="ObjectId of the project to check the name in"
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
