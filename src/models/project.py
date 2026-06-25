"""
Pydantic models for Cognigy Project resources.

This module defines the data models for creating, reading, and updating
Cognigy Projects via the v2.0 API. Models include validation for colors,
locales, and ObjectId fields according to the API specification.
"""

from enum import Enum
from typing import Optional, Union

from pydantic import Field, field_validator

from .base import CognigyBaseModel


class CssColor(str, Enum):
    """
    Standard CSS color names supported by Cognigy.

    These are the web-standard color names that can be used
    for project color customization.
    """

    ALICE_BLUE = "aliceBlue"
    ANTIQUE_WHITE = "antiqueWhite"
    AQUA = "aqua"
    AQUAMARINE = "aquamarine"
    AZURE = "azure"
    BEIGE = "beige"
    BISQUE = "bisque"
    BLACK = "black"
    BLANCHED_ALMOND = "blanchedAlmond"
    BLUE = "blue"
    BLUE_VIOLET = "blueViolet"
    BROWN = "brown"
    BURLY_WOOD = "burlyWood"
    CADET_BLUE = "cadetBlue"
    CHARTREUSE = "chartreuse"
    CHOCOLATE = "chocolate"
    CORAL = "coral"
    CORNFLOWER_BLUE = "cornflowerBlue"
    CORNSILK = "cornsilk"
    CRIMSON = "crimson"
    CYAN = "cyan"
    DARK_BLUE = "darkBlue"
    DARK_CYAN = "darkCyan"
    DARK_GOLDEN_ROD = "darkGoldenRod"
    DARK_GRAY = "darkGray"
    DARK_GREY = "darkGrey"
    DARK_GREEN = "darkGreen"
    DARK_KHAKI = "darkKhaki"
    DARK_MAGENTA = "darkMagenta"
    DARK_OLIVE_GREEN = "darkOliveGreen"
    DARK_ORANGE = "darkOrange"
    DARK_ORCHID = "darkOrchid"
    DARK_RED = "darkRed"
    DARK_SALMON = "darkSalmon"
    DARK_SEA_GREEN = "darkSeaGreen"
    DARK_SLATE_BLUE = "darkSlateBlue"
    DARK_SLATE_GRAY = "darkSlateGray"
    DARK_SLATE_GREY = "darkSlateGrey"
    DARK_TURQUOISE = "darkTurquoise"
    DARK_VIOLET = "darkViolet"
    DEEP_PINK = "deepPink"
    DEEP_SKY_BLUE = "deepSkyBlue"
    DIM_GRAY = "dimGray"
    DIM_GREY = "dimGrey"
    DODGER_BLUE = "dodgerBlue"
    FIRE_BRICK = "fireBrick"
    FLORAL_WHITE = "floralWhite"
    FOREST_GREEN = "forestGreen"
    FUCHSIA = "fuchsia"
    GAINSBORO = "gainsboro"
    GHOST_WHITE = "ghostWhite"
    GOLD = "gold"
    GOLDEN_ROD = "goldenRod"
    GRAY = "gray"
    GREY = "grey"
    GREEN = "green"
    GREEN_YELLOW = "greenYellow"
    HONEY_DEW = "honeyDew"
    HOT_PINK = "hotPink"
    INDIAN_RED = "indianRed"
    INDIGO = "indigo"
    IVORY = "ivory"
    KHAKI = "khaki"
    LAVENDER = "lavender"
    LAVENDER_BLUSH = "lavenderBlush"
    LAWN_GREEN = "lawnGreen"
    LEMON_CHIFFON = "lemonChiffon"
    LIGHT_BLUE = "lightBlue"
    LIGHT_CORAL = "lightCoral"
    LIGHT_CYAN = "lightCyan"
    LIGHT_GOLDEN_ROD_YELLOW = "lightGoldenRodYellow"
    LIGHT_GRAY = "lightGray"
    LIGHT_GREY = "lightGrey"
    LIGHT_GREEN = "lightGreen"
    LIGHT_PINK = "lightPink"
    LIGHT_SALMON = "lightSalmon"
    LIGHT_SEA_GREEN = "lightSeaGreen"
    LIGHT_SKY_BLUE = "lightSkyBlue"
    LIGHT_SLATE_GRAY = "lightSlateGray"
    LIGHT_SLATE_GREY = "lightSlateGrey"
    LIGHT_STEEL_BLUE = "lightSteelBlue"
    LIGHT_YELLOW = "lightYellow"
    LIME = "lime"
    LIME_GREEN = "limeGreen"
    LINEN = "linen"
    MAGENTA = "magenta"
    MAROON = "maroon"
    MEDIUM_AQUA_MARINE = "mediumAquaMarine"
    MEDIUM_BLUE = "mediumBlue"
    MEDIUM_ORCHID = "mediumOrchid"
    MEDIUM_PURPLE = "mediumPurple"
    MEDIUM_SEA_GREEN = "mediumSeaGreen"
    MEDIUM_SLATE_BLUE = "mediumSlateBlue"
    MEDIUM_SPRING_GREEN = "mediumSpringGreen"
    MEDIUM_TURQUOISE = "mediumTurquoise"
    MEDIUM_VIOLET_RED = "mediumVioletRed"
    MIDNIGHT_BLUE = "midnightBlue"
    MINT_CREAM = "mintCream"
    MISTY_ROSE = "mistyRose"
    MOCCASIN = "moccasin"
    NAVAJO_WHITE = "navajoWhite"
    NAVY = "navy"
    OLD_LACE = "oldLace"
    OLIVE = "olive"
    OLIVE_DRAB = "oliveDrab"
    ORANGE = "orange"
    ORANGE_RED = "orangeRed"
    ORCHID = "orchid"
    PALE_GOLDEN_ROD = "paleGoldenRod"
    PALE_GREEN = "paleGreen"
    PALE_TURQUOISE = "paleTurquoise"
    PALE_VIOLET_RED = "paleVioletRed"
    PAPAYA_WHIP = "papayaWhip"
    PEACH_PUFF = "peachPuff"
    PERU = "peru"
    PINK = "pink"
    PLUM = "plum"
    POWDER_BLUE = "powderBlue"
    PURPLE = "purple"
    REBECCA_PURPLE = "rebeccaPurple"
    RED = "red"
    ROSY_BROWN = "rosyBrown"
    ROYAL_BLUE = "royalBlue"
    SADDLE_BROWN = "saddleBrown"
    SALMON = "salmon"
    SANDY_BROWN = "sandyBrown"
    SEA_GREEN = "seaGreen"
    SEA_SHELL = "seaShell"
    SIENNA = "sienna"
    SILVER = "silver"
    SKY_BLUE = "skyBlue"
    SLATE_BLUE = "slateBlue"
    SLATE_GRAY = "slateGray"
    SLATE_GREY = "slateGrey"
    SNOW = "snow"
    SPRING_GREEN = "springGreen"
    STEEL_BLUE = "steelBlue"
    TAN = "tan"
    TEAL = "teal"
    THISTLE = "thistle"
    TOMATO = "tomato"
    TURQUOISE = "turquoise"
    VIOLET = "violet"
    WHEAT = "wheat"
    WHITE = "white"
    WHITE_SMOKE = "whiteSmoke"
    YELLOW = "yellow"
    YELLOW_GREEN = "yellowGreen"
    NONE = "none"
    TRANSPARENT = "transparent"


class CognigyColor(str, Enum):
    """
    Cognigy-specific color palette.

    These are custom colors provided by Cognigy for project
    color customization in addition to standard CSS colors.
    """

    AMBER = "amber"
    BLUE_GREY = "blueGrey"
    COGNIGY_BLUE = "cognigyBlue"
    COGNIGY_GREY = "cognigyGrey"
    DEEP_ORANGE = "deepOrange"
    DEEP_PURPLE = "deepPurple"
    LIGHT_BLUE = "lightBlue"
    LIGHT_GREEN = "lightGreen"


# Union type for all valid project colors
ProjectColor = Union[CssColor, CognigyColor]

# All valid color values as a set for validation
VALID_COLORS = {c.value for c in CssColor} | {c.value for c in CognigyColor}


class ProjectLocale(str, Enum):
    """
    Supported locales for Cognigy projects.

    These locale codes determine the primary language and regional
    settings for a project's NLU (Natural Language Understanding)
    and content.
    """

    GE_GE = "ge-GE"
    DA_DK = "da-DK"
    EN_AU = "en-AU"
    EN_CA = "en-CA"
    EN_IN = "en-IN"
    EN_GB = "en-GB"
    EN_US = "en-US"
    DE_DE = "de-DE"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"
    ES_ES = "es-ES"
    NL_NL = "nl-NL"
    AR_AE = "ar-AE"
    FI_FI = "fi-FI"
    FR_FR = "fr-FR"
    IT_IT = "it-IT"
    NN_NO = "nn-NO"
    PL_PL = "pl-PL"
    SV_SE = "sv-SE"
    TH_TH = "th-TH"
    ZH_CN = "zh-CN"
    VI_VN = "vi-VN"
    PT_BR = "pt-BR"
    RU_RU = "ru-RU"
    PT_PT = "pt-PT"
    TR_TR = "tr-TR"
    HI_IN = "hi-IN"
    BN_IN = "bn-IN"
    TA_IN = "ta-IN"


class WhisperAssistConfiguration(str, Enum):
    """
    Whisper Assist configuration options for handover.

    Controls how the Whisper Assist feature behaves during
    live agent handover sessions.

    Attributes:
        NONE: Whisper Assist is disabled.
        BASIC: Basic Whisper Assist functionality enabled.
        TEMPLATE: Template-based Whisper Assist enabled.
    """

    NONE = "none"
    BASIC = "basic"
    TEMPLATE = "template"


class HandoverConfiguration(CognigyBaseModel):
    """
    Configuration for live agent handover functionality.

    This model defines settings for how the project handles
    handover to live agents, including inbox setup and
    Whisper Assist configuration.

    Attributes:
        setup_live_agent_inbox: Whether to automatically set up
            a Live Agent inbox for this project.
        whisper_assist_configuration: The Whisper Assist mode
            to use during handover sessions.
    """

    setup_live_agent_inbox: Optional[bool] = Field(
        default=None,
        alias="setupLiveAgentInbox",
        description="Whether to set up a Live Agent inbox for the project.",
    )
    whisper_assist_configuration: Optional[WhisperAssistConfiguration] = Field(
        default=None,
        alias="whisperAssistConfiguration",
        description="Whisper Assist configuration mode: 'none', 'basic', or 'template'.",
    )


def _validate_object_id(value: Optional[str], field_name: str) -> Optional[str]:
    """
    Validate that a string is a valid MongoDB ObjectId format.

    Args:
        value: The string value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated string value.

    Raises:
        ValueError: If the value is not a valid 24-character hex string.
    """
    if value is None:
        return value
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    if len(value) != 24:
        raise ValueError(f"{field_name} must be exactly 24 characters, got {len(value)}")
    if not all(c in "0123456789abcdef" for c in value.lower()):
        raise ValueError(f"{field_name} must contain only hexadecimal characters")
    return value


def _validate_timestamp(value: Optional[int], field_name: str) -> Optional[int]:
    """
    Validate that a timestamp is within the valid Unix timestamp range.

    Args:
        value: The timestamp value to validate.
        field_name: Name of the field for error messages.

    Returns:
        The validated timestamp value.

    Raises:
        ValueError: If the value is outside the valid range (0-2147483647).
    """
    if value is None:
        return value
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    if value < 0 or value > 2147483647:
        raise ValueError(f"{field_name} must be between 0 and 2147483647, got {value}")
    return value


class Project(CognigyBaseModel):
    """
    Response model for Cognigy Project resources.

    This model represents a Project as returned by the Cognigy API.
    It includes all fields that may be present in GET and POST responses.

    Projects are the top-level organizational unit in Cognigy and contain
    flows, intents, lexicons, and other resources.

    Attributes:
        id: Unique identifier for the project (24-character hex ObjectId).
        name: The display name of the project.
        color: The color used to identify the project in the UI.
            Can be a CSS color name or a Cognigy-specific color.
        handover_configuration: Settings for live agent handover functionality.
        live_agent_default_inbox: The default Live Agent inbox ID for the project.
        primary_locale_reference: ObjectId reference to the project's primary locale.
        created_at: Unix timestamp when the project was created.
        created_by: ObjectId of the user who created the project.
        last_changed: Unix timestamp when the project was last modified.
        last_changed_by: ObjectId of the user who last modified the project.

    Example:
        >>> project = Project(
        ...     id="507f1f77bcf86cd799439011",
        ...     name="My Project",
        ...     color="blue"
        ... )
        >>> print(project.name)
        'My Project'
    """

    name: str = Field(..., description="The display name of the project.")
    color: Optional[str] = Field(
        default=None, description="The color used to identify the project in the UI."
    )
    handover_configuration: Optional[HandoverConfiguration] = Field(
        default=None,
        alias="handoverConfiguration",
        description="Configuration for live agent handover functionality.",
    )
    live_agent_default_inbox: Optional[int] = Field(
        default=None,
        alias="liveAgentDefaultInbox",
        description="The default Live Agent inbox ID for the project.",
    )
    primary_locale_reference: Optional[str] = Field(
        default=None,
        alias="primaryLocaleReference",
        description="ObjectId reference to the project's primary locale.",
    )
    created_at: Optional[int] = Field(
        default=None, alias="createdAt", description="Unix timestamp when the project was created."
    )
    created_by: Optional[str] = Field(
        default=None, alias="createdBy", description="ObjectId of the user who created the project."
    )
    last_changed: Optional[int] = Field(
        default=None,
        alias="lastChanged",
        description="Unix timestamp when the project was last modified.",
    )
    last_changed_by: Optional[str] = Field(
        default=None,
        alias="lastChangedBy",
        description="ObjectId of the user who last modified the project.",
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate that color is a valid CSS or Cognigy color."""
        if v is not None and v not in VALID_COLORS:
            raise ValueError(f"Invalid color '{v}'. Must be a valid CSS color or Cognigy color.")
        return v

    @field_validator("primary_locale_reference")
    @classmethod
    def validate_primary_locale_reference(cls, v: Optional[str]) -> Optional[str]:
        """Validate primary_locale_reference is a valid ObjectId."""
        return _validate_object_id(v, "primary_locale_reference")

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate created_by is a valid ObjectId."""
        return _validate_object_id(v, "created_by")

    @field_validator("last_changed_by")
    @classmethod
    def validate_last_changed_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate last_changed_by is a valid ObjectId."""
        return _validate_object_id(v, "last_changed_by")

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: Optional[int]) -> Optional[int]:
        """Validate created_at is a valid Unix timestamp."""
        return _validate_timestamp(v, "created_at")

    @field_validator("last_changed")
    @classmethod
    def validate_last_changed(cls, v: Optional[int]) -> Optional[int]:
        """Validate last_changed is a valid Unix timestamp."""
        return _validate_timestamp(v, "last_changed")


class ProjectCreate(CognigyBaseModel):
    """
    Input model for creating a new Cognigy Project.

    This model defines the fields that can be provided when creating
    a new project via the POST /v2.0/projects endpoint.

    Attributes:
        name: The display name for the new project. Required.
        color: The color to use for the project in the UI.
            Can be a CSS color name or a Cognigy-specific color.
        locale: The primary locale for the project, determining
            the default language for NLU and content.
        handover_configuration: Optional settings for live agent
            handover functionality.

    Example:
        >>> create_data = ProjectCreate(
        ...     name="Customer Support Bot",
        ...     color="cognigyBlue",
        ...     locale=ProjectLocale.EN_US
        ... )
        >>> project = client.projects.create(create_data)
    """

    name: str = Field(..., description="The display name for the new project.")
    color: Optional[str] = Field(
        default=None, description="The color to use for the project in the UI."
    )
    locale: Optional[ProjectLocale] = Field(
        default=None, description="The primary locale for the project (e.g., 'en-US', 'de-DE')."
    )
    handover_configuration: Optional[HandoverConfiguration] = Field(
        default=None,
        alias="handoverConfiguration",
        description="Configuration for live agent handover functionality.",
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate that color is a valid CSS or Cognigy color."""
        if v is not None and v not in VALID_COLORS:
            raise ValueError(f"Invalid color '{v}'. Must be a valid CSS color or Cognigy color.")
        return v


class ProjectUpdate(CognigyBaseModel):
    """
    Input model for updating an existing Cognigy Project.

    This model defines the fields that can be modified when updating
    a project via the PATCH /v2.0/projects/{projectId} endpoint.
    All fields are optional; only provided fields will be updated.

    Attributes:
        name: New display name for the project.
        color: New color for the project in the UI.
            Can be a CSS color name or a Cognigy-specific color.
        handover_configuration: Updated settings for live agent
            handover functionality.

    Example:
        >>> update_data = ProjectUpdate(
        ...     name="Updated Project Name",
        ...     color="deepPurple"
        ... )
        >>> project = client.projects.update(project_id, update_data)
    """

    name: Optional[str] = Field(default=None, description="New display name for the project.")
    color: Optional[str] = Field(default=None, description="New color for the project in the UI.")
    handover_configuration: Optional[HandoverConfiguration] = Field(
        default=None,
        alias="handoverConfiguration",
        description="Updated configuration for live agent handover functionality.",
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate that color is a valid CSS or Cognigy color."""
        if v is not None and v not in VALID_COLORS:
            raise ValueError(f"Invalid color '{v}'. Must be a valid CSS color or Cognigy color.")
        return v
