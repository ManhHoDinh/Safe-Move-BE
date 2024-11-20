from supabase import create_client
from fastapi import File, UploadFile
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.api.models import FloodInformation, FloodInformationCreate, EStatus
from app.api import db_manager
from app.api.db import get_db
from supabase import create_client, Client
import uuid


SUPABASE_URL = "https://evrsgjzzvkcfhtmntiul.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV2cnNnanp6dmtjZmh0bW50aXVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTk4MTg0NSwiZXhwIjoyMDQ3NTU3ODQ1fQ.AS6I-5rlQGzgbOazdegBFBB_yU68l7odtIcd0_TAr3w"
SUPABASE_BUCKET = "flood-image"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

flood_information = APIRouter()


@flood_information.get("/", response_model=List[FloodInformation])
async def list_flood_information(
    search: Optional[str] = None,
    status: Optional[EStatus] = None,
    db=Depends(get_db)
) -> List[FloodInformation]:
    return await db_manager.get_flood_information(db, search, status)


@flood_information.post("/", response_model=FloodInformation)
async def create_flood_info(
    flood_info: str, file: UploadFile = File(...), db=Depends(get_db)
):
    try:
        new_flood_info = await db_manager.create_flood_information(db, flood_info, file)
        return new_flood_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@flood_information.put("/{_id}", response_model=FloodInformation)
async def update_flood_info(
    _id: str, flood_info: FloodInformation, db=Depends(get_db)
):
    updated_flood_info = await db_manager.update_flood_information(db, _id, flood_info)
    if not updated_flood_info:
        raise HTTPException(
            status_code=404, detail="Flood information not found")
    return updated_flood_info

# Delete flood information entry by id


@flood_information.delete("/{_id}")
async def delete_flood_info(_id: str, db=Depends(get_db)):
    deleted = await db_manager.delete_flood_information(db, _id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Flood information not found")
    return {"message": "Flood information deleted successfully"}


@flood_information.post("/upload_image/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        # Read the file content
        file_content = await file.read()

        # Generate a unique filename to avoid duplication
        unique_filename = f"uploads/{uuid.uuid4()}_{file.filename}"

        # Upload the file to Supabase Storage
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            unique_filename, file_content, file_options={
                "contentType": file.content_type}
        )

        # Check if the response has an 'error' attribute or if the upload was successful
        if hasattr(response, 'error') and response.error:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file: {response.error['message']}"
            )

        # Get the public URL of the uploaded file
        public_url = supabase.storage.from_(
            SUPABASE_BUCKET).get_public_url(unique_filename)

        return {"file_url": public_url}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
