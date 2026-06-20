import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import UserRole


class ProjectStatus(enum.Enum):
    active = "active"
    archived = "archived"
    completed = "completed"


class Project(Base):
    __tablename__ = "projects"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active, nullable=False)
    owner_id = Column(TEXT, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relationships
    owner = relationship("User")
    members = relationship("ProjectMember", back_populates="project")


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(TEXT, ForeignKey("projects.id"), nullable=False)
    user_id = Column(TEXT, ForeignKey("user.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.member, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User")