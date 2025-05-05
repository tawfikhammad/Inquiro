from .base_model import BaseModel
from .db_schemas import Paper, Project
from utils.enums import DatabaseEnums, AssetTypeEnums
from bson import ObjectId


class PaperModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.PAPER_COLLECTION_NAME.value]
    
    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        return instance
    
    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Paper.get_indexes())

    async def create_paper(self, paper: Paper):
        res = await self.collection.insert_one(paper.dict(by_alias=True, exclude_unset=True))
        paper.id = res.inserted_id
        return paper
    
    async def get_paper_by_project(self, paper_project_id: str, paper_id: str):
        record = await self.collection.find_one(
            {"paper_project_id": ObjectId(paper_project_id) if isinstance(paper_project_id, str) else paper_project_id,
            "paper_id": paper_id})
        if record is None:
            return None
        return Paper(**record)
    
    async def get_papers_by_project(self, paper_project_id:str, paper_type:str = AssetTypeEnums.PDF.value):
        records = await self.collection.find(
            {"paper_project_id": ObjectId(paper_project_id) if isinstance(paper_project_id, str) else paper_project_id, 
            "paper_type": paper_type
             }).to_list(length=None)
        if records is None:
            return None
        papers = [Paper(**record) for record in records]
        return papers
    
    async def delete_paper_by_project(self, paper_project_id:str, paper_id: str):
        result = await self.collection.delete_one(
            {"paper_project_id": ObjectId(paper_project_id) if isinstance(paper_project_id, str) else paper_project_id,
             "paper_id": paper_id})
        return result.deleted_count > 0