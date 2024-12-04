# database.py
from pydantic import BaseModel
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from databases import Database

DATABASE_URI = "postgresql://default:RhQD6snM2BfI@ep-flat-base-a1ghdl1j-pooler.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require"
# Khởi tạo engine và sessionmaker
FloodPointBase = declarative_base()
FloodPointMetadata = MetaData()
FloodPointDatabase = Database(DATABASE_URI)
FloodPointEngine = create_engine(DATABASE_URI)

# Dependency để lấy session
def get_flood_point_db():
    return FloodPointDatabase
        
flood_point_table = Table(
    'flood_points',  # The name of the table
    FloodPointMetadata,         # The metadata object
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String(100), index=True, nullable=False),
    Column('latitude', Float, nullable=False),
    Column('longitude', Float, nullable=False),
    Column('flood_level', Integer, nullable=False),
    Column('expiration_time', DateTime, default=datetime.utcnow),
)

class FloodPointCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    flood_level: int
    expiration_time: datetime  # Thời gian hết hạn

class FloodPointResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    flood_level: int
    expiration_time: datetime
    class Config:
        orm_mode = True
