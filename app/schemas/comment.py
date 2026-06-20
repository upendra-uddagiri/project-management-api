from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CommentCreate(BaseModel):
    content: str


class CommentRead(BaseModel):
    id: str
    content: str
    task_id: str
    author_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)