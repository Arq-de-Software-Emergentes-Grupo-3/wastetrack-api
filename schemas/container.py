from pydantic import BaseModel
from typing import Optional, Literal

class ContainerCreate(BaseModel):
    name: str
    latitude: str
    longitude: str
    capacity: int
    limit: int

class ContainerUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[Literal["active", "inactive"]] = None
    isFavorite: Optional[bool] = None
    limit: Optional[int] = None

class ContainerResponse(BaseModel):
    guid: str
    name: str
    latitude: str
    longitude: str
    capacity: int
    status: str
    isFavorite: bool
    limit: int

class FavoriteUpdate(BaseModel):
    isFavorite: bool

class CapacityUpdate(BaseModel):
    capacity: int

    @classmethod
    def validate(cls, values):
        if values.get("capacity") is not None and values["capacity"] < 0:
            raise ValueError("Capacity must be a non-negative integer")
        return values

    class Config:
        orm_mode = True

class LimitUpdate(BaseModel):
    limit: int

    @classmethod
    def validate(cls, values):
        if values.get("limit") is not None and values["limit"] < 0:
            raise ValueError("Limit must be a non-negative integer")
        return values

    class Config:
        orm_mode = True
