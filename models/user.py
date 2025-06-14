import uuid
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime
from config.db import Base

def generate_guid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    guid = Column(String(36), primary_key=True, default=generate_guid, unique=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("worker", "citizen", name="user_roles"), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    latitude = Column(String(255))
    longitude = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
