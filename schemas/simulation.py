from pydantic import BaseModel
from typing import List
from datetime import datetime

class SimulationCreate(BaseModel):
    container_guids: List[str]

class SimulationResponse(BaseModel):
    id: int
    created_at: datetime
    distance_km: float
    duration_min: float
    route: List[str]

    class Config:
        orm_mode = True
