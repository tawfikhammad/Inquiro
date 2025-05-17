from pydantic import BaseModel, Field
from typing import List, Optional
from bson.objectid import ObjectId

class Chunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_project_id: ObjectId
    chunk_paper_id: ObjectId
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_id: int = Field(..., ge=0)
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
            ,
            {
                "key": [("chunk_paper_id", 1)],
                "name": "chunk_paper_id_index_1",
                "unique": False
            }
        ]