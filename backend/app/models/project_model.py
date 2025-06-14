from .base_model import BaseModel
from .db_schemas import Project
from utils.enums import DatabaseEnums
from bson import ObjectId

class ProjectModel(BaseModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.PROJECT_COLLECTION_NAME.value]

    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        return instance

    async def ensure_indexes(self):
        await self.create_indexes(self.collection, Project.get_indexes())

    async def create_project(self, project_title: str):
        project = Project(project_title=project_title)
        res= await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project.id = res.inserted_id
        return project
    
    async def get_or_create_project(self, project_title: str):
        """
        Get a project by its project_id and if the project does not exist, create one
        """
        record = await self.collection.find_one({"project_title": project_title})
        if record is None:
            project = Project(project_title=project_title)
            project = await self.create_project(project)
            return project
        return Project(**record)
    
    async def get_all_projects(self, page: int=0, limit: int=10):
        """
        return all projects in the database with pagination support starting from page 0 with a limit of 10
        """
        cursor = self.collection.find().skip(page * limit).limit(limit)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects
    
    async def get_project_by_id(self, project_id: str):
        record = await self.collection.find_one({"_id": ObjectId(project_id)})
        if record is None:
            return None
        return Project(**record)
    
    async def delete_all_projects(self):
        """Delete all projects from the collection"""
        result = await self.collection.delete_many({})
        return result.deleted_count
    
    async def delete_project(self, project_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(project_id)})
        if result.deleted_count == 0:
            return None
        return result.deleted_count

