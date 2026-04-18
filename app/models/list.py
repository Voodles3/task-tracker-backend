from pydantic import AwareDatetime, BaseModel, Field, field_validator


class TaskList(BaseModel):
    id: int = Field(..., description="The ID of the list")
    name: str = Field(..., min_length=1, description="The name of the list")
    created_at: AwareDatetime = Field(..., description="When the list was created")
    updated_at: AwareDatetime = Field(..., description="When the list was last updated")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_list_name(value)


class TaskListCreate(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_list_name(value)


class TaskListUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return None if value is None else normalize_list_name(value)


def normalize_list_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("List name cannot be blank")
    return value
