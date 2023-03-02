
from fastapi import FastAPI
from routers.test import router as testRouter
import uvicorn as uvicorn

from pymongo import MongoClient
from celery import Celery



def create_app() -> FastAPI:
    current_app = FastAPI()
    # current_app.include_router(universities.router)
    current_app.celery_app = Celery('tasks', broker='redis://192.168.1.183:49153', backend='redis://192.168.1.183:49153')
    # current_app.celery_app = Celery('tasks', broker='redis://localhost:10000', backend='redis://localhost:10000')


    current_app.celery_app.conf.update(task_track_started=True)
    current_app.celery_app.conf.update(task_serializer='pickle')
    current_app.celery_app.conf.update(result_serializer='pickle')
    current_app.celery_app.conf.update(accept_content=['pickle', 'json'])
    current_app.include_router(testRouter)
    return current_app


app = create_app()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient('mongodb://192.168.1.183:49155/fddf?readPreference=primary&directConnection=true&ssl=false')
    app.database = app.mongodb_client["backendSf342"]

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}



if __name__ == "__main__":
    uvicorn.run("main:app", port=3500, reload=True,host="0.0.0.0")