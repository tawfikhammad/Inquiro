from fastapi import APIRouter, Request, Body, status, HTTPException
from fastapi.responses import JSONResponse
from controllers import RAGController
from models import ProjectModel, ChunkModel
from .schema import PushRequest, SearchRequest
from utils.enums import ResponseSignals
from utils import get_logger
logger = get_logger(__name__)

rag_router = APIRouter()

@rag_router.post("/vdb/index/")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    logger.info(f"Indexing request received for project_id: {project_id} with reset={push_request.do_reset}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    has_records = True
    page_no = 1
    inserted_items_count = 0

    collection_name = rag_controller.create_collection_name(project_id=project_id)
    await request.app.vectordb_client.create_collection(
        collection_name=collection_name,
        embedding_size=request.app.embedding_client.embedding_size,
        do_reset=push_request.do_reset,
    )

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(Chunks_project_id=project_id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        await rag_controller.index_into_vdb(
            collection_name=collection_name,
            chunks=page_chunks
        )   
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VDB_INSERT_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@rag_router.get("/vdb/info")
async def get_project_index_info(request: Request, project_id: str):
    logger.info(f"Index info request received for project_id: {project_id}")
    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    collection_info = await rag_controller.get_vdb_collection_info(project=project)
    if not collection_info:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignals.VDB_INFO_RETRIEVED_ERROR.value
            }
        )
    return JSONResponse(
        content={
            "signal": ResponseSignals.VDB_INFO_RETRIEVED_SUCCESS.value,
            "collection_info": collection_info
        }
    )

@rag_router.post("/vdb/search")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    logger.info(f"Search request received for project_id: {project_id} with query: {search_request.query} and limit: {search_request.limit}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Project with id {project_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    results = await rag_controller.search(
        project=project,
        query=search_request.query,
        limit=search_request.limit,
        RAGFusion=search_request.RAGFusion
    )
    if not results:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignals.VDB_NO_SEARCH_RESULTS.value
            }
        )
    return JSONResponse(
        content={
            "signal": ResponseSignals.VDB_SEARCH_SUCCESS.value,
            "results": [result.dict() for result in results]
        }
    )

@rag_router.post("/chat/answer")
async def answer_rag(request: Request, project_id: str, search_request: SearchRequest):
    logger.info(f"Answer request received for project_id: {project_id} with query: {search_request.query} and limit: {search_request.limit}")

    project_model = await ProjectModel.get_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Project with id {project_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignals.PAPER_NOT_FOUND.value
        )
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    answer, full_prompt = await rag_controller.answer(
        project=project,
        query=search_request.query,
        limit=search_request.limit,
    )
    if not answer:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignals.RAG_NO_ANSWER.value,
                "answer": None,
                "full_prompt": full_prompt,
            }
        )
    return JSONResponse(
        content={
            "signal": ResponseSignals.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
        }
    )
