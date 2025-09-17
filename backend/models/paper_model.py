from .base_model import BaseModel
from .db_schemas import Paper
from utils.enums import DatabaseEnums, AssetTypeEnums
from bson import ObjectId
from utils import get_logger
logger = get_logger(__name__)

class PaperModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.PAPER_COLLECTION_NAME.value]
    
    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        logger.info("PaperModel instance created and indexes ensured.")
        return instance
    
    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Paper.get_indexes())

    async def create_paper(self, paper: Paper) -> Paper:
        try:
            res = await self.collection.insert_one(paper.dict(by_alias=True, exclude_unset=True))
            paper.id = res.inserted_id
            logger.info(f"Paper created with ID: {paper.id} and name: {paper.paper_name}")
            return paper
        except Exception as e:
            logger.error(f"Error creating paper with ID: {paper.id} and name: {paper.paper_name}")
            raise

    async def get_paper_by_name(self, paper_project_id: ObjectId, paper_name: str):
        try:
            record = await self.collection.find_one(
                {"paper_project_id": paper_project_id,
                "paper_name": paper_name})
            if record is None:
                logger.warning(f"Paper not found: {paper_name} in project {paper_project_id}")
                return None
            logger.info(f"Paper found: {paper_name} in project {paper_project_id}")
            return Paper(**record)
        except Exception as e:
            logger.error(f"Error retrieving paper '{paper_name}' for project '{paper_project_id}'")
            raise

    async def get_or_create_paper(self, paper: Paper) -> Paper:
        try:
            paper = await self.get_paper_by_name(paper.paper_project_id, paper.paper_name)
            if not paper:
                paper = await self.create_paper(paper)
                return paper
            return paper
        except Exception as e:
            logger.error(f"Error in get_or_create_paper for {paper.paper_name}: {e}")
            raise
    
    async def get_paper_by_id(self, paper_project_id: str, paper_id: str):
        try:
            record = await self.collection.find_one(
                {"paper_project_id": ObjectId(paper_project_id),
                "_id": ObjectId(paper_id)}
            )
            if not record:
                logger.warning(f"Paper not found with ID: {paper_id} in project {paper_project_id}")
                return None
            return Paper(**record)
        except Exception as e:
            logger.error(f"Error retrieving paper by ID '{paper_id}' for project '{paper_project_id}'")
            raise

    async def get_papers_by_project(self, paper_project_id: str):
        try:    
            query = {"paper_project_id": ObjectId(paper_project_id)}
            records = await self.collection.find(query).to_list(length=None)
            papers = [Paper(**record) for record in records]
            if len(papers) == 0:
                logger.warning(f"No papers found for the project {paper_project_id}.")
                return []
            return papers
        except Exception as e:
            logger.error(f"Error fetching papers for project {paper_project_id}: {e}")
            raise
        
    async def delete_paper_by_project(self, paper_project_id:str, paper_id: str):
        try:
            result = await self.collection.delete_one(
                {"paper_project_id": ObjectId(paper_project_id),
                "_id": ObjectId(paper_id)}
            )
            if result.deleted_count == 0:
                logger.warning(f"Paper not found for deletion with ID: {paper_id} in project {paper_project_id}")
                return 0
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting paper {paper_id} from project {paper_project_id}: {e}")
            raise