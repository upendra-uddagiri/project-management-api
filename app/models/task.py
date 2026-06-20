from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid
import enum


class TaskStatus(enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    in_review = "in_review"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    due_date = Column(DateTime, nullable=True)
    project_id = Column(TEXT, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(TEXT, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project")
    assignee = relationship("User")