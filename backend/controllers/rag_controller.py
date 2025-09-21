from .base_controller import BaseController
from models.db_schemas import Project, Chunk
from AI.LLM.LLMEnums import DocumentTypeEnum
from typing import List
import json
import asyncio
from utils import get_logger
logger = get_logger(__name__)

class RAGController(BaseController):
    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vdb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=str(project.id))
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def get_vdb_collection_info(self, project: Project):
        try:
            collection_name = self.create_collection_name(project_id=str(project.id))
            collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)

            return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))
        except Exception as e:
            logger.error(f"Error retrieving collection info for project {str(project.id)}: {e}")
            return None
        
    async def index_into_vdb(self, collection_name: str, chunks: List[Chunk], chunks_ids: List[int]):
        try:
            texts = [c.chunk_text for c in chunks]
            metadata = [c.chunk_metadata for c in chunks]
            
            # Limit concurrency for embedding requests to avoid quota issues
            sem = asyncio.Semaphore(8)
            async def embed_with_limit(t):
                async with sem:
                    return await self.embedding_client.embed_text(text=t, document_type=DocumentTypeEnum.DOCUMENT.value)

            vectors = await asyncio.gather(*[embed_with_limit(t) for t in texts])
            if not vectors or len(vectors) == 0:
                logger.error(f"Error embedding the text of chunks of collection {collection_name} ")
                raise

            await self.vectordb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                metadata=metadata,
                vectors=vectors,
                record_ids=chunks_ids,
            )

        except Exception as e:
            logger.error(f"Error indexing into VDB for collection {collection_name}: {e}")
            raise

    async def search(self, project: Project, query: str, limit: int = 10):
        try:
            # step1: get collection name
            collection_name = self.create_collection_name(project_id=str(project.id))

            # step2: get text embedding vector
            vector = await self.embedding_client.embed_text(text=query, document_type=DocumentTypeEnum.QUERY.value)
            if not vector or len(vector) == 0:
                logger.error(f"Error embedding the query {str(project.id)}")
                raise

            # step3: do semantic search
            results = await self.vectordb_client.query_search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
                min_score=0.7,
                return_metadata=True
            )
            return results
        except Exception as e:  
            logger.error(f"Error searching VDB for project {str(project.id)}: {e}")
            raise
    
    async def answer(self, project: Project, query: str, limit: int = 10):
        answer, full_prompt = None, None

        # step1: retrieve related documents
        retrieved_documents = await self.search(project=project, query=query, limit=limit,)

        if not retrieved_documents or len(retrieved_documents) == 0:
            logger.warning(f"No documents retrieved for RAG question answering for project {str(project.id)}")
            return answer, full_prompt
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc.text,
                    "chunk_metadata": json.dumps(doc.metadata or {}, ensure_ascii=False)
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt")
        full_prompt = "\n\n".join([documents_prompts, footer_prompt])

        # step4: Retrieve the Answer
        answer = await self.generation_client.generate_text(
            user_prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.5
            )
        if not answer:
            logger.error(f"Error generating answer for RAG question answering for project {str(project.id)}")
            return None, full_prompt
        
        logger.info(f"RAG answer generated successfully for project {str(project.id)}")
        return answer, full_prompt