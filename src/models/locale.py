"""
Locale models for the Cognigy API.

This module contains Pydantic models for Locale resources including
response models, create/update request models, and the NLU language enum.
"""

import re
from enum import Enum
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


class NluLanguage(str, Enum):
    """
    Supported NLU (Natural Language Understanding) languages.
    
    These language codes follow the format: language-region (e.g., 'en-US').
    Each value represents a supported language for intent recognition
    and natural language processing in Cognigy.
    
    Attributes:
        GE_GE: Georgian (Georgia)
        DA_DK: Danish (Denmark)
        EN_AU: English (Australia)
        EN_CA: English (Canada)
        EN_IN: English (India)
        EN_GB: English (United Kingdom)
        EN_US: English (United States)
        DE_DE: German (Germany)
        JA_JP: Japanese (Japan)
        KO_KR: Korean (Korea)
        ES_ES: Spanish (Spain)
        NL_NL: Dutch (Netherlands)
        AR_AE: Arabic (United Arab Emirates)
        FI_FI: Finnish (Finland)
        FR_FR: French (France)
        IT_IT: Italian (Italy)
        NN_NO: Norwegian Nynorsk (Norway)
        PL_PL: Polish (Poland)
        SV_SE: Swedish (Sweden)
        TH_TH: Thai (Thailand)
        ZH_CN: Chinese Simplified (China)
        VI_VN: Vietnamese (Vietnam)
        PT_BR: Portuguese (Brazil)
        RU_RU: Russian (Russia)
        PT_PT: Portuguese (Portugal)
        TR_TR: Turkish (Turkey)
        HI_IN: Hindi (India)
        BN_IN: Bengali (India)
        TA_IN: Tamil (India)
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


class Locale(CognigyBaseModel):
    """
    Response model for Locale resources.
    
    Represents a Cognigy Locale which defines a language configuration
    for a project. Locales are used to support multi-language virtual agents.
    Used for both GET single locale and GET list responses.
    
    Attributes:
        id: MongoDB ObjectId of the locale (24 hex characters).
        name: Human-readable name of the locale (e.g., "English").
        primary: Whether this is the primary/default locale for the project.
        nlu_language: The NLU language code for intent recognition.
        fallback_locale_reference: ObjectId of the fallback locale to use
            when content is not available in this locale.
        created_at: Unix timestamp when the locale was created (0 to 2147483647).
        created_by: ObjectId of the user who created the locale.
        last_changed: Unix timestamp when the locale was last modified (0 to 2147483647).
        last_changed_by: ObjectId of the user who last modified the locale.
    """
    name: Optional[str] = Field(
        None,
        description="Human-readable name of the locale (e.g., 'English')"
    )
    primary: Optional[bool] = Field(
        None,
        description="Whether this is the primary/default locale for the project"
    )
    nlu_language: Optional[NluLanguage] = Field(
        None,
        alias="nluLanguage",
        description="The NLU language code for intent recognition"
    )
    fallback_locale_reference: Optional[str] = Field(
        None,
        alias="fallbackLocaleReference",
        description="ObjectId of the fallback locale"
    )
    created_at: Optional[int] = Field(
        None,
        alias="createdAt",
        description="Unix timestamp when the locale was created"
    )
    created_by: Optional[str] = Field(
        None,
        alias="createdBy",
        description="ObjectId of the user who created the locale"
    )
    last_changed: Optional[int] = Field(
        None,
        alias="lastChanged",
        description="Unix timestamp when the locale was last modified"
    )
    last_changed_by: Optional[str] = Field(
        None,
        alias="lastChangedBy",
        description="ObjectId of the user who last modified the locale"
    )

    @field_validator("fallback_locale_reference")
    @classmethod
    def validate_fallback_locale_reference(cls, v: Optional[str]) -> Optional[str]:
        """Validate fallback_locale_reference matches ObjectId format."""
        return _validate_object_id(v, "fallback_locale_reference")

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


class LocaleCreate(CognigyBaseModel):
    """
    Input model for creating a Locale.
    
    Contains the required and optional fields for creating a new locale
    via the POST /v2.0/locales endpoint.
    
    Attributes:
        name: Human-readable name of the locale (e.g., "English").
        project_id: ObjectId of the project to create the locale in (required).
        primary: Whether this should be the primary/default locale.
        nlu_language: The NLU language code for intent recognition.
        fallback_locale_reference: ObjectId of the fallback locale to use
            when content is not available in this locale.
    
    Example:
        >>> from cognigy.models import LocaleCreate, NluLanguage
        >>> locale_data = LocaleCreate(
        ...     name="German",
        ...     project_id="507f1f77bcf86cd799439011",
        ...     nlu_language=NluLanguage.DE_DE,
        ...     primary=False
        ... )
    """
    name: Optional[str] = Field(
        None,
        description="Human-readable name of the locale (e.g., 'English')"
    )
    project_id: str = Field(
        ...,
        alias="projectId",
        description="ObjectId of the project to create the locale in"
    )
    primary: Optional[bool] = Field(
        None,
        description="Whether this should be the primary/default locale"
    )
    nlu_language: Optional[NluLanguage] = Field(
        None,
        alias="nluLanguage",
        description="The NLU language code for intent recognition"
    )
    fallback_locale_reference: Optional[str] = Field(
        None,
        alias="fallbackLocaleReference",
        description="ObjectId of the fallback locale"
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

    @field_validator("fallback_locale_reference")
    @classmethod
    def validate_fallback_locale_reference(cls, v: Optional[str]) -> Optional[str]:
        """Validate fallback_locale_reference matches ObjectId format."""
        return _validate_object_id(v, "fallback_locale_reference")


class LocaleUpdate(CognigyBaseModel):
    """
    Input model for updating a Locale.
    
    Contains the optional fields for updating an existing locale
    via the PATCH /v2.0/locales/{localeId} endpoint. Only provided
    fields will be updated.
    
    Attributes:
        name: New human-readable name for the locale.
        primary: Whether this should be the primary/default locale.
        nlu_language: New NLU language code for intent recognition.
        fallback_locale_reference: ObjectId of the new fallback locale.
    
    Example:
        >>> from cognigy.models import LocaleUpdate, NluLanguage
        >>> update_data = LocaleUpdate(
        ...     name="Updated Locale Name",
        ...     nlu_language=NluLanguage.EN_GB
        ... )
    """
    name: Optional[str] = Field(
        None,
        description="New human-readable name for the locale"
    )
    primary: Optional[bool] = Field(
        None,
        description="Whether this should be the primary/default locale"
    )
    nlu_language: Optional[NluLanguage] = Field(
        None,
        alias="nluLanguage",
        description="New NLU language code for intent recognition"
    )
    fallback_locale_reference: Optional[str] = Field(
        None,
        alias="fallbackLocaleReference",
        description="ObjectId of the new fallback locale"
    )

    @field_validator("fallback_locale_reference")
    @classmethod
    def validate_fallback_locale_reference(cls, v: Optional[str]) -> Optional[str]:
        """Validate fallback_locale_reference matches ObjectId format."""
        return _validate_object_id(v, "fallback_locale_reference")
