import random
import string
from sqlalchemy import Column, String, Integer, Enum, Boolean
from config.db import Base

def generate_guid():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Container(Base):
    __tablename__ = "containers"

    guid = Column(String(6), primary_key=True, default=generate_guid, unique=True, index=True)
    name = Column(String(255), nullable=False)
    latitude = Column(String(255), nullable=False)
    longitude = Column(String(255), nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(Enum("active", "inactive", name="status_enum"), default="active")
    isFavorite = Column(Boolean, default=False)
    limit = Column(Integer, nullable=False, default=100)
