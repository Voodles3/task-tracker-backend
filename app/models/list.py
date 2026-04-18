from pydantic import AwareDatetime, BaseModel, Field


class TaskList(BaseModel):
    id: int = Field(..., description="The ID of the list")
    name: str = Field(..., description="The name of the list")
    created_at: AwareDatetime = Field(..., description="When the list was created")
    updated_at: AwareDatetime = Field(..., description="When the list was last updated")


class TaskListCreate(BaseModel):
    name: str


class TaskListUpdate(BaseModel):
    name: str | None = None
