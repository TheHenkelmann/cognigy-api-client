"""Tests for custom exception types."""

from __future__ import annotations

from cognigy.exceptions import (
    CognigyAPIError,
    CognigyConfigurationError,
    CognigyError,
    CognigyValidationError,
)


class TestCognigyExceptions:
    def test_api_error_includes_status_and_detail(self):
        err = CognigyAPIError(
            message="API request failed: Unauthorized",
            status_code=401,
            response_body={"detail": "Invalid API key"},
        )
        assert err.status_code == 401
        assert err.response_body == {"detail": "Invalid API key"}
        assert "401" in str(err)
        assert "Invalid API key" in str(err)

    def test_validation_error_formats_field_errors(self):
        err = CognigyValidationError(
            "Data does not match the expected model.",
            errors=[{"loc": ("name",), "msg": "Field required"}],
        )
        text = str(err)
        assert "name" in text
        assert "Field required" in text

    def test_validation_error_without_details(self):
        err = CognigyValidationError("Validation failed.")
        assert str(err) == "Validation failed."

    def test_exception_hierarchy(self):
        assert issubclass(CognigyConfigurationError, CognigyError)
        assert issubclass(CognigyAPIError, CognigyError)
        assert issubclass(CognigyValidationError, CognigyError)
