from datetime import datetime, timezone

from databases import Database
from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, Integer,
                        MetaData, String, Table, create_engine)
from sqlalchemy.dialects.postgresql import JSONB

DATABASE_URI = 'postgresql://cameras_owner:vgQ6znmdqUo4@ep-holy-unit-a168mnk4.ap-southeast-1.aws.neon.tech/cameras?sslmode=require'

engine = create_engine(DATABASE_URI)
metadata = MetaData()

cameras = Table(
    'cameras',
    metadata,
    Column('_id', String, primary_key=True),
    Column('id', String, unique=True, nullable=False),
    Column('name', String(50), nullable=False),
    Column('loc', JSONB),
    Column('values', JSONB),
    Column('dist', String(50)),
    Column('angle', Integer),
    Column('ptz', Boolean),
    Column('liveviewUrl', String(250)),
    Column('isEnabled', Boolean, default=False),
    Column('lastmodified', DateTime, default=datetime.utcnow())
)

follow_camera = Table(
    'follow_camera',
    metadata,
    Column('_id', String, primary_key=True),
    Column('cameraId', String),
    Column('userId', String),
    Column('userEmail', String),
)

database = Database(DATABASE_URI)


async def get_db():
    return database
