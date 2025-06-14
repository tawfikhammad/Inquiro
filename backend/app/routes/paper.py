from fastapi import APIRouter, UploadFile, File, Depends, status, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from config import app_settings, AppSettings
from controllers import PaperController
from .schema import ProcessRequest
from models import ProjectModel, PaperModel, ChunkModel
from models.db_schemas import Paper, Project, Chunk
from utils.enums import ResponseSignals, AssetTypeEnums
import aiofiles
from pathlib import Path
import os

import logging
logger = logging.getLogger('unicorn.errors')

def _serialize_paper(paper):
    paper_dict = paper.dict(by_alias=True, exclude_unset=True)
    if "_id" in paper_dict and paper_dict["_id"]:
        paper_dict["_id"] = str(paper_dict["_id"])
    if "paper_project_id" in paper_dict and paper_dict["paper_project_id"]:
        paper_dict["paper_project_id"] = str(paper_dict["paper_project_id"])
    return paper_dict

papers_router = APIRouter()

@papers_router.post("/upload-paper")
async def upload_paper(request: Request, project_id: str, file: UploadFile = File(...),
                     app_settings : AppSettings = Depends(app_settings)):
    
    """
    Upload a file to a project.
    - Validates file type and size
    - Saves file to the project directory
    - Creates an paper record in the database
    - Generates chunks from the file 
    - saves chunks to the database
    """
    
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Error retrieving project: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found.")
    
    isvalid, message = PaperController().validfile(file=file)
    if not isvalid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": message})
    
    paper_path, paper_name = PaperController().paper_path(project_title=project.project_title, paper_name=file.filename)

    try:
        async with aiofiles.open(paper_path, "wb") as f:
            while chunk:= await file.read(app_settings.CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"message": ResponseSignals.FAILED_UPLOAD.value})
    
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    paper = await paper_model.get_paper_by_name(
        paper_project_id=project_id,
        paper_name=paper_name)

    if paper:
        logger.info(f"Paper already exists: {paper.id}")
        return JSONResponse(status_code=200,
                            content={
                                "message": ResponseSignals.PAPER_EXISTS.value,
                                "paper": _serialize_paper(paper)})

    paper = await paper_model.create_paper(
        Paper(
            paper_project_id=project.id,
            paper_name=paper_name,
            paper_type=AssetTypeEnums.PDF.value,
            paper_size=os.path.getsize(paper_path)
        ))
    
    chunk_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)
    chunks = PaperController().get_chunks(
        project_title=project.project_title,
        paper_name=paper.paper_name,
        chunk_size=100,
        chunk_overlap=20
    )

    if not chunks:
        logger.warning(f"No chunks generated for paper {paper.id}.")
        return JSONResponse(status_code=204, content={"message": ResponseSignals.FAILED_PROCESS_FILE.value})
    
    inserted_chunks = [
        Chunk(
            chunk_project_id=project.id,
            chunk_paper_id=paper.id,
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_id=i
        ) for i, chunk in enumerate(chunks)
    ]

    no_chunks = await chunk_model.insert_chunks(inserted_chunks)

    return JSONResponse(
        status_code=200,
        content={
            "message": ResponseSignals.SUCCESS_UPLOAD.value,
            "paper_id": _serialize_paper(paper),
            "no_chunks": no_chunks
        }
    )

# List all papers by project
@papers_router.get("/")
async def list_papers(request: Request, project_id: str):
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)
    papers = await paper_model.get_papers_by_project(paper_project_id=project_id)

    return JSONResponse(
        status_code=200,
        content=[_serialize_paper(paper) for paper in papers]
    )

# Get paper details by ID
@papers_router.get("/{paper_id}")
async def get_paper(request: Request, project_id: str, paper_id: str):
    paper_model = await PaperModel.get_instance(db_client= request.app.mongodb_client)
    paper = await paper_model.get_paper_by_id(paper_project_id= project_id, paper_id= paper_id)

    if not paper:
        logger.error(f"Error retrieving paper: {paper_id}")
        raise HTTPException(status_code=404, detail="Paper not found.")

    return JSONResponse(
        status_code=200,
        content=_serialize_paper(paper)
    )

# Delete a paper
@papers_router.delete("/{paper_id}")
async def delete_paper(request: Request, project_id: str, paper_id: str):
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    paper_model = await PaperModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Error retrieving project: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found.")
    
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        logger.error(f"Error retrieving paper: {paper_id}")
        raise HTTPException(status_code=404, detail="Paper not found.")
    
    paper_path, paper_name = PaperController().paper_path(project_title=project.project_title, paper_name=paper.paper_name)

    # Delete the paper file from the filesystem
    if Path(paper_path).exists():
        try:
            Path(paper_path).unlink()
        except Exception as e:
            logger.error(f"Error deleting summary file: {e}")
            raise HTTPException(status_code=500, detail="Internal error deleting file.")

    # Delete the paper file from db
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
    paper = await paper_model.get_paper_by_id(paper_project_id=project_id, paper_id=paper_id)
    if not paper:
        logger.error(f"Error retrieving paper: {paper_id}")
        raise HTTPException(status_code=404, detail="Paper not found.")

    paper_path, paper_name = PaperController().paper_path(project_title=project.project_title, paper_name=paper.paper_name)
    if not Path(paper_path):
        raise HTTPException(status_code=404, detail=ResponseSignals.FILE_NOT_FOUND.value)
    
    try:
        return FileResponse(
            paper_path,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={paper_name}.pdf"}
        )
    except Exception as e:
        logger.error(f"Error displaying PDF file: {e}")
        raise HTTPException(status_code=500, detail="Internal error displaying PDF file.")