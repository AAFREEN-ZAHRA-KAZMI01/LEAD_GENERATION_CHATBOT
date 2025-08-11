import pandas as pd
from config import Config
from qdrant_client.models import PointStruct
from .qdrant_connector import QdrantConnector
from  .utils.embeddings import get_embedding

class DataLoader:
    def __init__(self):
        self.qdrant = QdrantConnector()
    
    def load_property_data(self):
        df = pd.read_csv(Config.PROPERTY_DATA_PATH)
        df.fillna("", inplace=True)
        
        # Create collection if not exists
        try:
            self.qdrant.create_collection(vector_size=1536)  # OpenAI embedding size
        except Exception as e:
            print(f"Collection already exists or error: {e}")
        
        # Prepare points for Qdrant
        points = []
        for idx, row in df.iterrows():
            # Combine relevant fields for embedding
            text_to_embed = f"{row['title']} {row['type']} {row['location']} {row['description']}"
            
            points.append(
                PointStruct(
                    id=idx,
                    vector=get_embedding(text_to_embed),
                    payload={
                        "id": row['id'],
                        "title": row['title'],
                        "price": row['price'],
                        "type": row['type'],
                        "bedrooms": row['bedrooms'],
                        "area": row['area'],
                        "location": row['location'],
                        "sector": row['sector'],
                        "features": row['features'],
                        "contact": row['contact'],
                        "description": row['description']
                    }
                )
            )
        
        # Upload to Qdrant
        self.qdrant.client.upsert(
            collection_name=Config.QDRANT_COLLECTION,
            points=points
        )
        
        return df