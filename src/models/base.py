from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def to_camel(s: str) -> str:
    """Convert snake_case to camelCase (first letter lowercase)."""
    parts = s.split("_")
    return parts[0].lower() + "".join(p.title() for p in parts[1:])


class CognigyBaseModel(BaseModel):
    """
    Base model for all Cognigy resources.
    Handles the _id -> id mapping automatically.
    All snake_case fields get camelCase aliases when serializing for the API.
    """

    id: Optional[str] = Field(None, alias="_id")
    reference_id: Optional[str] = Field(None, alias="referenceId")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        alias_generator=to_camel,
    )


class CognigyCreateUpdateModel(BaseModel):
    """
    Base for create/update request models.
    All snake_case fields get camelCase aliases when serializing for the API.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
