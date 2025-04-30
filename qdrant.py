from qdrant_client import QdrantClient
import os 
qdrant_client = QdrantClient(
    url= os.environ["QDRANT_DB_URL"]  , 
    api_key=  os.environ["QDRANT_API_KEY"]
)
QDRANT_COLLECTION = 'financial_statement'

