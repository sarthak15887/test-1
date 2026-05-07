"""
Knowledge Graph API Routes
Endpoints for knowledge graph operations
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.services.knowledge_graph.pipeline import get_knowledge_graph_pipeline
from backend.models.database import get_db_session
from backend.auth.dependencies import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])

class ProcessDocumentRequest(BaseModel):
    document_id: int
    domain: str = "general"
    
class SearchRequest(BaseModel):
    query: str
    limit: int = 50
    
@router.post("/process-document")
async def process_document_to_graph(
    request: ProcessDocumentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Process a document and extract knowledge graph"""
    pipeline = get_knowledge_graph_pipeline()
    
    # Start processing in background
    background_tasks.add_task(
        pipeline.process_document_to_graph,
        document_id=request.document_id,
        domain=request.domain
    )
    
    return {
        "message": "Document processing started",
        "document_id": request.document_id,
        "domain": request.domain
    }

@router.post("/search")
async def search_knowledge_graph(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search the knowledge graph"""
    pipeline = get_knowledge_graph_pipeline()
    
    try:
        results = await pipeline.search_knowledge_graph(
            query=request.query,
            limit=request.limit
        )
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stats")
async def get_graph_stats(
    current_user: User = Depends(get_current_user)
):
    """Get knowledge graph statistics"""
    pipeline = get_knowledge_graph_pipeline()
    
    stats = pipeline.get_graph_statistics()
    
    return stats

@router.get("/entities/{entity_id}")
async def get_entity(
    entity_id: str,
    depth: int = 2,
    current_user: User = Depends(get_current_user)
):
    """Get entity and its relationships"""
    pipeline = get_knowledge_graph_pipeline()
    
    if not pipeline.graph_service:
        raise HTTPException(status_code=500, detail="Graph service not initialized")
        
    result = pipeline.graph_service.find_related_entities(entity_id, depth)
    
    return result

@router.get("/entities/label/{label}")
async def get_entities_by_label(
    label: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get entities by label"""
    pipeline = get_knowledge_graph_pipeline()
    
    if not pipeline.graph_service:
        raise HTTPException(status_code=500, detail="Graph service not initialized")
        
    entities = pipeline.graph_service.find_entities_by_label(label, limit)
    
    return {
        "label": label,
        "entities": [
            {
                "id": e.id,
                "label": e.label,
                "properties": e.properties
            }
            for e in entities
        ],
        "count": len(entities)
    }
