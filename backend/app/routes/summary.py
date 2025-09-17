from fastapi import APIRouter, status, Request, HTTPException, Body
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from controllers import PaperController, SummaryController
from models import ProjectModel, PaperModel, SummaryModel
from models.db_schemas import Summary
from utils.enums import ResponseSignals, AssetTypeEnums
from pathlib import Path
import os

from utils import get_logger 
logger = get_logger(__name__)


def _serialize_summary(summary):
    summary_dict = summary.dict(by_alias=True, exclude_unset=True)
    summary_dict["_id"] = str(summary_dict["_id"])
    summary_dict["summary_project_id"] = str(summary_dict["summary_project_id"])
    summary_dict["summary_paper_id"] = str(summary_dict["summary_paper_id"])
    return summary_dict

summary_router = APIRouter()

# Create a summary.
@summary_router.post("/create")
async def create_summary(request: Request, project_id: str, paper_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    # Check if the project exists
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    # Check if the paper exists
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")
    
    paper_controller = PaperController()
    paper_path, paper_name = await paper_controller.paper_path(project.project_title, paper.paper_name)
    
    summary_controller = SummaryController(summary_client=request.app.summary_client)
    summary_path, summary_name = await summary_controller.summary_path(project.project_title, paper.paper_name)

    summary = Summary(
        summary_project_id=project.id,
        summary_paper_id=paper.id,
        summary_name=summary_name,
        summary_type=AssetTypeEnums.MD.value
    )

    if Path(summary_path).exists():
        summary = await summary_model.get_or_create_summary(summary)
        return JSONResponse(status_code=status.HTTP_201_CREATED, 
            content={
                "message": "Summary already exists",
                "summary": _serialize_summary(summary)
            }
        )

    try:
        summary_content = await summary_controller.generate_summary(paper_path, paper_name)
        await summary_controller.save_summary(summary_path, summary_content)

        summary.summary_size = os.path.getsize(summary_path)
        summary = await summary_model.get_or_create_summary(summary)

        logger.info(f"Summary created successfully for paper: {paper_name}")

    except Exception as e:
        logger.error(f"Failed to create summary: {e}")
        if Path(summary_path).exists():
            Path(summary_path).unlink()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create summary")


    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": ResponseSignals.SUCCESS_UPLOAD.value,
            "summary": _serialize_summary(summary)     
        }
    )

# List all summaries by project
@summary_router.get("/")
async def list_summaries(request: Request, project_id: str):
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summaries = await summary_model.get_summaries_by_project(summary_project_id=project_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[_serialize_summary(summary) for summary in summaries]
    )

# Get a summary by project
@summary_router.get("/{summary_id}")      
async def get_summary(request: Request, project_id: str, summary_id: str):
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    summary = await summary_model.get_summary_by_project(summary_project_id=project_id, summary_id=summary_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found.")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=_serialize_summary(summary)  
    )

# Delete a summary by ID
@summary_router.delete("/{summary_id}")
async def delete_summary(request: Request, project_id: str, paper_id: str, summary_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")

    summary_controller = SummaryController(summary_client=request.app.summary_client)
    summary_path, _ = await summary_controller.summary_path(project.project_title, paper.paper_name)
    
    summary = await summary_model.get_summary_by_project(summary_project_id=project_id, summary_id=summary_id)
    if not summary:
        # Clean orphan file if exists
        if Path(summary_path).exists():
            Path(summary_path).unlink()
            logger.warning(f"Deleted orphan summary file at {summary_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found.")

    # Delete from DB
    result = await summary_model.delete_summary_by_project(project_summary_id=project_id, summary_id=summary.id)
    if result == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found.")

    # Delete file
    if Path(summary_path).exists():
        Path(summary_path).unlink()
        logger.info(f"Summary file deleted at {summary_path}")

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

# Serve the summary file
@summary_router.get("/view/{summary_id}")
async def serve_summary_file(request: Request, project_id: str, paper_id: str, summary_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")
        
    # if summary exists in db
    summary = await summary_model.get_summary_by_project(summary_project_id=project_id, summary_id=summary_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found.")

    summary_controller = SummaryController(request.app.summary_client)
    summary_path, summary_name = await summary_controller.summary_path(project_title=project.project_title, paper_name=paper.paper_name)
    
    # if summary exists in filesystem
    if not Path(summary_path).exists():
        logger.error(f"Summary file not found at {summary_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignals.FILE_NOT_FOUND.value)

    try:
        def iter_file(path, chunk_size=1024*1024):
            with open(path, "r", encoding="utf-8") as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        return StreamingResponse(
            iter_file(Path(summary_path)),
            media_type="text/markdown",
            headers={"Content-Disposition": f'inline; filename="{summary_name}.md"'}
        )
    except Exception as e:
        logger.error(f"Error displaying summary: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error displaying summary file.")

# Update the summary file with new content
@summary_router.put("/{summary_id}", response_class=PlainTextResponse)
async def update_summary_file(request: Request, project_id: str, paper_id: str, summary_id: str,
    new_content: str = Body(..., media_type="text/markdown")):

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model   = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    summary_model = await SummaryModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")
        
    summary = await summary_model.get_summary_by_project(summary_project_id=project_id, summary_id=summary_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found.")
    
    summary_controller = SummaryController(summary_client=request.app.summary_client)
    summary_path, summary_name = await summary_controller.summary_path(project.project_title, paper.paper_name)
    
    path = Path(summary_path)
    if not path.exists():
        logger.error(f"Summary file not found at: {summary_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseSignals.FILE_NOT_FOUND.value)

    try:
        path.write_text(new_content, encoding="utf-8")

        #update summary size
        summary.summary_size = os.path.getsize(summary_path)
        await summary_model.update_summary(summary)

        return PlainTextResponse(
            new_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'inline; filename="{summary_name}.md"'}
        )
    except Exception as e:
        logger.error(f"Error updating summary {summary_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error updating summary file."
        )
