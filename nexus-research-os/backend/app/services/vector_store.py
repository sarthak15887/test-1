"""
Vector Store Service
Handles vector embeddings, indexing, and similarity search using Qdrant.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class VectorStoreService:
    """Service for managing vector embeddings and similarity search."""
    
    def __init__(
        self,
        embedding_model: str = "text-embedding-3-small",
        embedding_dimensions: int = 1536,
        collection_prefix: Optional[str] = None,
    ):
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.collection_prefix = collection_prefix or settings.QDRANT_COLLECTION_PREFIX
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=True,
        )
        
        # Initialize embeddings model
        self.embeddings: Embeddings = OpenAIEmbeddings(
            model=embedding_model,
            dimensions=embedding_dimensions,
        )
        
        # Cache for collection info
        self._collection_cache: Dict[str, bool] = {}
    
    def _get_collection_name(self, organization_id: UUID) -> str:
        """Generate collection name for organization."""
        return f"{self.collection_prefix}{str(organization_id).replace('-', '_')}"
    
    async def ensure_collection(self, organization_id: UUID) -> str:
        """Ensure collection exists for organization."""
        collection_name = self._get_collection_name(organization_id)
        
        # Check cache first
        if self._collection_cache.get(collection_name):
            return collection_name
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)
            
            if not collection_exists:
                # Create collection with HNSW index for fast similarity search
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimensions,
                        distance=Cosine,
                    ),
                    hnsw_config=models.HnswConfigDiff(
                        m=16,
                        ef_construct=100,
                    ),
                    optimizers_config=models.OptimizersConfigDiff(
                        default_segment_number=2,
                        max_segment_size=10_000_000,
                    ),
                )
                
                # Create payload indexes for filtering
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="document_id",
                    field_schema=models.KeywordIndexParams(type="keyword"),
                )
                
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="project_id",
                    field_schema=models.KeywordIndexParams(type="keyword"),
                )
                
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="chunk_index",
                    field_schema=models.IntegerIndexParams(type="integer"),
                )
                
                logger.info(f"Created collection: {collection_name}")
            
            self._collection_cache[collection_name] = True
            return collection_name
            
        except Exception as e:
            logger.error(f"Error ensuring collection {collection_name}: {str(e)}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            # Use batch processing for efficiency
            embeddings = await asyncio.to_thread(
                self.embeddings.embed_documents,
                texts,
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    async def index_chunks(
        self,
        organization_id: UUID,
        document_id: UUID,
        chunks: List[Dict[str, Any]],
        project_id: Optional[UUID] = None,
    ) -> int:
        """Index document chunks into vector store."""
        try:
            collection_name = await self.ensure_collection(organization_id)
            
            # Extract texts and generate embeddings
            texts = [chunk['content'] for chunk in chunks]
            embeddings = await self.embed_texts(texts)
            
            # Prepare points for upsert
            points = []
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = str(uuid4())
                
                # Build payload with metadata
                payload = {
                    "document_id": str(document_id),
                    "chunk_index": chunk.get('chunk_index', idx),
                    "content": chunk['content'],
                    "start_char": chunk.get('start_char'),
                    "end_char": chunk.get('end_char'),
                    **chunk.get('metadata', {}),
                }
                
                if project_id:
                    payload["project_id"] = str(project_id)
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
                points.append(point)
            
            # Upsert points in batches
            batch_size = 100
            total_upserted = 0
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                result = self.client.upsert(
                    collection_name=collection_name,
                    points=batch,
                    wait=True,
                )
                total_upserted += len(batch)
            
            logger.info(f"Indexed {total_upserted} chunks for document {document_id}")
            return total_upserted
            
        except Exception as e:
            logger.error(f"Error indexing chunks: {str(e)}")
            raise
    
    async def search_similarity(
        self,
        organization_id: UUID,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Perform similarity search with optional filters."""
        try:
            collection_name = await self.ensure_collection(organization_id)
            
            # Generate query embedding
            query_embedding = await self.embed_text(query)
            
            # Build filter if provided
            qdrant_filter = None
            if filters:
                conditions = []
                
                if 'document_id' in filters:
                    conditions.append(
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=str(filters['document_id'])),
                        )
                    )
                
                if 'project_id' in filters:
                    conditions.append(
                        FieldCondition(
                            key="project_id",
                            match=MatchValue(value=str(filters['project_id'])),
                        )
                    )
                
                if 'min_score' in filters:
                    conditions.append(
                        FieldCondition(
                            key="score",
                            range=Range(gte=filters['min_score']),
                        )
                    )
                
                if conditions:
                    qdrant_filter = Filter(must=conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                query_filter=qdrant_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get('content', ''),
                    "document_id": result.payload.get('document_id'),
                    "chunk_index": result.payload.get('chunk_index'),
                    "metadata": {
                        k: v for k, v in result.payload.items()
                        if k not in ['content', 'document_id', 'chunk_index']
                    },
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            raise
    
    async def delete_document_vectors(
        self,
        organization_id: UUID,
        document_id: UUID,
    ) -> int:
        """Delete all vectors for a specific document."""
        try:
            collection_name = await self.ensure_collection(organization_id)
            
            # Delete by filter
            result = self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="document_id",
                                match=MatchValue(value=str(document_id)),
                            )
                        ]
                    )
                ),
            )
            
            logger.info(f"Deleted vectors for document {document_id}")
            return result.status == 'completed'
            
        except Exception as e:
            logger.error(f"Error deleting document vectors: {str(e)}")
            raise
    
    async def get_collection_stats(self, organization_id: UUID) -> Dict[str, Any]:
        """Get statistics for organization's collection."""
        try:
            collection_name = self._get_collection_name(organization_id)
            
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)
            
            if not collection_exists:
                return {
                    "exists": False,
                    "vector_count": 0,
                    "indexed_documents": 0,
                }
            
            # Get collection info
            info = self.client.get_collection(collection_name)
            
            # Count unique documents
            # Note: This is approximate - Qdrant doesn't have direct count by payload
            return {
                "exists": True,
                "vector_count": info.points_count,
                "vectors_count": info.vectors_count,
                "segments_count": info.segments_count,
                "config": {
                    "embedding_model": self.embedding_model,
                    "dimensions": self.embedding_dimensions,
                },
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check if vector store is healthy."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False


# Singleton instance
_vector_store_service: Optional[VectorStoreService] = None


def get_vector_store_service() -> VectorStoreService:
    """Get or create vector store service singleton."""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    return _vector_store_service
