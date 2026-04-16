from enum import Enum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field


class Priority(Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNSET = "UNSET"


class SortBy(Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    TITLE = "title"


type Order = Literal["asc", "desc"]


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

    q: str | None = Field(
        None,
        description="Filter tasks case-insensitively by title and description",
    )

    sort_by: SortBy = Field(
        SortBy.CREATED_AT, description="Sort tasks by a specified field"
    )
    order: Order = Field(
        "asc", description="Order sorted tasks ascending or descending"
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
            "The priority of the task. Lower number = higher priority. 0 means unset."
        ),
    )

    # Optional fields with defaults
    description: str | None = Field(None, description="The task description")
    due_date: AwareDatetime | None = Field(None, description="The task's due date")
    completed_at: AwareDatetime | None = Field(
        None, description="When the task was completed"
    )


class TasksResponse(BaseModel):
    count: int
    tasks: list[Task]


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
