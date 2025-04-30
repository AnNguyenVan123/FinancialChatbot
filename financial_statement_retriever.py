import os
import json
import logging
from typing import List, Optional
from io import BytesIO

from aws_db import s3_client
from qdrant import qdrant_client
from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain_core.retrievers import BaseRetriever
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QDRANT_COLLECTION = "financial_statement"
S3_BUCKET = "financial-data-chatbot"

# Initialize embedding model
try:
    EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    raise RuntimeError(f"Failed to load embedding model: {e}")

# Verify Qdrant collection
try:
    collection_info = qdrant_client.get_collection(QDRANT_COLLECTION)
    if not collection_info:
        raise ValueError(f"Collection '{QDRANT_COLLECTION}' is not accessible")
except Exception as e:
    logger.error(f"Collection '{QDRANT_COLLECTION}' verification failed: {e}")
    raise ValueError(f"Collection '{QDRANT_COLLECTION}' does not exist or is inaccessible: {e}")


def fetch_s3_document(s3_key: str) -> Optional[str]:
    """Fetch and parse JSON document from S3."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        file_content = response["Body"].read()

        if not s3_key.endswith(".json"):
            logger.warning(f"Unsupported file format: {s3_key}")
            return None

        json_data = json.loads(file_content.decode("utf-8"))
        return json.dumps(json_data, ensure_ascii=False, indent=2)

    except ClientError as e:
        logger.error(f"Failed to fetch S3 document {s3_key}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in S3 document {s3_key}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing S3 document {s3_key}: {e}")
        return None


class QdrantS3Retriever(BaseRetriever, BaseModel):
    """Custom retriever for Qdrant and S3 integration."""
    embedding: HuggingFaceEmbeddings = Field(...)
    s3_bucket: str = Field(...)
    k: int = 5

    class Config:
        arbitrary_types_allowed = True  # Allow non-Pydantic types like HuggingFaceEmbeddings

    def _get_relevant_documents(self, query: str) -> List[Document]:
        try:
            # Generate query embedding
            query_embedding = self.embedding.embed_query(query)

            # Query Qdrant
            results = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION,
                query=query_embedding,
                limit=self.k,
                with_payload=True,
                with_vectors=False
            ).points

            documents = []
            for result in results:
                payload = result.payload or {}
                s3_key = payload.get("s3_key")

                if not s3_key:
                    logger.warning(f"No s3_key in payload: {payload}")
                    continue

                content = fetch_s3_document(s3_key)
                if content:
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "s3_key": s3_key,
                            "score": getattr(result, "score", None),
                            **payload
                        }
                    ))
                else:
                    logger.warning(f"Failed to fetch content for s3_key: {s3_key}")

            return documents

        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []


# Create retriever instance
retriever = QdrantS3Retriever(
    embedding=EMBEDDING_MODEL,
    s3_bucket=S3_BUCKET,
    k=5
)

