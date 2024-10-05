from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Date,
    Boolean,
    Enum,
    MetaData,
    Float,
    create_engine
)
from databases import Database
from app.api.models import FloodLevel


DATABASE_URI = 'postgresql://movie-service-database_owner:DcMx0NO8ShfQ@ep-muddy-scene-a1mdwe61.ap-southeast-1.aws.neon.tech/movie-service-database?sslmode=require'

engine = create_engine(DATABASE_URI)
metadata = MetaData()

cameras = Table(
    'cameras',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('url', String(250)),
    Column('createdAt', Date),
    Column('updatedAt', Date),
    Column('isActive', Boolean),
    Column('longitude', Float),
    Column('latitude', Float),
    Column('address', String(250)),
    Column('floodLevel', Enum(FloodLevel))
)

database = Database(DATABASE_URI)
