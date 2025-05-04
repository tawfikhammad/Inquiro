from fastapi import APIRouter, UploadFile, File, Depends, status, Request
from fastapi.responses import JSONResponse
from config import app_settings, AppSettings
from controllers import DataController
from models import ProjectModel, AssetModel
from models.db_schemas import Asset
from utils.enums import ResponseSignals, AssetTypeEnums
import aiofiles
import os

import logging
logger = logging.getLogger('unicorn.errors')


upload_router = APIRouter()

@upload_router.post("/upload-pdf/{project_title}")
async def upload_pdf(request: Request , file: UploadFile = File(...), project_title: str = "default_project",
                     app_settings : AppSettings = Depends(app_settings)):
    
    """
    Upload a file to a project.
    - Validates file type and size
    - Saves file to the project directory
    - Creates an asset record in the database
    """
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_or_create_project(project_title=project_title)
    
    isvalid, message = DataController().validfile(file=file)
    if not isvalid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": message})
    
    file_path, file_name = DataController().file_path(project_title=project_title, filename=file.filename)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk:= await file.read(app_settings.CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"message": ResponseSignals.FAILED_UPLOAD.value})
    
    asset_model = await AssetModel.get_instance(db_client=request.app.mongodb_client)
    asset = await asset_model.create_asset(
        Asset(
            asset_project_id=project.id,
            asset_name=file_name,
            asset_type=AssetTypeEnums.PDF.value,
            asset_size=os.path.getsize(file_path)
        ))

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                         content={
                            "message": ResponseSignals.SUCCESS_UPLOAD.value,
                            "file_id": asset.asset_name
                            })
