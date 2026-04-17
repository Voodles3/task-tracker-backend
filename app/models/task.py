from enum import Enum
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field


class Priority(Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNSET = "UNSET"

    @property
    def sort_order(self) -> int:
        return {
            Priority.URGENT: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
            Priority.UNSET: 4,
        }[self]


class SortBy(Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    TITLE = "title"


class Order(Enum):
    ASC = "asc"
    DESC = "desc"


default_sort_order = {
    SortBy.CREATED_AT: Order.DESC,
    SortBy.UPDATED_AT: Order.DESC,
    SortBy.DUE_DATE: Order.ASC,
    SortBy.PRIORITY: Order.ASC,
    SortBy.TITLE: Order.ASC,
}


class TaskQueryParams(BaseModel):
    completed: Annotated[
        bool | None, Field(description="Filter tasks by completion status")
    ] = None
    priority: Annotated[
        Priority | None, Field(description="Filter tasks by priority level")
    ] = None
    due_before: Annotated[
        AwareDatetime | None, Field(description="Filter tasks due before this date")
    ] = None
    due_after: Annotated[
        AwareDatetime | None, Field(description="Filter tasks due after this date")
    ] = None

    q: Annotated[
        str | None,
        Field(
            description="Filter tasks case-insensitively by title and description",
        ),
    ] = None

    sort_by: Annotated[SortBy, Field(description="Sort tasks by a specified field")] = (
        SortBy.CREATED_AT
    )
    order: Annotated[
        Order | None,
        Field(
            description="""
            Order sorted tasks ascending or descending by the SortBy value.
            If None, uses default sort order""",
        ),
    ] = None


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
