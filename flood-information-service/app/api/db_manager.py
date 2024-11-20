from typing import List, Optional
from app.api.db import flood_information
from app.api.models import FloodInformation, FloodInformationCreate
from databases import Database
from sqlalchemy import or_, select, insert, update, delete, cast, Text, and_
from uuid import uuid4
from fastapi import HTTPException, File, UploadFile, Form
from supabase import create_client, Client
import uuid
import json


SUPABASE_URL = "https://evrsgjzzvkcfhtmntiul.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV2cnNnanp6dmtjZmh0bW50aXVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTk4MTg0NSwiZXhwIjoyMDQ3NTU3ODQ1fQ.AS6I-5rlQGzgbOazdegBFBB_yU68l7odtIcd0_TAr3w"
SUPABASE_BUCKET = "flood-image"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def create_upload_file(file: UploadFile = File(...)):
    try:
        file_content = await file.read()

        unique_filename = f"uploads/{uuid.uuid4()}_{file.filename}"

        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            unique_filename, file_content, file_options={
                "contentType": file.content_type}
        )

        if hasattr(response, 'error') and response.error:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file: {response.error['message']}"
            )

        public_url = supabase.storage.from_(
            SUPABASE_BUCKET).get_public_url(unique_filename)

        return {"file_url": public_url}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )


async def get_flood_information(
    db: Database,
    search: Optional[str] = None,
    status: Optional[str] = None
) -> List[FloodInformation]:
    query = select(flood_information)

    conditions = []

    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                flood_information.c.locationName.ilike(search_pattern),
                flood_information.c.userName.ilike(search_pattern)
            )
        )

    # Add status condition if it exists
    if status:
        conditions.append(cast(flood_information.c.status,
                          Text).ilike(status))

    if conditions:
        query = query.where(and_(*conditions))

    results = await db.fetch_all(query)
    return [FloodInformation(**result) for result in results]


async def create_flood_information(db: Database, flood_info: str, file: UploadFile = File(...)):
    try:
        flood_info_data = json.loads(flood_info)
        flood_info_model = FloodInformationCreate(**flood_info_data)

        upload_response = await create_upload_file(file)
        file_url = upload_response["file_url"]
        new_flood_info = {
            "_id": str(uuid4()),
            "userName": flood_info_model.userName,
            "userId": flood_info_model.userId,
            "location": flood_info_model.location.dict(),
            "locationName": flood_info_model.locationName,
            "status": flood_info_model.status,
            "floodLevel": flood_info_model.floodLevel,
            "url": file_url,
        }
        query = insert(flood_information).values(new_flood_info)
        await db.execute(query)

        return FloodInformation(**new_flood_info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def update_flood_information(db: Database, _id: str, flood_info: FloodInformation):
    query = (
        update(flood_information)
        .where(flood_information.c._id == _id)
        .values(
            userName=flood_info.userName,
            userId=flood_info.userId,
            location=flood_info.location.dict(),
            locationName=flood_info.locationName,
            status=flood_info.status,
            floodLevel=flood_info.floodLevel,
            date=flood_info.date
        )
        .returning(flood_information)
    )

    result = await db.fetch_one(query)

    if result is None:
        raise HTTPException(
            status_code=404, detail="Flood information not found"
        )

    return FloodInformation(**result)


async def delete_flood_information(db: Database, _id: str):
    query = delete(flood_information).where(flood_information.c._id == _id)

    # Execute the query and get the result
    result = await db.execute(query)

    if result == 0:  # No rows were deleted
        raise HTTPException(
            status_code=404, detail="Flood information not found"
        )

    return {"message": "Flood information deleted successfully"}
