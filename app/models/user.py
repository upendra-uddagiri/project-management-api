from sqlalchemy import Column,Integer,String,Boolean,DateTime,Enum
from sqlalchemy.dialects.sqlite import TEXT
from app.database import Base
from datetime import datetime
import uuid
import enum
class UserRole(enum.Enum):
  admin="admin"
  manager="manager"
  member="member"

class User(Base):
  __tablename__="user"

  id=Column(TEXT,primary_key=True,index=True,default=lambda:str(uuid.uuid4()))
  email=Column(String,unique=True,nullable=False,index=True)
  hashed_password=Column(String,nullable=False)
  full_name=Column(String,nullable=False)
  role=Column(Enum(UserRole),default=UserRole.member,nullable=False)
  is_active=Column(Boolean,default=True,nullable=False)
  created_at=Column(DateTime,nullable=False,default=datetime.utcnow)
  updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
