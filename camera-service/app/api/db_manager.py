from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx
from app.api.db import cameras, get_db, follow_camera
from app.api.models import CAMERA_API_URL, Camera, FollowRequest
from databases import Database
from pydantic import ValidationError
from sqlalchemy import insert, or_, select, update, and_, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import uuid4

camera_status = {}


def truncate_string(value: str, max_length: int = 50) -> str:
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length]
    return value


class DBManager:
    def __init__(self, session: get_db):
        self.session = session

    async def fetch_cameras_from_api(self) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(CAMERA_API_URL)
            response.raise_for_status()
            data = response.json()
            print(f"Fetched camera data: {data}")
            return data

    async def fetch_cameras(self) -> List[Dict]:
        api_data = await self.fetch_cameras_from_api()

        for camera in api_data:
            stmt = select([cameras.c.id]).where(cameras.c.id == camera['id'])
            result = await self.session.fetch_one(stmt)

            if result is None:
                new_camera_data = {
                    '_id': camera['_id'],
                    'id': camera['id'],
                    'name': truncate_string(camera['name']),
                    'loc': camera['loc'],
                    'values': camera['values'],
                    'dist': truncate_string(camera['dist']),
                    'ptz': camera['ptz'],
                    'angle': camera.get('angle'),
                    'liveviewUrl': truncate_string(camera['liveviewUrl']),
                    'isEnabled': False,
                    'lastmodified':  datetime.utcnow()
                }
                stmt = insert(cameras).values(new_camera_data)
                try:
                    await self.session.execute(stmt)
                except IntegrityError:
                    pass
        stmt = select([cameras])
        result = await self.session.fetch_all(stmt)
        return result


async def get_camera_by_id(db: Database, camera_id: str) -> dict:
    query = select([cameras]).where(cameras.c._id == camera_id)
    result = await db.fetch_one(query)
    return result


async def update_camera_statuses(db: Database, camera_ids: List[str], is_enabled: bool) -> List[dict]:
    updated_cameras = []

    for camera_id in camera_ids:
        query = (
            update(cameras)
            .where(cameras.c.id == camera_id)
            .values(isEnabled=is_enabled, lastmodified=datetime.utcnow())
            .returning(cameras)  # Optional: returns the updated row
        )
        print("3", camera_id)
        result = await db.fetch_one(query)
        if result:
            updated_cameras.append(result)

    return updated_cameras


async def get_camera_list(
    db: Database,
    is_enabled: Optional[bool] = None,
    search: Optional[str] = None
) -> List[Camera]:
    query = select([cameras])

    if is_enabled is not None:
        query = query.where(cameras.c.isEnabled == is_enabled)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                cameras.c.name.ilike(search_pattern),
                cameras.c.id.ilike(search_pattern),
                cameras.c.dist.ilike(search_pattern)
            )
        )

    results = await db.fetch_all(query)
    return [Camera(**result) for result in results]


async def follow_camera_service(db: Database, request: FollowRequest):
    camera_query = await db.fetch_one(
        select([cameras]).where(cameras.c._id == request.cameraId)
    )
    if camera_query is None:
        raise HTTPException(status_code=404, detail="Camera does not exist")

    follow_query = await db.fetch_one(
        select([follow_camera]).where(
            and_(
                follow_camera.c.cameraId == request.cameraId,
                follow_camera.c.userId == request.userId
            )
        )
    )
    if follow_query is not None:
        raise HTTPException(
            status_code=400, detail="User already following this camera"
        )

    follow_entry = {
        '_id': str(uuid4()),
        'cameraId': request.cameraId,
        'userId': request.userId,
        'userEmail': request.userEmail,
    }
    insert_query = insert(follow_camera).values(follow_entry)
    await db.execute(insert_query)

    return follow_entry


async def unfollow_camera_service(db: Database, _id: str):
    query = delete(follow_camera).where(follow_camera.c._id == _id)

    result = await db.execute(query)

    if result is None:
        raise HTTPException(
            status_code=404, detail="Follow camera  not found"
        )

    return {"message": "Follow camera deleted successfully"}
