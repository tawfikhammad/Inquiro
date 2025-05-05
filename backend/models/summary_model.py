from .base_model import BaseModel
from .db_schemas import Summary
from utils.enums import DatabaseEnums
from bson import ObjectId


class SummaryModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.SUMMARY_COLLECTION_NAME.value]
    
    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        return instance
    
    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Summary.get_indexes())

    async def create_summary(self, summary: Summary):
        res = await self.collection.insert_one(summary.dict(by_alias=True, exclude_unset=True))
        summary.id = res.inserted_id
        return summary
    
    async def get_summary_by_project(self, summary_project_id: str, summary_id: str):
        record = await self.collection.find_one(
            {"summary_project_id": ObjectId(summary_project_id) if isinstance(summary_project_id, str) else summary_project_id,
            "summary_id": summary_id})
        if record is None:
            return None
        return Summary(**record)
    
    async def get_summaries_by_project(self, summary_project_id: str, summary_type: str):
        records = await self.collection.find(
            {"summary_project_id": ObjectId(summary_project_id) if isinstance(summary_project_id, str) else summary_project_id, 
            "summary_type": summary_type
             }).to_list(length=None)
        if records is None:
            return None
        summaries = [Summary(**record) for record in records]
        return summaries
    
    async def delete_summary_by_project(self, project_summary_id: str, summary_id: str):
        result = await self.collection.delete_one(
            {"summary_project_id": ObjectId(project_summary_id) if isinstance(project_summary_id, str) else project_summary_id,
             "summary_id": summary_id})
        return result.deleted_count > 0