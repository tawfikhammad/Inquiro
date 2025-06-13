from fastapi import APIRouter, Depends
from config import AppSettings, app_settings

welcome_router = APIRouter()

@welcome_router.get("/")
async def welcome(app_settings : AppSettings = Depends(app_settings)):

    project_name = app_settings.APP_NAME
    version = app_settings.APP_VERSION

    return {"message": f"Welcome to {project_name} {version}"}