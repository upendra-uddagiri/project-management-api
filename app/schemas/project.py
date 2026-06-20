from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.project import ProjectStatus
from app.models.user import UserRole

class ProjectBase(BaseModel):
    name: str
    description:Optional[str]=None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectRead(ProjectBase):
    id: str
    owner_id: str
    status:ProjectStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberRead(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)