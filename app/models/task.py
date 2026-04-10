from enum import Enum

from pydantic import AwareDatetime, BaseModel, Field


class Priority(Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNSET = "UNSET"


class TaskQueryParams(BaseModel):
    completed: bool | None = Field(
        None, description="Filter tasks by completion status"
    )
    priority: Priority | None = Field(
        None, description="Filter tasks by priority level"
    )
    due_before: AwareDatetime | None = Field(
        None, description="Filter tasks due before this date"
    )
    due_after: AwareDatetime | None = Field(
        None, description="Filter tasks due after this date"
    )


class Task(BaseModel):
    # Required fields without defaults
    id: int = Field(..., description="The ID of the task")
    title: str = Field(..., description="The name of the task")
    created_at: AwareDatetime = Field(..., description="When the task was created")
    updated_at: AwareDatetime = Field(..., description="When the task was last updated")

    # Required fields with defaults
    completed: bool = Field(False, description="The task's completion status")
    priority: Priority = Field(
        Priority.UNSET,
        description=(
            "The priority of the task. Lower number = higher priority. "
            "0 means unset."
        ),
    )

    # Optional fields with defaults
    description: str | None = Field(None, description="The task description")
    due_date: AwareDatetime | None = Field(None, description="The task's due date")
    completed_at: AwareDatetime | None = Field(
        None, description="When the task was completed"
    )


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: Priority = Priority.UNSET
    due_date: AwareDatetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    due_date: AwareDatetime | None = None
    completed: bool | None = None
