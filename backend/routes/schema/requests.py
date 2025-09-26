from pydantic import BaseModel
from typing import List, Optional

class ProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0

class ProjectRequest(BaseModel):
    project_title: str

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    RAGFusion: Optional[bool] = False