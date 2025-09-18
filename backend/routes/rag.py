from fastapi import APIRouter, Request, Body, status
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
    project_model = await ProjectModel.get_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.db_client)

    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Project with id {project_id} not found.")
        raise
    
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project_id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids =  list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        
        rag_controller.index_into_vdb(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids
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
    
    project_model = await ProjectModel.get_instance(db_client=request.app.db_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Project with id {project_id} not found.")
        raise

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    collection_info = rag_controller.get_vdb_collection_info(project=project)
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
    
    project_model = await ProjectModel.get_instance(db_client=request.app.db_client)
    project = await project_model.get_project_by_id(project_id=project_id)
    if not project:
        logger.error(f"Project with id {project_id} not found.")
        raise

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    results = rag_controller.search(
        project=project,
        query=search_request.query,
        limit=search_request.limit
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
    
    project_model = await ProjectModel.get_instance(db_client=request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    answer, full_prompt = rag_controller.answer(
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
