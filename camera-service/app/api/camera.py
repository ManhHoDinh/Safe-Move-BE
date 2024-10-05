from typing import List
from fastapi import APIRouter

from app.api.models import CameraIn, CameraOut, CameraUpdate
from app.api import db_manager

cameras = APIRouter()


@cameras.get('/', response_model=List[CameraOut])
async def get_cameras():
    return await db_manager.get_all_cameras()


@cameras.get('/{id}', response_model=CameraOut)
async def get_camera_detail(id: int):
    return await db_manager.get_camera(id)


@cameras.post('/', response_model=CameraOut, status_code=201)
async def create_camera(payload: CameraIn):
    return await db_manager.create_camera(payload)


@cameras.patch('/{id}', response_model=CameraOut)
async def update_camera(id: int, payload: CameraUpdate):
    return await db_manager.update_camera(id, payload)


@cameras.delete('/{id}', status_code=200)
async def delete_camera(id: int):
    return await db_manager.delete_camera(id)
