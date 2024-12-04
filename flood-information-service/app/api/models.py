from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field



class EStatus(str, Enum):
    APPROVED = "Approved"
    PENDING = "Pending"
    DECLINED = "Declined"


class FloodInformation(BaseModel):
    id: str = Field(default=None, alias="_id")
    userName: str
    latitude: float
    longitude: float
    locationName: str
    date: datetime = datetime.utcnow()
    status: EStatus
    floodLevel: int
    message: str
    modelDetectFloodLevel: int
    userId: str
    url: str


class FloodInformationCreate(BaseModel):
    userName: str
    latitude: float
    longitude: float
    locationName: str
    message: str
    date: datetime = Field(default_factory=datetime.utcnow)
    floodLevel: int
    userId: str
