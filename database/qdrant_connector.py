from qdrant_client import QdrantClient
from config import Config

class QdrantConnector:
    def __init__(self):
        self.client = QdrantClient(
            host=Config.QDRANT_HOST,
            port=Config.QDRANT_PORT
        )
        self.collection_name = Config.QDRANT_COLLECTION
    
    def search_properties(self, query_embedding, limit=5, filters=None):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=filters,
            limit=limit
        )
    
    def create_collection(self, vector_size):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config={
                "size": vector_size,
                "distance": "Cosine"
            }
        )