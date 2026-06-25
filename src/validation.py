"""
Validation helpers for create/update payloads.

Ensures data is validated against the correct Pydantic model before sending
to the API, so disallowed fields (e.g. _id) and wrong types are caught locally
with clear errors instead of API 400 responses.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from .exceptions import CognigyValidationError

T = TypeVar("T", bound=BaseModel)


def validate_create_update_data(data: Any, model_class: type[T]) -> T:
    """
    Validate and coerce data to the target Pydantic model for create/update requests.

    - If `data` is already an instance of `model_class`, it is returned unchanged.
    - Otherwise, data is converted (from dict or another model via model_dump) and
      validated with `model_class`. Only fields defined on the target model are
      kept; disallowed fields (e.g. _id from a GET response) are stripped and
      will not be sent to the API.

    Args:
        data: The payload—either a dict, a Pydantic model instance, or similar.
        model_class: The Pydantic model class to validate against (e.g. NodeUpdate,
                     LocaleCreate). Must only include fields allowed by the API.

    Returns:
        A validated instance of `model_class` ready to be passed to the client
        (e.g. for model_dump(by_alias=True, exclude_none=True) in _request).

    Raises:
        CognigyValidationError: If validation fails (wrong types, extra fields
                                when forbidden, missing required fields, etc.).
                                The exception message and .errors list give a
                                human-readable overview of all validation errors.
    """
    if isinstance(data, model_class):
        return data

    raw = data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

    try:
        return model_class.model_validate(raw)
    except ValidationError as e:
        errors = e.errors()
        raise CognigyValidationError(
            "Data does not match the expected model for this request.",
            errors=errors,
        ) from e


def build_list_params(
    *,
    filter: str | None = None,
    limit: int | None = None,
    skip: int | None = None,
    sort: str | None = None,
    next_cursor: str | None = None,
    previous_cursor: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build and validate a params dict for list-style endpoints.

    Enforces a consistent contract across all list endpoints:
    - filter: optional string
    - limit: optional int, must be >= 1.  When ``None`` the key is
      omitted from the returned dict (useful when the paginator sets
      its own limit).
    - skip: optional int, defaults to 0 when omitted, must be >= 0
    - sort: optional string (e.g. "name:asc" or "-createdAt")
    - next_cursor / previous_cursor: optional 24-character strings
    - any additional query parameters can be supplied via `extra`
    """
    params: dict[str, Any] = {}

    if filter is not None:
        if not isinstance(filter, str):
            raise CognigyValidationError("filter must be a string.")
        if filter:
            params["filter"] = filter

    if limit is not None:
        if not isinstance(limit, int) or limit < 1:
            raise CognigyValidationError("limit must be an integer greater than or equal to 1.")
        params["limit"] = limit

    if skip is None:
        skip = 0
    if not isinstance(skip, int) or skip < 0:
        raise CognigyValidationError("skip must be an integer greater than or equal to 0.")
    if skip:
        params["skip"] = skip

    if sort is not None:
        if not isinstance(sort, str):
            raise CognigyValidationError("sort must be a string.")
        if sort:
            params["sort"] = sort

    if next_cursor is not None:
        if not isinstance(next_cursor, str) or len(next_cursor) != 24:
            raise CognigyValidationError("next must be a 24-character string.")
        params["next"] = next_cursor

    if previous_cursor is not None:
        if not isinstance(previous_cursor, str) or len(previous_cursor) != 24:
            raise CognigyValidationError("previous must be a 24-character string.")
        params["previous"] = previous_cursor

    if extra:
        for key, value in extra.items():
            if value is not None:
                params[key] = value

    return params
