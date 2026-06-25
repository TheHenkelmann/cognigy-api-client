"""Tests for Pydantic model serialization and validation."""

from __future__ import annotations

import pytest

from cognigy.models.base import to_camel
from cognigy.models.project import Project, ProjectCreate, ProjectUpdate
from conftest import PROJECT_ID


class TestToCamel:
    def test_converts_snake_case(self):
        assert to_camel("created_at") == "createdAt"
        assert to_camel("primary_locale_reference") == "primaryLocaleReference"


class TestCognigyBaseModel:
    def test_maps_id_alias_from_api_response(self):
        project = Project.model_validate({"_id": PROJECT_ID, "name": "Test"})
        assert project.id == PROJECT_ID

    def test_serializes_id_as_underscore_id(self):
        project = Project(id=PROJECT_ID, name="Test")
        dumped = project.model_dump(by_alias=True)
        assert dumped["_id"] == PROJECT_ID
        assert "id" not in dumped

    def test_ignores_unknown_fields(self):
        project = Project.model_validate(
            {"_id": PROJECT_ID, "name": "Test", "unknownField": "ignored"}
        )
        assert project.name == "Test"


class TestProjectModels:
    def test_project_create_serializes_camel_case(self):
        create = ProjectCreate(name="New", color="blue")
        dumped = create.model_dump(by_alias=True, exclude_none=True)
        assert dumped == {"name": "New", "color": "blue"}

    def test_project_update_partial_fields(self):
        update = ProjectUpdate(name="Renamed")
        dumped = update.model_dump(by_alias=True, exclude_none=True)
        assert dumped == {"name": "Renamed"}

    def test_project_rejects_invalid_color(self):
        with pytest.raises(ValueError, match="Invalid color"):
            Project.model_validate({"_id": PROJECT_ID, "name": "Test", "color": "not-a-color"})
