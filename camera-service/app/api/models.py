from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

CAMERA_API_URL = "https://api.notis.vn/v4/cameras/bybbox?lat1=11.160767&lng1=106.554166&lat2=9.45&lng2=128.99999"


class Location(BaseModel):
    type: str
    coordinates: List[float]


class Camera(BaseModel):
    camera_id: str = Field(..., alias="_id")
    id: str
    name: str
    loc: Location
    values: Dict[str, str]
    dist: str
    ptz: bool
    angle: Optional[int] = None
    liveviewUrl: str
    isEnabled: bool
    lastModified: datetime = datetime.utcnow()


class CameraStatusUpdate(BaseModel):
    status: str


class CameraUpdateRequest(BaseModel):
    camera_id: str
    is_enabled: bool


class FollowCamera(BaseModel):
    id: str
    cameraId: str
    userId: str
    userEmail: str


class FollowRequest(BaseModel):
    cameraId: str
    userId: str
    userEmail: str
