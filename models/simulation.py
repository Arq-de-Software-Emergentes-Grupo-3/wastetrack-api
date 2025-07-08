from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, UTC
from config.db import Base

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    total_distance_km = Column(Float, nullable=False)
    duration_min = Column(Float, nullable=False)
    route = Column(String(1000), nullable=False)
    distances = Column(String(5000), nullable=False)
