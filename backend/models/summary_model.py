from .base_model import BaseModel
from .db_schemas import Summary
from bson import ObjectId
from utils.enums import DatabaseEnums
from utils import get_logger
logger = get_logger(__name__)

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
        try:
            res = await self.collection.insert_one(summary.dict(by_alias=True, exclude_unset=True))
            summary.id = res.inserted_id
            logger.info(f"Summary created with ID: {summary.id} and name {summary.summary_name}")
            return summary
        except Exception as e:
            logger.error(f"Error creating summary with ID: {summary.id} and name {summary.summary_name}: {e}")
            raise

    async def get_summary_by_name(self, summary_project_id: str, summary_name: str):
        try:
            record = await self.collection.find_one(
                {"summary_project_id": summary_project_id,
                "summary_name": summary_name})
            if record is None:
                logger.warning(f"Summary not found: {summary_name} in project {summary_project_id}")
                return None
            logger.info(f"Summary found: {summary_name} in project {summary_project_id}")
            return Summary(**record)
        except Exception as e:
            logger.error(f"Error retrieving summary '{summary_name}' for project '{summary_project_id}': {e}")
            raise

    async def get_or_create_summary(self, summary: Summary) -> Summary:
        try:
            summary = await self.get_summary_by_name(summary.summary_project_id, summary.summary_name)
            if not summary:
                summary = await self.create_summary(summary)
                return summary
            return summary
        except Exception as e:
            logger.error(f"Error in get_or_create_summary for {summary.summary_name}: {e}")
            raise
    
    async def update_summary(self, summary: Summary):
        try:
            result = await self.collection.update_one(
                {"_id": summary.id},
                {"$set": summary.dict(by_alias=True, exclude={"id"}, exclude_unset=True)}
            )
            if result.modified_count == 0:  
                logger.info(f"Summary {summary.id} matched but no fields were changed.")

            logger.info(f"Summary {summary.id} updated successfully for paper {summary.summary_paper_id}.")
        except Exception as e:
            logger.error(f"Error updating summary in DB: {e}")
            raise
    
    async def get_summary_by_project(self, summary_project_id: str, summary_id: str):
        try:
            record = await self.collection.find_one(
                {"summary_project_id": ObjectId(summary_project_id),
                "_id": ObjectId(summary_id)}
            )
            if not record:
                logger.warning(f"Summary '{summary_id}' not found for project '{summary_project_id}'")
                return None
            return Summary(**record)
        except Exception as e:
            logger.error(f"Error retrieving summary '{summary_id}' for project '{summary_project_id}': {e}")
            raise

    async def get_summaries_by_project(self, summaries_project_id: str, summary_type: str = None):
        try:    
            query = {"summary_project_id": summaries_project_id}
            if summary_type:
                query["summary_type"] = summary_type
                
            records = await self.collection.find(query).to_list(length=None)
            if not records:
                logger.warning(f"No summaries found for project '{summaries_project_id}'")
                return []
            summaries = [Summary(**record) for record in records]
            return summaries
        except Exception as e:
            logger.error(f"Error retrieving summaries for project '{summaries_project_id}' : {e}")
            raise
    
    async def delete_summary_by_project(self, summary_project_id: str, summary_id: str):
        try:
            result = await self.collection.delete_one(
                {"summary_project_id": ObjectId(summary_project_id),
                "_id": ObjectId(summary_id)}
            )
            if result.deleted_count == 0:
                logger.warning(f"Summary not found for deletion with ID: {summary_id} in project {summary_project_id}")
                return 0
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting summary {summary_id} from project {summary_project_id}: {e}")
            raise