from fastapi import APIRouter, File, Depends, status, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from models import ProjectModel, PaperModel, SummaryModel
from models.db_schemas import Project
from .schema import ProjectRequest
from utils.enums import ResponseSignals

from utils import get_logger
logger = get_logger(__name__)

def _serialize_project(project):
    project_dict = project.dict(by_alias=True, exclude_unset=True)
    project_dict["_id"] = str(project_dict["_id"])
    return project_dict


project_router = APIRouter()

#List all projects in the database.
@project_router.get("/")
async def list_projects(request: Request):
    logger.info("Incoming request to list all projects.")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    projects = await project_model.get_all_projects()
    if not projects or len(projects) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    serialized_projects = [_serialize_project(project) for project in projects]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=serialized_projects
    )

# Create a new project.
@project_router.post("/create")
async def create(request: Request, project_request: ProjectRequest):
    logger.info(f"Incoming request to create project with title: {project_request.project_title}")
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    created_project  = await project_model.get_or_create_project(
        Project(project_title=project_request.project_title)
    )
    serialized_project = _serialize_project(created_project)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": ResponseSignals.PROJECT_CREATED_SUCCESS.value,
            "project": serialized_project
        }
    )
# Get project details by ID.
@project_router.get("/{project_id}")
async def get_project(request: Request, project_id: str):
    logger.info(f"Incoming request to get project by ID: {project_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )

    serialized_project = _serialize_project(project)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=serialized_project
    )

# Delete all projects.
@project_router.delete("/")
async def delete_all(request: Request):
    logger.info("Incoming request to delete all projects.")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    deleted_count = await project_model.delete_all_projects()
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

# Delete a project.
@project_router.delete("/{project_id}")
async def delete_project(request: Request, project_id: str):
    logger.info(f"Incoming request to delete project by ID: {project_id}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    deleted_count = await project_model.delete_project(project_id=project_id)
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

# List all assets (papers and summaries) in a project.
@project_router.get('/{project_id}/assets')
async def get_project_assets(request: Request, project_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if project == 0:
        logger.warning(f"Project not found when fetching assets: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PROJECT_NOT_FOUND.value
        )
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    papers = await paper_model.get_papers_by_project(papers_project_id=project_id)

    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summaries = await summary_model.get_summaries_by_project(summaries_project_id=project_id)
    
    papers_response = [paper.dict(by_alias=True, exclude_unset=True) for paper in papers]
    summaries_response = [summary.dict(by_alias=True, exclude_unset=True) for summary in summaries]
    
    return JSONResponse(
        status_code=200,
        content={
            "papers number": len(papers_response),
            "summaries number": len(summaries_response)
        }
    )
    
    



    

