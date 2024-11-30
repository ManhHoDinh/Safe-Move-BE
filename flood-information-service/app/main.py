from fastapi import FastAPI
from app.api.flood_information import flood_information
from app.api.db import metadata, database, engine
from fastapi.middleware.cors import CORSMiddleware
from app.api.flood_point_db import FloodPointMetadata, FloodPointDatabase, FloodPointEngine

metadata.create_all(engine)
FloodPointMetadata.create_all(FloodPointEngine)
app = FastAPI(openapi_url="/api/v1/flood-information/openapi.json",
              docs_url="/api/v1/flood-information/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()
    await FloodPointDatabase.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await FloodPointDatabase.disconnect()


app.include_router(flood_information, prefix='/api/v1/flood-information',
                   tags=['flood-information'])
