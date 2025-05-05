from fastapi import APIRouter, UploadFile, File, Depends, status, Request, HTTPException, Body
from fastapi.responses import JSONResponse, PlainTextResponse
from config import app_settings, AppSettings
from controllers import DataController
from models import ProjectModel, PaperModel, SummaryModel
from models.db_schemas import Paper, Summary
from utils.enums import ResponseSignals, AssetTypeEnums
from pathlib import Path
import os

import logging
logger = logging.getLogger('unicorn.errors')


summaries_router = APIRouter()

# Create a summary for a paper in a project.
@summaries_router.post("/create")
async def create_summary(request: Request, project_id: str, paper_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    # Check if the project exists
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Check if the paper exists
    paper = await paper_model.get_paper_by_project(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    
    file_path, file_name = DataController().file_path(project_title=project.project_title, filename=paper.paper_name)

    # Create summary record in the database
    summary = {
        "summary_project_id": project.id,
        "summary_paper_id": paper.id,
        "summary_name": file_name,
        "summary_type": AssetTypeEnums.MD.value,
        "summary_size": os.path.getsize(file_path)
    }

    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summary_record = await summary_model.create_summary(Summary(summary))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": ResponseSignals.SUCCESS_UPLOAD.value,
            "summary_id": str(summary_record.id)     
            }
    )

# List all summaries by project
@summaries_router.get("/")
async def list_summaries(request: Request, project_id: str):
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summaries = await summary_model.get_summaries_by_project(summary_project_id=project_id)

    return JSONResponse(
        status_code=200,
        content=[summary.dict(by_alias=True, exclude_unset=True) for summary in summaries]
    )

# Get a summary by 
@summaries_router.get("/{summary_id}")      
async def get_summary(request: Request, project_id: str, summary_id: str):
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summary = await summary_model.get_summary_by_project(summary_project_id=project_id, summary_id=summary_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found.")

    return JSONResponse(
        status_code=200,
        content=summary.dict(by_alias=True, exclude_unset=True)
    )

# Delete a summary by ID
@summaries_router.delete("/{summary_id}")
async def delete_summary(request: Request, project_id: str, summary_id: str):
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    result = await summary_model.delete_summary_by_project(project_summary_id=project_id, summary_id=summary_id)

    if not result:
        raise HTTPException(status_code=404, detail="Summary not found.")

    return JSONResponse(
        status_code=200,
        content={"message": "Summary deleted successfully."}
    )

# Serve the summary file
@summaries_router.get("/view/{summary_id}")
async def serve_summary_file(request: Request, project_id: str, paper_id: str, summary_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    paper = await paper_model.get_paper_by_project(paper_project_id=project_id, paper_id=paper_id)

    summary_path, filename = DataController().summary_path(
        project_title=project.project_title,
        filename=paper.paper_name
    )
    path = Path(summary_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=ResponseSignals.FILE_NOT_FOUND.value)

    try:
        content = path.read_text(encoding="utf-8")
        return PlainTextResponse(
            content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )
    except Exception as e:
        logger.error("Error serving summary %s: %s", summary_path, e)
        raise HTTPException(status_code=500, detail="Internal error displaying summary file.")
    

# Update the summary file with new content
@summaries_router.put("/{summary_id}", response_class=PlainTextResponse)
async def update_summary_file(request: Request, project_id: str, paper_id: str, summary_id: str,
    new_content: str = Body(..., media_type="text/markdown")):

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model   = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    paper   = await paper_model.get_paper_by_project(paper_project_id=project_id, paper_id=paper_id)

    summary_path, filename = DataController().summary_path(
        project_title=project.project_title,
        filename=paper.paper_name)
    
    path = Path(summary_path)
    if not path.exists():
        logger.error("Summary file not found: %s", summary_path)
        raise HTTPException(status_code=404, detail=ResponseSignals.FILE_NOT_FOUND.value)

    try:
        path.write_text(new_content, encoding="utf-8")
        return PlainTextResponse(
            new_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )
    except Exception as e:
        logger.error("Error writing summary %s: %s", summary_path, e)
        raise HTTPException(
            status_code=500,
            detail="Internal error updating summary file."
        )
