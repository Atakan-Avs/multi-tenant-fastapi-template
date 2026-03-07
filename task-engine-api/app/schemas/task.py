from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: str = Field(default="medium")   # low/medium/high
    assigned_to_user_id: int | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: str | None = None                 # todo/doing/done
    priority: str | None = None               # low/medium/high
    assigned_to_user_id: int | None = None
    due_date: datetime | None = None


class TaskOut(BaseModel):
    id: int
    org_id: int
    title: str
    description: str | None
    status: str
    priority: str
    assigned_to_user_id: int | None
    due_date: datetime | None

    class Config:
        from_attributes = True