from pydantic import BaseModel
from typing import Optional
from enum import Enum


class FloodLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    danger = "danger"


class CameraIn(BaseModel):
    name: str
    url: str
    createdAt: Optional[str]
    updatedAt: Optional[str]
    isActive: bool
    longitude: float
    latitude: float
    address: Optional[str]
    floodLevel: FloodLevel


class CameraOut(CameraIn):
    id: int


class CameraUpdate(CameraIn):
    name: Optional[str]
    url: Optional[str]
    isActive: Optional[bool]
    longitude: Optional[float]
    latitude: Optional[float]
    address: Optional[str]
    floodLevel: Optional[FloodLevel]
