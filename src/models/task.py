"""
Task models for the Cognigy API.

This module contains Pydantic models for Task resources including
response models and status enumerations.

Tasks represent asynchronous operations in the Cognigy system such as
imports, exports, training operations, and other long-running processes.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional

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


class TaskStatus(str, Enum):
    """
    Enumeration of possible task statuses.

    Represents the lifecycle states of a task in the Cognigy system.

    Attributes:
        QUEUED: Task is waiting in the queue to be processed.
        ACTIVE: Task is currently being executed.
        DONE: Task has completed successfully.
        CANCELLING: Task cancellation has been requested and is in progress.
        CANCELLED: Task has been cancelled.
        ERROR: Task has failed with an error.
    """

    QUEUED = "queued"
    ACTIVE = "active"
    DONE = "done"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    ERROR = "error"


class Task(CognigyBaseModel):
    """
    Response model for Task resources.

    Represents a Cognigy Task - an asynchronous operation that runs
    in the background such as imports, exports, training, etc.
    Used for both GET single task and GET list responses.

    Attributes:
        id: MongoDB ObjectId of the task (24 hex characters).
        name: Name/type of the task describing the operation being performed.
        data: Parameters and configuration data for the task.
        status: Current status of the task (queued, active, done, cancelling,
                cancelled, error).
        current_step: Current progress step number (for multi-step tasks).
        total_step: Total number of steps in the task.
        fail_reason: Error message if the task failed.
        last_run_at: ISO 8601 datetime when the task last started running.
        last_finished_at: ISO 8601 datetime when the task last finished.
        created_at: Unix timestamp when the task was created (0 to 2147483647).
        last_changed: Unix timestamp when the task was last modified (0 to 2147483647).
        created_by: ObjectId of user who created the task (24 hex characters).
        last_changed_by: ObjectId of user who last modified the task (24 hex characters).

    Example:
        >>> task = Task(
        ...     id="507f1f77bcf86cd799439011",
        ...     name="import-flow",
        ...     status=TaskStatus.ACTIVE,
        ...     current_step=2,
        ...     total_step=5
        ... )
        >>> print(f"Task {task.name}: {task.status.value} ({task.current_step}/{task.total_step})")
        Task import-flow: active (2/5)
    """

    name: Optional[str] = Field(
        None, description="Name/type of the task describing the operation being performed"
    )
    data: Optional[dict[str, Any]] = Field(
        None, description="Parameters and configuration data for the task"
    )
    status: Optional[TaskStatus] = Field(None, description="Current status of the task")
    current_step: Optional[int] = Field(
        None, alias="currentStep", description="Current progress step number (for multi-step tasks)"
    )
    total_step: Optional[int] = Field(
        None, alias="totalStep", description="Total number of steps in the task"
    )
    fail_reason: Optional[str] = Field(
        None, alias="failReason", description="Error message if the task failed"
    )
    last_run_at: Optional[datetime] = Field(
        None, alias="lastRunAt", description="ISO 8601 datetime when the task last started running"
    )
    last_finished_at: Optional[datetime] = Field(
        None, alias="lastFinishedAt", description="ISO 8601 datetime when the task last finished"
    )
    created_at: Optional[int] = Field(
        None, alias="createdAt", description="Unix timestamp when the task was created"
    )
    last_changed: Optional[int] = Field(
        None, alias="lastChanged", description="Unix timestamp when the task was last modified"
    )
    created_by: Optional[str] = Field(
        None, alias="createdBy", description="ObjectId of user who created the task"
    )
    last_changed_by: Optional[str] = Field(
        None, alias="lastChangedBy", description="ObjectId of user who last modified the task"
    )

    @field_validator("current_step", "total_step")
    @classmethod
    def validate_step_positive(cls, v: Optional[int], info) -> Optional[int]:
        """Validate step values are non-negative integers."""
        if v is not None and v < 0:
            raise ValueError(f"{info.field_name} must be a non-negative integer, got {v}")
        return v

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: Optional[int]) -> Optional[int]:
        """Validate created_at is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "created_at")

    @field_validator("last_changed")
    @classmethod
    def validate_last_changed(cls, v: Optional[int]) -> Optional[int]:
        """Validate last_changed is a valid Unix timestamp."""
        return _validate_unix_timestamp(v, "last_changed")

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate created_by matches ObjectId format."""
        return _validate_object_id(v, "created_by")

    @field_validator("last_changed_by")
    @classmethod
    def validate_last_changed_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate last_changed_by matches ObjectId format."""
        return _validate_object_id(v, "last_changed_by")

    @property
    def progress_percent(self) -> Optional[float]:
        """
        Calculate the task progress as a percentage.

        Returns:
            Progress percentage (0.0 to 100.0) if both current_step and
            total_step are set and total_step > 0, otherwise None.

        Example:
            >>> task.current_step = 3
            >>> task.total_step = 10
            >>> task.progress_percent
            30.0
        """
        if self.current_step is not None and self.total_step and self.total_step > 0:
            return (self.current_step / self.total_step) * 100.0
        return None

    @property
    def is_complete(self) -> bool:
        """
        Check if the task has completed (successfully or with failure).

        Returns:
            True if the task status is 'done', 'cancelled', or 'error'.

        Example:
            >>> task.status = TaskStatus.DONE
            >>> task.is_complete
            True
        """
        return self.status in (TaskStatus.DONE, TaskStatus.CANCELLED, TaskStatus.ERROR)

    @property
    def is_running(self) -> bool:
        """
        Check if the task is currently running.

        Returns:
            True if the task status is 'active' or 'cancelling'.

        Example:
            >>> task.status = TaskStatus.ACTIVE
            >>> task.is_running
            True
        """
        return self.status in (TaskStatus.ACTIVE, TaskStatus.CANCELLING)
