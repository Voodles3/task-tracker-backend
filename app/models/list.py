from enum import Enum
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field


class TaskList(BaseModel):
    id: int = Field(..., description="The ID of the list")
    name: str = Field(..., description="The name of the list")
    created_at: AwareDatetime = Field(..., description="When the list was created")
    updated_at: AwareDatetime = Field(..., description="When the list was last updated")


class ListCreate(BaseModel):
    name: str


class ListUpdate(BaseModel):
    name: str | None = None
