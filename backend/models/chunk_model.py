from pymongo import InsertOne
from .base_model import BaseModel
from .db_schemas import Chunk, Project
from bson import ObjectId
from typing import List
from utils.enums import DatabaseEnums
from utils import get_logger
logger = get_logger(__name__)


class ChunkModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnums.CHUNK_COLLECTION_NAME.value]

    @classmethod
    async def get_instance(cls, db_client):
        instance = cls(db_client)
        await instance.ensure_indexes()
        return instance
    
    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Chunk.get_indexes())

    async def create_chunk(self, chunk: Chunk):
        res = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = res.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        record = await self.collection.find_one({"_id": chunk_id})
        if record is None:
            return None
        return Chunk(**record)
    
    async def insert_chunks(self, chunks: List[Chunk], batch_size: int=100):
        try:
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i: i+batch_size]  
                operation= [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch]
                await self.collection.bulk_write(operation)
            logger.info(f"Inserted {len(chunks)} chunks into the database.")
            return len(chunks)
        except Exception as e:
            logger.error(f"Error inserting chunks")
            raise
    
    async def get_project_chunks(self, Chunks_project_id: str, page_no: int=1, page_size: int=50):
        try:
            records = await self.collection.find({
                "chunk_project_id": ObjectId(Chunks_project_id)
                }
            ).skip((page_no-1) * page_size).limit(page_size).to_list(length=None)
            if not records or len(records) == 0:
                logger.info(f"No chunks found for project {Chunks_project_id} on page {page_no}")
                return []

            return [Chunk(**record)for record in records]
        except Exception as e:
            logger.error(f"Error fetching chunks for project {Chunks_project_id}")
            raise


    async def get_paper_chunks(self, chunks_paper_id: str, page_no: int=1, page_size: int=50):
        try:
            records = await self.collection.find({
                        "chunk_paper_id": ObjectId(chunks_paper_id) if isinstance(chunks_paper_id, str) else chunks_paper_id
                }).skip(
                    (page_no-1) * page_size
                ).limit(page_size).to_list(length=None)

            return [Chunk(**record)for record in records]
        except Exception as e:
            logger.error(f"Error fetching chunks for paper {chunks_paper_id}")
            raise

    async def delete_chunks_by_project(self, chunks_project_id: str):
        try:
            result = await self.collection.delete_many({
                "chunk_project_id": ObjectId(chunks_project_id)})
            if result.deleted_count == 0:
                logger.warning(f"No chunks found for deletion for project {chunks_project_id}")
                return 0
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting chunks for project {chunks_project_id}")
            raise

    async def delete_chunks_by_paper(self, chunks_project_id: str, chunks_paper_id: str):
        try:
            result = await self.collection.delete_many({
                "chunk_project_id": ObjectId(chunks_project_id),
                "chunk_paper_id": ObjectId(chunks_paper_id)})
            if result.deleted_count == 0:
                logger.warning(f"No chunks found for deletion for paper {chunks_paper_id} in project {chunks_project_id}")
                return 0
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting chunks for paper {chunks_paper_id} in project {chunks_project_id}")
            raise
    



    

