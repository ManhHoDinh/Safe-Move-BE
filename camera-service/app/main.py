from fastapi import FastAPI
from app.api.camera import cameras
from app.api.db import metadata, database, engine

metadata.create_all(engine)

app = FastAPI(openapi_url="/api/v1/cameras/openapi.json", docs_url="/api/v1/cameras/docs")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(cameras, prefix='/api/v1/cameras', tags=['cameras'])