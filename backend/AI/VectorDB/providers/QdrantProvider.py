from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from ..VDBInterface import VectorDBInterface
from models.db_schemas import RetrievedDocument
from typing import List
import uuid
from utils.app_logging import get_logger
logger = get_logger(__name__)

class QdrantProvider(VectorDBInterface):
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 grpc_port: int = 6334, distance_metric: str="cosine"):
        self.host = host
        self.port = port
        self.grpc_port = grpc_port
        self.distance_metric = None
        self.client = None

        if distance_metric == "cosine":
            self.distance_metric = models.Distance.COSINE
        elif distance_metric == "dot":
            self.distance_metric = models.Distance.DOT

    async def connect(self):
        self.client = AsyncQdrantClient(
                host=self.host,
                port=self.port,
                prefer_grpc=False,  # Use HTTP instead of gRPC
        )
        logger.info("Connected to Qdrant database.")

    async def disconnect(self):
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Qdrant database.")

    async def is_collection_exist(self, collection_name):
        return await self.client.collection_exists(collection_name)

    async def list_all_collections(self):
        return await self.client.get_collections()

    async def get_collection_info(self, collection_name):
        if await self.client.collection_exists(collection_name):
            return await self.client.get_collection(collection_name=collection_name)
        else:
            logger.warning(f"Collection '{collection_name}' does not exist.")
            return None

    async def delete_collection(self, collection_name):
        if await self.client.collection_exists(collection_name):
            await self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted.")
        else:
            logger.warning(f"Collection '{collection_name}' does not exist.")

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            _ = await self.delete_collection(collection_name)

        if not await self.client.collection_exists(collection_name):
            _ = await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_metric
                )
            )
            logger.info(f"Collection '{collection_name}' created.")
        else:
            logger.warning(f"Collection '{collection_name}' already exists.")

    async def insert_one(self, collection_name:str, text:str, vector:list, record_id:int = None):

        if await self.client.collection_exists(collection_name):
            try:
                await self.client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                        id= record_id,
                        vector= vector, 
                        payload= {"text": text}
                )])
                logger.info(f"Inserted one document into collection '{collection_name}'.")

            except Exception as e:
                logger.error(f"Error inserting document into collection '{collection_name}': {e}")
                return False
        else:
            logger.warning(f"Collection '{collection_name}' does not exist. Cannot insert document.")

    async def insert_many(self, collection_name:str, texts:list, vectors:list,
                record_ids:list = None, batch_size:int = 50):

        if not await self.client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist.")
            return False

        record_ids = record_ids or [str(uuid.uuid4()) for _ in range(len(texts))]
        try:
            for i in range(0, len(texts), batch_size):
                batch_points = []
                for j in range(i, min(i + batch_size, len(texts))):
                    payload = {"text": texts[j]}

                    point = models.PointStruct(
                        id=record_ids[j],
                        vector=vectors[j],
                        payload=payload)

                    batch_points.append(point)

                await self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points
                )

                logger.info(f"Inserted batch {i} to {i + len(batch_points)} into collection '{collection_name}'")

            return True

        except Exception as e:
            logger.error(f"Error inserting into collection '{collection_name}': {e}")
            return False 

    async def search(self, collection_name:str, query_vector:list, limit:int = 5):
        try:
            search_result = await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )

            if not search_result or len(search_result) == 0:
                logger.warning(f"No results found in collection '{collection_name}'.")
                return None

            retrieved_result = [
                RetrievedDocument(**{
                            "score": result.score,
                            "text": result.payload["text"],
                        }
                    )
                for result in search_result
            ]

            logger.info(f"Search completed in collection '{collection_name}'.")
            return retrieved_result

        except Exception as e:
            logger.error(f"Error searching in collection '{collection_name}': {e}")
            return None