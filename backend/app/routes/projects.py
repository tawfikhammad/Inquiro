from fastapi import APIRouter, File, Depends, status, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from config import app_settings, AppSettings
from models import ProjectModel, PaperModel, SummaryModel
from models.db_schemas import Project, Paper, Summary
from .schema import ProjectRequest
from utils.enums import ResponseSignals, AssetTypeEnums
import os

import logging
logger = logging.getLogger('unicorn.errors')

def _serialize_project(project):
    project_dict = project.dict(by_alias=True, exclude_unset=True)
    project_dict["_id"] = str(project_dict["_id"])
    return project_dict


projects_router = APIRouter()

#List all projects in the database.
@projects_router.get("/")
async def list_projects(request: Request, app_settings: AppSettings = Depends(app_settings)):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    projects = await project_model.get_all_projects()
    serialized_projects = [_serialize_project(project) for project in projects]
    
    return JSONResponse(
        status_code=200,
        content=serialized_projects
    )

# Create a new project.
@projects_router.post("/create")
async def create(request: Request, project_request: ProjectRequest):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    created_project  = await project_model.create_project(project_title=project_request.project_title)
    serialized_project = _serialize_project(created_project)

    return JSONResponse(
        status_code=201,
        content=serialized_project
    )

#Get project details by ID.
@projects_router.get("/{project_id}")
async def get_project(request: Request, project_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    serlized_project = _serialize_project(project)

    return JSONResponse(
        status_code=200,
        content=serlized_project
    )

#delete all projects.
@projects_router.delete("/")
async def delete_all(request: Request):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    deleted_count = await project_model.delete_all_projects()
    
    return JSONResponse(
        status_code=200,
        content={
            "message": f"All projects deleted successfully.",
            "deleted_count": deleted_count
        }
    )
# Delete a project.
@projects_router.delete("/{project_id}")
async def delete_project(request: Request, project_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.delete_project(project_id=project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    return JSONResponse(
        status_code=200,
        content={"message": "Project deleted successfully."}
    )

# List all assets (papers and summaries) in a project.
@projects_router.get('/{project_id}')
async def get_project_assets(request: Request, project_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Error retrieving project: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found.")
    
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    papers = await paper_model.get_papers_by_project(project_id=project.id)

    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summaries = await summary_model.get_summaries_by_project(project.id)
    
    papers_response = [paper.dict(by_alias=True, exclude_unset=True) for paper in papers]
    summaries_response = [summary.dict(by_alias=True, exclude_unset=True) for summary in summaries]
    
    return JSONResponse(
        status_code=200,
        content={
            "papers number": len(papers_response),
            "summaries number": len(summaries_response)
        }
    )
    
    



    

