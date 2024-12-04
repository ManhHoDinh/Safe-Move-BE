from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.api.models import Camera, FollowRequest, FollowCamera
from app.api import db_manager
from app.api.db_manager import DBManager
from sqlalchemy.orm import Session
from app.api.db import get_db
from databases import Database
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, TemplateId, Substitution
from sqlalchemy import select

cameras = APIRouter()


@cameras.get("/", response_model=List[Camera])
async def get_all_cameras(db: Session = Depends(get_db)):
    db_manager = DBManager(db)
    return await db_manager.fetch_cameras()


@cameras.get("/cameras", response_model=List[Camera])
async def list_cameras(
    is_enabled: Optional[bool] = None,
    search: Optional[str] = None,
    db=Depends(get_db)
) -> List[Camera]:
    return await db_manager.get_camera_list(db, is_enabled, search)


@cameras.get("/follow/camera/{user_id}")
async def get_follow_camera(userId: str, db=Depends(get_db)):
    camera = await db_manager.get_follow_camera(db, userId)
    if not camera:
        raise HTTPException(status_code=404, detail="Follow camera not found")
    return camera


@cameras.get("/cameras/{camera_id}")
async def read_camera(camera_id: str, db=Depends(get_db)):
    camera = await db_manager.get_camera_by_id(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@cameras.put("/cameras/status")
async def modify_multiple_camera_status(
    camera_id_list: List[str],
    is_enabled: bool,
    db: Database = Depends(get_db)
):
    try:
        updated_cameras = await db_manager.update_camera_statuses(db, camera_id_list, is_enabled)

        if updated_cameras:
            return {"updated": len(updated_cameras), "status": "success"}
        else:
            raise HTTPException(
                status_code=404, detail="No cameras found or updated")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@cameras.post("/cameras/follow")
async def follow_camera(
    requestInfo: FollowRequest,
    db: Database = Depends(get_db)
):
    try:
        new_follow = await db_manager.follow_camera_service(db, requestInfo)
        return new_follow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cameras.delete("/cameras/follow")
async def unfollow_camera(cameraId: str, userId: str, db=Depends(get_db)):
    deleted = await db_manager.unfollow_camera_service(db, cameraId, userId)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Follow camera not found")
    return {"message": "Follow camera deleted successfully"}


@cameras.post("/cameras/send-email/{_id}")
async def send_email(_id: str, db=Depends(get_db)):
    await db_manager.send_email(_id, db)
