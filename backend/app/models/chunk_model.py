from .base_model import BaseModel
from  utils.enums import DatabaseEnums
from .db_schemas import Chunk, Project
from bson import ObjectId

from pymongo import InsertOne

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
    
    async def insert_chunks(self, chunks: list, batch_size:int=100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i+batch_size]  
            operation= [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch]
            await self.collection.bulk_write(operation)
        return len(chunks)
    
    
    async def get_project_chunks(self, project_id: str, page_no: int=1, page_size: int=50):
        records = await self.collection.find({
                    "chunk_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id
                }).skip((page_no-1) * page_size).limit(page_size).to_list(length=None)

        return [Chunk(**record)for record in records]
    
    
    async def get_paper_chunks(self, paper_id: str, page_no: int=1, page_size: int=50):
        records = await self.collection.find({
                    "chunk_paper_id": ObjectId(paper_id) if isinstance(paper_id, str) else paper_id
                }).skip(
                    (page_no-1) * page_size
                ).limit(page_size).to_list(length=None)

        return [Chunk(**record)for record in records]
    
    
    async def del_chunks_by_projectID(self, project_id: str):
        result = await self.collection.delete_many({
            "chunk_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id})
        return result.deleted_count
    
    
    async def del_chunks_by_paperID(self, project_id: ObjectId, paper_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id,
            "chunk_paper_id": ObjectId(paper_id) if isinstance(paper_id, str) else paper_id})
        return result.deleted_count
    



    

