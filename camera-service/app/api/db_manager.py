from sqlalchemy import delete
from app.api.models import CameraIn
from app.api.db import cameras, database
import logging

logger = logging.getLogger(__name__)


async def get_all_cameras():
    query = cameras.select()
    a = await database.fetch_all(query=query)
    for i in a:
        logger.debug(i)

    return a


async def get_camera(id: str):
    query = cameras.select().where(cameras.c.id == id)
    return await database.fetch_one(query=query)


async def create_camera(payload: CameraIn):
    query = cameras.insert().values(**payload.dict())
    camera_id = await database.execute(query)
    return {**payload.dict(), "id": camera_id}


async def update_camera(id: int, payload: CameraIn):
    camera = await get_camera(id=id)
    if not camera:
        return None

    update_data = payload.dict(exclude_unset=True)
    camera_in_db = CameraIn(**camera)

    updated_camera = camera_in_db.copy(update=update_data)

    query = (
        cameras
        .update()
        .where(cameras.c.id == id)
        .values(**updated_camera.dict())
    )

    return await database.execute(query=query)


async def delete_camera(id: int):
    query = delete(cameras).where(cameras.c.id == id)
    await database.execute(query)
    return "Camera deleted successfully"
