from abc import ABC, abstractmethod

class VDBInterface(ABC):

    @abstractmethod
    def connect(self):
        """Connect to the VDB."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the VDB."""
        pass

    @abstractmethod
    def create_collection(self, collection_name):
        """Create a collection in the VDB."""
        pass

    @abstractmethod
    def is_collection(self, collection_name):
        """Check if a collection exists in the VDB."""
        pass

    @abstractmethod
    def delete_collection(self, query):
        pass

    @abstractmethod
    def get_all_collections(self):
        """Get all collections in the VDB."""
        pass

    @abstractmethod
    def get_collection_info(self, collection_name):
        """Get information about a specific collection in the VDB."""
        pass

    @abstractmethod
    def insert_one(self, data):
        """Insert a single document into the VDB."""
        pass

    @abstractmethod
    def insert_many(self, data):
        """Insert multiple documents into the VDB."""
        pass

    @abstractmethod
    def search(self, query, top_k=5):
        """Search for similar documents in the VDB."""
        pass