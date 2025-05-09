from pydantic import BaseModel
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str

class NotificationOut(BaseModel):
    id: int
    user_id: str
    title: str
    message: str
    timestamp: datetime

    class Config:
        orm_mode = True
