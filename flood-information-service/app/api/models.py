from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class Location(BaseModel):
    type: str
    coordinates: List[float]


class EStatus(str, Enum):
    APPROVED = "Approved"
    PENDING = "Pending"
    DECLINED = "Declined"


class FloodInformation(BaseModel):
    id: str = Field(default=None, alias="_id")
    userName: str
    location: Location
    locationName: str
    date: datetime = datetime.utcnow()
    status: EStatus
    floodLevel: int
    userId: str
    url: str


class FloodInformationCreate(BaseModel):
    userName: str
    location: Location
    locationName: str
    date: datetime = Field(default_factory=datetime.utcnow)
    status: EStatus
    floodLevel: int
    userId: str
