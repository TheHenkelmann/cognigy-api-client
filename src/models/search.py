"""
Search models for the Cognigy API.

This module provides Pydantic models for search results returned by
the Cognigy v2.0 global search endpoint.
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field, field_validator

from .base import CognigyBaseModel


class SearchResultType(str, Enum):
    """
    Types of resources that can appear in search results.

    Attributes:
        ENDPOINT: An endpoint resource.
        EXTENSION: An extension resource.
        FLOW: A flow resource.
        FUNCTION: A function resource.
        LEXICON: A lexicon resource.
        GOAL: A goal resource.
        HANDOVER_PROVIDER: A handover provider resource.
        NLU_CONNECTOR: An NLU connector resource.
        PLAYBOOK: A playbook resource.
        PROJECT: A project resource.
        SNAPSHOT: A snapshot resource.
    """

    ENDPOINT = "endpoint"
    EXTENSION = "extension"
    FLOW = "flow"
    FUNCTION = "function"
    LEXICON = "lexicon"
    GOAL = "goal"
    HANDOVER_PROVIDER = "handoverProvider"
    NLU_CONNECTOR = "nluconnector"
    PLAYBOOK = "playbook"
    PROJECT = "project"
    SNAPSHOT = "snapshot"


class NLUConnectorSubType(str, Enum):
    """
    Subtypes for NLU connector resources.

    Attributes:
        ALEXA: Amazon Alexa NLU.
        DIALOGFLOW: Google Dialogflow NLU.
        DIALOGFLOW_BUILT_IN: Dialogflow built-in NLU.
        AMAZON_LEX_BUILT_IN: Amazon Lex built-in NLU.
        LUIS: Microsoft LUIS NLU.
        WATSON: IBM Watson NLU.
        NO_NLU: No NLU processing.
        COGNIGY: Cognigy native NLU.
        CODE: Code-based NLU.
        GENERATIVE_AI: Generative AI-based NLU.
        LEX: Amazon Lex NLU.
    """

    ALEXA = "alexa"
    DIALOGFLOW = "dialogflow"
    DIALOGFLOW_BUILT_IN = "dialogflowBuiltIn"
    AMAZON_LEX_BUILT_IN = "amazonLexBuiltIn"
    LUIS = "luis"
    WATSON = "watson"
    NO_NLU = "noNlu"
    COGNIGY = "cognigy"
    CODE = "code"
    GENERATIVE_AI = "generativeAI"
    LEX = "lex"


class EndpointSubType(str, Enum):
    """
    Subtypes for endpoint resources.

    Attributes:
        FACEBOOK: Facebook Messenger endpoint.
        ALEXA: Amazon Alexa endpoint.
        SLACK: Slack endpoint.
        GENERIC: Generic endpoint.
        INJECT: Inject endpoint.
        REST: REST API endpoint.
        REALTIME: Realtime endpoint.
        SOCKET: Socket endpoint.
        ADMIN_CONSOLE: Admin console endpoint.
        WEBCHAT2: Webchat v2 endpoint.
        DIALOGFLOW: Dialogflow endpoint.
        TWILIO: Twilio voice endpoint.
        TWILIO_SMS: Twilio SMS endpoint.
        LINE: LINE messaging endpoint.
        INTERCOM: Intercom endpoint.
        MICROSOFT_BOT_FRAMEWORK: Microsoft Bot Framework endpoint.
        MICROSOFT_TEAMS: Microsoft Teams endpoint.
        SUNSHINE_CONVERSATIONS: Zendesk Sunshine Conversations endpoint.
        ADMIN_WEBCHAT: Admin webchat endpoint.
        AVAYA: Avaya endpoint.
        NON_CONVERSATIONAL: Non-conversational endpoint.
        VOICE_GATEWAY2: Voice Gateway v2 endpoint.
        AMAZON_LEX: Amazon Lex endpoint.
        WORKPLACE: Facebook Workplace endpoint.
        WEBHOOK: Webhook endpoint.
        ABSTRACT_REST: Abstract REST endpoint.
        USERLIKE: Userlike endpoint.
        RING_CENTRAL_ENGAGE: RingCentral Engage endpoint.
        AUDIO_CODES: AudioCodes endpoint.
        BANDWIDTH: Bandwidth endpoint.
        WHATSAPP: WhatsApp endpoint.
        EIGHT_BY_EIGHT: 8x8 endpoint.
        GENESYS_BOT_CONNECTOR: Genesys Bot Connector endpoint.
        NICE_CXONE: NICE CXone endpoint.
        AGENT_ASSIST_VOICE: Agent Assist Voice endpoint.
        WEBCHAT3: Webchat v3 endpoint.
        NICE_CXONE_AAH: NICE CXone AAH endpoint.
        ZOOM_CONTACT_CENTER: Zoom Contact Center endpoint.
    """

    FACEBOOK = "facebook"
    ALEXA = "alexa"
    SLACK = "slack"
    GENERIC = "generic"
    INJECT = "inject"
    REST = "rest"
    REALTIME = "realtime"
    SOCKET = "socket"
    ADMIN_CONSOLE = "adminconsole"
    WEBCHAT2 = "webchat2"
    DIALOGFLOW = "dialogflow"
    TWILIO = "twilio"
    TWILIO_SMS = "twilio-sms"
    LINE = "line"
    INTERCOM = "intercom"
    MICROSOFT_BOT_FRAMEWORK = "microsoftBotFramework"
    MICROSOFT_TEAMS = "microsoftTeams"
    SUNSHINE_CONVERSATIONS = "sunshineConversations"
    ADMIN_WEBCHAT = "admin-webchat"
    AVAYA = "avaya"
    NON_CONVERSATIONAL = "nonConversational"
    VOICE_GATEWAY2 = "voiceGateway2"
    AMAZON_LEX = "amazonLex"
    WORKPLACE = "workplace"
    WEBHOOK = "webhook"
    ABSTRACT_REST = "abstractRest"
    USERLIKE = "userlike"
    RING_CENTRAL_ENGAGE = "ringCentralEngage"
    AUDIO_CODES = "audioCodes"
    BANDWIDTH = "bandwidth"
    WHATSAPP = "whatsapp"
    EIGHT_BY_EIGHT = "eightByEight"
    GENESYS_BOT_CONNECTOR = "genesysBotConnector"
    NICE_CXONE = "niceCXOne"
    AGENT_ASSIST_VOICE = "agentAssistVoice"
    WEBCHAT3 = "webchat3"
    NICE_CXONE_AAH = "niceCXOneAAH"
    ZOOM_CONTACT_CENTER = "zoomContactCenter"


class GenerativeAIProviderSubType(str, Enum):
    """
    Subtypes for Generative AI provider resources.

    Attributes:
        OPENAI: OpenAI provider.
        OPENAI_COMPATIBLE: OpenAI-compatible provider.
        AZURE_OPENAI: Azure OpenAI provider.
        ANTHROPIC: Anthropic provider.
        GOOGLE_VERTEX_AI: Google Vertex AI provider.
        GOOGLE_GEMINI: Google Gemini provider.
        ALEPH_ALPHA: Aleph Alpha provider.
        AWS_BEDROCK: AWS Bedrock provider.
        MISTRAL: Mistral provider.
    """

    OPENAI = "openAI"
    OPENAI_COMPATIBLE = "openAICompatible"
    AZURE_OPENAI = "azureOpenAI"
    ANTHROPIC = "anthropic"
    GOOGLE_VERTEX_AI = "googleVertexAI"
    GOOGLE_GEMINI = "googleGemini"
    ALEPH_ALPHA = "alephAlpha"
    AWS_BEDROCK = "awsBedrock"
    MISTRAL = "mistral"


class SearchResult(CognigyBaseModel):
    """
    A single search result item from the global search endpoint.

    Represents a resource found by the global search, which can be
    any of the supported resource types (endpoint, flow, project, etc.).

    Attributes:
        id: The unique ObjectId of the resource (24 hex characters).
        name: The display name of the resource.
        type: The type of resource (e.g., 'flow', 'endpoint', 'project').
        sub_type: Optional subtype providing more specific categorization.
            The possible values depend on the resource type.
        project_id: The ObjectId of the project containing this resource.
            May be None for project-level resources.
        last_changed: Unix timestamp of the last modification time.

    Example:
        >>> result = SearchResult(
        ...     _id="507f1f77bcf86cd799439011",
        ...     name="My Flow",
        ...     type="flow",
        ...     projectId="507f1f77bcf86cd799439012",
        ...     lastChanged=1694518620
        ... )
        >>> print(result.name)
        'My Flow'
    """

    name: str = Field(..., description="The name of the resource")
    type: SearchResultType = Field(..., description="The type of the resource")
    sub_type: str | None = Field(
        None, alias="subType", description="The subtype of the resource, varies by resource type"
    )
    project_id: str | None = Field(
        None, alias="projectId", description="The project ObjectId containing this resource"
    )
    last_changed: int | None = Field(
        None,
        alias="lastChanged",
        description="Unix timestamp of last modification",
        ge=0,
        le=2147483647,
    )

    @field_validator("id", "project_id", mode="before")
    @classmethod
    def validate_object_id(cls, v: str | None) -> str | None:
        """
        Validate that ObjectId fields contain exactly 24 lowercase hex characters.

        Args:
            v: The value to validate.

        Returns:
            The validated value or None if input was None.

        Raises:
            ValueError: If the value is not a valid 24-character hex string.
        """
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("ObjectId must be a string")
        if len(v) != 24:
            raise ValueError("ObjectId must be exactly 24 characters")
        if not all(c in "0123456789abcdef" for c in v.lower()):
            raise ValueError("ObjectId must contain only hexadecimal characters")
        return v

    @field_validator("last_changed", mode="before")
    @classmethod
    def validate_timestamp(cls, v: int | None) -> int | None:
        """
        Validate that the Unix timestamp is within valid range.

        Args:
            v: The timestamp value to validate.

        Returns:
            The validated timestamp or None if input was None.

        Raises:
            ValueError: If the timestamp is negative or exceeds max 32-bit value.
        """
        if v is None:
            return v
        if not isinstance(v, int):
            raise ValueError("Timestamp must be an integer")
        if v < 0:
            raise ValueError("Timestamp cannot be negative")
        if v > 2147483647:
            raise ValueError("Timestamp exceeds maximum value")
        return v
