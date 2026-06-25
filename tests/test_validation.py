"""Tests for validation helpers."""

from __future__ import annotations

import pytest

from cognigy.exceptions import CognigyValidationError
from cognigy.models.project import ProjectCreate, ProjectUpdate
from cognigy.validation import build_list_params, validate_create_update_data
from conftest import CURSOR


class TestValidateCreateUpdateData:
    def test_returns_model_instance_unchanged(self):
        data = ProjectCreate(name="Test")
        result = validate_create_update_data(data, ProjectCreate)
        assert result is data

    def test_validates_dict_input(self):
        result = validate_create_update_data({"name": "From Dict"}, ProjectCreate)
        assert isinstance(result, ProjectCreate)
        assert result.name == "From Dict"

    def test_converts_other_model_via_model_dump(self):
        source = ProjectUpdate(name="Updated")
        result = validate_create_update_data(source, ProjectCreate)
        assert isinstance(result, ProjectCreate)
        assert result.name == "Updated"

    def test_raises_on_invalid_data(self):
        with pytest.raises(CognigyValidationError) as exc_info:
            validate_create_update_data({"color": "blue"}, ProjectCreate)

        assert exc_info.value.errors


class TestBuildListParams:
    def test_builds_minimal_params(self):
        assert build_list_params() == {}

    def test_includes_filter_sort_and_limit(self):
        params = build_list_params(filter="bot", sort="-createdAt", limit=25)
        assert params == {
            "filter": "bot",
            "sort": "-createdAt",
            "limit": 25,
        }

    def test_includes_skip_when_nonzero(self):
        params = build_list_params(skip=10)
        assert params["skip"] == 10

    def test_omits_skip_when_zero(self):
        params = build_list_params(skip=0)
        assert "skip" not in params

    def test_includes_cursor_params(self):
        params = build_list_params(
            next_cursor=CURSOR,
            previous_cursor="b" * 24,
        )
        assert params["next"] == CURSOR
        assert params["previous"] == "b" * 24

    def test_merges_extra_params(self):
        params = build_list_params(extra={"projectId": "abc", "ignored": None})
        assert params == {"projectId": "abc"}

    @pytest.mark.parametrize(
        ("kwargs", "match"),
        [
            ({"filter": 123}, "filter must be a string"),
            ({"limit": 0}, "limit must be an integer"),
            ({"skip": -1}, "skip must be an integer"),
            ({"sort": 1}, "sort must be a string"),
            ({"next_cursor": "short"}, "next must be a 24-character string"),
            ({"previous_cursor": "x" * 10}, "previous must be a 24-character string"),
        ],
    )
    def test_rejects_invalid_params(self, kwargs, match):
        with pytest.raises(CognigyValidationError, match=match):
            build_list_params(**kwargs)
