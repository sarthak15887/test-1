"""
Knowledge Graph Service - Neo4j Integration
Handles entity extraction, relationship mapping, and graph queries
"""
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    id: str
    label: str
    properties: Dict[str, Any]
    
@dataclass
class Relationship:
    start_node: str
    end_node: str
    type: str
    properties: Dict[str, Any]

class KnowledgeGraphService:
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._verify_connectivity()
        
    def _verify_connectivity(self):
        try:
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
            
    def close(self):
        self.driver.close()
        
    def create_entity(self, entity: Entity) -> bool:
        """Create a node in the knowledge graph"""
        query = """
        MERGE (n:Entity {id: $id})
        SET n.label = $label, n += $properties
        RETURN n
        """
        try:
            with self.driver.session() as session:
                session.run(query, 
                          id=entity.id, 
                          label=entity.label, 
                          properties=entity.properties)
            logger.info(f"Created entity: {entity.id}")
            return True
        except Exception as e:
            logger.error(f"Error creating entity: {e}")
            return False
            
    def create_relationship(self, relationship: Relationship) -> bool:
        """Create a relationship between two nodes"""
        query = """
        MATCH (a:Entity {id: $start_id})
        MATCH (b:Entity {id: $end_id})
        MERGE (a)-[r:RELATIONSHIP {type: $type}]->(b)
        SET r += $properties
        RETURN r
        """
        try:
            with self.driver.session() as session:
                session.run(query,
                          start_id=relationship.start_node,
                          end_id=relationship.end_node,
                          type=relationship.type,
                          properties=relationship.properties)
            logger.info(f"Created relationship: {relationship.start_node}-[{relationship.type}]->{relationship.end_node}")
            return True
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False
            
    def find_entities_by_label(self, label: str, limit: int = 100) -> List[Entity]:
        """Find entities by their label"""
        query = """
        MATCH (n:Entity {label: $label})
        RETURN n
        LIMIT $limit
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, label=label, limit=limit)
                entities = []
                for record in result:
                    node = record["n"]
                    entities.append(Entity(
                        id=node["id"],
                        label=node["label"],
                        properties={k: v for k, v in node.items() if k not in ['id', 'label']}
                    ))
                return entities
        except Exception as e:
            logger.error(f"Error finding entities: {e}")
            return []
            
    def find_related_entities(self, entity_id: str, depth: int = 2) -> Dict[str, Any]:
        """Find entities related to a given entity up to specified depth"""
        query = """
        MATCH (start:Entity {id: $start_id})
        OPTIONAL MATCH path = (start)-[*1..$depth]-(related)
        WHERE related <> start
        RETURN start, collect(DISTINCT related) as related_nodes, 
               collect(DISTINCT relationships(path)) as relationships
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, start_id=entity_id, depth=depth)
                record = result.single()
                if not record:
                    return {"nodes": [], "relationships": []}
                    
                nodes = [record["start"]] + record["related_nodes"]
                entity_list = []
                for node in nodes:
                    if node:
                        entity_list.append({
                            "id": node["id"],
                            "label": node["label"],
                            "properties": {k: v for k, v in node.items() if k not in ['id', 'label']}
                        })
                        
                return {"nodes": entity_list, "relationships": []}
        except Exception as e:
            logger.error(f"Error finding related entities: {e}")
            return {"nodes": [], "relationships": []}
            
    def search_graph(self, query_text: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Full-text search across entity properties"""
        query = """
        CALL db.index.fulltext.queryNodes('entity_fulltext', $query_text)
        YIELD node, score
        RETURN node, score
        LIMIT $limit
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, query_text=query_text, limit=limit)
                results = []
                for record in result:
                    node = record["node"]
                    results.append({
                        "id": node["id"],
                        "label": node["label"],
                        "score": record["score"],
                        "properties": {k: v for k, v in node.items() if k not in ['id', 'label']}
                    })
                return results
        except Exception as e:
            logger.error(f"Error searching graph: {e}")
            return []
            
    def create_fulltext_index(self):
        """Create full-text index for entity search"""
        query = """
        CREATE FULLTEXT INDEX entity_fulltext 
        FOR (n:Entity) 
        ON EACH [n.label, n.name, n.description]
        """
        try:
            with self.driver.session() as session:
                session.run(query)
            logger.info("Created full-text index for entities")
        except Exception as e:
            logger.warning(f"Full-text index may already exist: {e}")
            
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        queries = {
            "node_count": "MATCH (n) RETURN count(n) as count",
            "relationship_count": "MATCH ()-[r]->() RETURN count(r) as count",
            "label_counts": "MATCH (n) RETURN labels(n) as labels, count(n) as count",
            "relationship_types": "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count"
        }
        
        stats = {}
        try:
            with self.driver.session() as session:
                for key, query in queries.items():
                    result = session.run(query)
                    if key in ["node_count", "relationship_count"]:
                        stats[key] = result.single()[0] if result.single() else 0
                    else:
                        stats[key] = [{"labels": record[0], "count": record[1]} for record in result]
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            
        return stats

# Singleton instance
_kg_service: Optional[KnowledgeGraphService] = None

def get_knowledge_graph_service(uri: str, user: str, password: str) -> KnowledgeGraphService:
    global _kg_service
    if _kg_service is None:
        _kg_service = KnowledgeGraphService(uri, user, password)
    return _kg_service
