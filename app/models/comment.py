import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(TEXT, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(String, nullable=False)
    task_id = Column(TEXT, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(TEXT, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    task = relationship("Task")
    author = relationship("User")