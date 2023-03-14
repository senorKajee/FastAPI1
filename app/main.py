"""
Entry point of the FastAPi apigateway application.

This module contains the main FastAPI application and the initialization of the database connection,
and regristration of the routers. and other stuffs.
"""
import uvicorn
from celery import Celery
from fastapi import FastAPI
from pymongo import MongoClient
from routers import Router


def _create_app() -> FastAPI:
    current_app = FastAPI()
    current_app.celery_app = Celery('tasks', broker='redis://192.168.1.183:49153', backend='redis://192.168.1.183:49153')
    current_app.celery_app.conf.update(task_track_started=True)
    current_app.celery_app.conf.update(task_serializer='pickle')
    current_app.celery_app.conf.update(result_serializer='pickle')
    current_app.celery_app.conf.update(accept_content=['pickle', 'json'])
    current_app.include_router(Router)
    return current_app


app = _create_app()

@app.on_event("startup")
def startup_db_client()-> None:
    """Initialize the database connection. and add connection context to the app object."""
    app.mongodb_client = MongoClient('mongodb://192.168.1.183:49155/fddf?readPreference=primary&directConnection=true&ssl=false')
    app.database = app.mongodb_client["backendSf342"]

@app.on_event("shutdown")
def shutdown_db_client()-> None:
    """Close the database connection."""
    app.mongodb_client.close()

if __name__ == "__main__":
    uvicorn.run("main:app", port=3500, reload=True,host="0.0.0.0")
