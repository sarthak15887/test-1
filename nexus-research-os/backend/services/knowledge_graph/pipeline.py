"""
Knowledge Graph Pipeline Service
Orchestrates document processing, entity extraction, and graph population
"""
from typing import List, Dict, Any, Optional
import logging
from backend.services.document_processor import get_document_processor
from backend.services.knowledge_graph.entity_extractor import get_entity_extraction_service
from backend.services.knowledge_graph.graph_service import get_knowledge_graph_service
from backend.models.database import get_db_session
from backend.models.document import Document

logger = logging.getLogger(__name__)

class KnowledgeGraphPipeline:
    def __init__(self):
        self.doc_processor = get_document_processor()
        self.entity_extractor = get_entity_extraction_service()
        self.graph_service = None  # Lazy initialization
        
    def _init_graph_service(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """Initialize Neo4j connection"""
        from backend.services.knowledge_graph.graph_service import get_knowledge_graph_service
        self.graph_service = get_knowledge_graph_service(neo4j_uri, neo4j_user, neo4j_password)
        
    async def process_document_to_graph(
        self, 
        document_id: int, 
        domain: str = "general",
        neo4j_uri: str = "bolt://neo4j:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password"
    ) -> Dict[str, Any]:
        """Process a document and populate knowledge graph"""
        
        try:
            # Initialize graph service if needed
            if not self.graph_service:
                self._init_graph_service(neo4j_uri, neo4j_user, neo4j_password)
                
            # Get document from database
            db = next(get_db_session())
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return {"success": False, "error": "Document not found"}
                
            logger.info(f"Processing document {document_id}: {document.title}")
            
            # Parse document into chunks
            chunks = await self.doc_processor.parse_and_chunk(
                file_path=document.file_path,
                chunk_size=1000,
                chunk_overlap=200
            )
            
            logger.info(f"Extracted {len(chunks)} chunks from document")
            
            # Extract entities and relationships
            extracted_knowledge = self.entity_extractor.extract_from_document_chunks(
                chunks=chunks,
                domain=domain
            )
            
            logger.info(f"Extracted {len(extracted_knowledge.entities)} entities and "
                       f"{len(extracted_knowledge.relationships)} relationships")
            
            # Populate knowledge graph
            entities_created = 0
            for entity in extracted_knowledge.entities:
                if self.graph_service.create_entity(entity):
                    entities_created += 1
                    
            relationships_created = 0
            for relationship in extracted_knowledge.relationships:
                if self.graph_service.create_relationship(relationship):
                    relationships_created += 1
                    
            # Create fulltext index if not exists
            self.graph_service.create_fulltext_index()
            
            # Update document status
            document.status = "processed"
            document.metadata = document.metadata or {}
            document.metadata["entities_count"] = entities_created
            document.metadata["relationships_count"] = relationships_created
            db.commit()
            
            return {
                "success": True,
                "document_id": document_id,
                "entities_created": entities_created,
                "relationships_created": relationships_created,
                "chunks_processed": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing document to graph: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()
            
    async def search_knowledge_graph(
        self, 
        query: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search the knowledge graph"""
        if not self.graph_service:
            raise ValueError("Graph service not initialized")
            
        return self.graph_service.search_graph(query, limit)
        
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        if not self.graph_service:
            return {"error": "Graph service not initialized"}
            
        return self.graph_service.get_graph_stats()

# Singleton instance
_pipeline = None

def get_knowledge_graph_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = KnowledgeGraphPipeline()
    return _pipeline
