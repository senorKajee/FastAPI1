"""
Routers Module for FastAPI.

this module is used to import all routers and compose them into one router to be used in the main app.

Route Table
----------------
| Path | Method | Handler | Description |
|------|--------|---------|-------------|
| / | GET | baseRouter | Contain all path in base path |

"""
from fastapi import APIRouter

from .base_router import router as baseRouter

Router = APIRouter(prefix='', responses={404: {"description": "Not found"}})

Router.include_router(baseRouter)
