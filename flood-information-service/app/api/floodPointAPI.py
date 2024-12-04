from fastapi import APIRouter, Depends,status, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, database
from .database import get_db
import random
from typing import List
import requests
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from fastapi.responses import JSONResponse
import tensorflow as tf
from PIL import Image
import io
from utils import get_image_from_bytes
from loguru import logger
import httpx
from PIL import Image
# URL của API
EXTERNAL_API_URL = "https://api.notis.vn/v4/cameras/bybbox?lat1=11.160767&lng1=106.554166&lat2=9.45&lng2=128.99999"

# Headers cho request
HEADERS = {
    "Host": "api.notis.vn",
    "accept": "application/json, text/plain, */*",
    "device-id": "bf738a0a3e6eddc2",
    "user-agent": "Mozilla/5.0 (Linux; Android 12; Pixel 4 Build/SQ3A.220705.003.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Mobile Safari/537.36",
    "origin": "http://localhost",
    "x-requested-with": "com.fts.notis",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "http://localhost/",
    "accept-language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
}
# Load the trained model
model = load_model("./fine_tuned_flood_detection_model.keras")

# Define the expected input size for your model
IMAGE_HEIGHT = 224
IMAGE_WIDTH = 224
# Function to preprocess an image for the model
def preprocess_image(image: Image.Image) -> np.ndarray:
    """Resize and normalize an image for model input."""
    img = image.resize((IMAGE_HEIGHT, IMAGE_WIDTH))
    img_array = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

async def predict(image: Image.Image) -> int:
    """Make a prediction based on the preprocessed image."""
    try:
        img_array = preprocess_image(image)
        pred = model.predict(img_array)
        predicted_class = np.argmax(pred, axis=1)[0]
        label = "Flooding" if predicted_class == 0 else "Normal"
        print("Prediction: ", label)
        return predicted_class
    except Exception as e:
        logger.error("Error during prediction: {}", e)
        return 0  # Return 0 if there's an error
    
async def get_image_and_detect(url):
    print("URL: ",url)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                image_bytes = response.content
                # Xử lý image_bytes với chức năng detect
                input_image = get_image_from_bytes(image_bytes)
                return input_image
            else:
                logger.error("Failed to fetch image, status code: {}", response.status_code)
    except Exception as e:
        logger.error("Error in fetching or detecting image: {}", e)

async def update_flood_points():
    db = next(get_db())  # Lấy kết nối DB
    delete_expired_flood_points(db)  # Xóa các điểm đã hết hạn
    try:
        response = requests.get(EXTERNAL_API_URL)
        if response.status_code == 200:
            flood_points = response.json()  # Giả định API trả về danh sách JSON
            for point in flood_points:
                latitude = point["loc"]["coordinates"][1]
                longitude = point["loc"]["coordinates"][0]
                name = point["name"]
                existing_point = db.query(models.FloodPoint).filter(
                    models.FloodPoint.latitude == latitude,
                    models.FloodPoint.longitude == longitude
                ).first()
                
                # Thiết lập expiration_time là thời gian hiện tại + 5 phút
                expiration_time = datetime.now() + timedelta(minutes=5)
                
                # Random flood_level từ 0 đến 5
                url = f"http://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx?id={point['_id']}"
            
                flood_level = await predict(get_image_and_detect(url))
                
                # Cập nhật nếu điểm đã tồn tại, thêm mới nếu không tồn tại
                if existing_point:
                    existing_point.name = name
                    existing_point.expiration_time = expiration_time
                    existing_point.flood_level = flood_level
                else:
                    new_point = models.FloodPoint(
                        name=name,
                        latitude=latitude,
                        longitude=longitude,
                        expiration_time=expiration_time,
                        flood_level=flood_level
                    )
                    db.add(new_point)
            db.commit()
    except Exception as e:
        print(f"Error updating flood points: {e}")
    finally:
        db.close()


router = APIRouter()

@router.get("/flood_points/", response_model=List[schemas.FloodPointResponse])
def get_all_flood_points(db: Session = Depends(get_db)):
    flood_points = db.query(models.FloodPoint).all()
    return flood_points

@router.post("/flood_points/", response_model=schemas.FloodPointResponse)
def create_flood_point(point: schemas.FloodPointCreate, db: Session = Depends(get_db)):
    db_point = models.FloodPoint(
        name=point.name,
        latitude=point.latitude,
        longitude=point.longitude,
        flood_level=point.flood_level,
        expiration_time=point.expiration_time
    )
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    return db_point

@router.delete("/flood_points/", response_model=dict)
def delete_flood_point(latitude: float, longitude: float, db: Session = Depends(get_db)):
    db_point = db.query(models.FloodPoint).filter(
        models.FloodPoint.latitude == latitude,
        models.FloodPoint.longitude == longitude
    ).first()
    
    if db_point is None:
        raise HTTPException(status_code=404, detail="Flood point not found")
    
    if db_point.expiration_time < datetime.now():
        raise HTTPException(status_code=410, detail="Flood point has expired and cannot be deleted.")
    
    db.delete(db_point)
    db.commit()
    return {"message": "Flood point deleted successfully"}

@router.delete("/flood_points/expired/", response_model=dict)
def delete_expired_flood_points(db: Session = Depends(get_db)):
    expired_points = db.query(models.FloodPoint).filter(models.FloodPoint.expiration_time < datetime.now()).all()
    if not expired_points:
        return {"message": "No expired flood points to delete"}
    
    for point in expired_points:
        db.delete(point)
    
    db.commit()
    return {"message": f"Deleted {len(expired_points)} expired flood points"}

@router.get('/healthCheck', status_code=status.HTTP_200_OK)
def perform_healthCheck():
    return {'healthCheck': 'Everything OK!'}
