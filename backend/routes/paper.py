from fastapi import APIRouter, UploadFile, File, Depends, status, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from config import app_settings, AppSettings
from controllers import DataController
from models import ProjectModel, PaperModel
from models.db_schemas import Paper
from utils.enums import ResponseSignals, AssetTypeEnums
import aiofiles
from pathlib import Path
import os

import logging
logger = logging.getLogger('unicorn.errors')


papers_router = APIRouter()

@papers_router.post("/upload-paper")
async def upload_paper(request: Request, project_id: str, file: UploadFile = File(...),
                     app_settings : AppSettings = Depends(app_settings)):
    
    """
    Upload a file to a project.
    - Validates file type and size
    - Saves file to the project directory
    - Creates an paper record in the database
    """
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Error retrieving project: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found.")
    
    isvalid, message = DataController().validfile(file=file)
    if not isvalid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": message})
    
    file_path, file_name = DataController().paper_path(project_title=project.project_title, filename=file.filename)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk:= await file.read(app_settings.CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"message": ResponseSignals.FAILED_UPLOAD.value})
    
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    paper = await paper_model.create_paper(
        paper(
            paper_project_id=project.id,
            paper_name=file_name,
            paper_type=AssetTypeEnums.PDF.value,
            paper_size=os.path.getsize(file_path)
        ))

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                         content={
                            "message": ResponseSignals.SUCCESS_UPLOAD.value,
                            "file_id": paper.paper_name
                            })

# List all papers by project
@papers_router.get("/")
async def list_papers(request: Request, project_id: str):
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    papers = await paper_model.get_papers_by_project(paper_project_id=project_id)

    return JSONResponse(
        status_code=200,
        content=[paper.dict(by_alias=True, exclude_unset=True) for paper in papers]
    )

# Get paper details by ID
@papers_router.get("/{paper_id}")
async def get_paper(request: Request, project_id: str, paper_id: str):
    paper_model = await PaperModel.get_instance(db_client= request.app.mongodb_client)
    paper = await paper_model.get_paper_by_project(paper_project_id= project_id, paper_id= paper_id)

    if not paper:
        logger.error(f"Error retrieving paper: {paper_id}")
        raise HTTPException(status_code=404, detail="Paper not found.")

    return JSONResponse(
        status_code=200,
        content=paper.dict(by_alias=True, exclude_unset=True)
    )


# Delete a paper
@papers_router.delete("/{paper_id}")
async def delete_paper(request: Request, project_id: str, paper_id: str):
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    result = await paper_model.delete_paper_by_project(paper_project_id= project_id ,paper_id= paper_id)

    if not result:
        logger.error(f"Error deleting paper: {paper_id}")
        raise HTTPException(status_code=404, detail="Paper not found.")

    return JSONResponse(
        status_code=200,
        content={"message": "Paper deleted successfully."}
    )

# Serve PDF file
@papers_router.get("/view/{paper_id}")
async def serve_pdf_file(request: Request, project_id: str, paper_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    paper = await paper_model.get_paper_by_project(paper_project_id=project_id, paper_id=paper_id)

    paper_path, filename = DataController().paper_path(project_title=project.project_title, filename=paper.paper_name)
    if not Path(paper_path):
        raise HTTPException(status_code=404, detail=ResponseSignals.FILE_NOT_FOUND.value)
    
    try:
        return FileResponse(
            paper_path,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error displaying PDF file: {e}")
        raise HTTPException(status_code=500, detail="Internal error displaying PDF file.")