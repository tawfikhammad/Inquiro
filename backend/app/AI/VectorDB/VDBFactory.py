from .providers import QdrantProvider
from utils import PathUtils
from .VDBEnums import VectorDBType

class VDBProviderFactory:
    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        db_path = PathUtils().get_vdb_path(db_name= self.config.VECTOR_DB_PATH)
        if provider == VectorDBType.QDRANT.value:
            qdrant_provider = QdrantProvider(db_path, self.config.VECTOR_DB_DISTANCE_METHOD)
            return qdrant_provider
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        