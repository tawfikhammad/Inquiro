from pydantic import BaseModel, Field, validator
from typing import List, Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_title: str = Field(..., min_length=1)

    @validator('project_title')
    def project_id_validator(cls, v):
        if not v.isalnum():
            raise ValueError('Project ID must be alphanumeric')
        return v
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_title", 1)],
                "name": "project_title_index_1",
                "unique": True
            }
        ]
        
