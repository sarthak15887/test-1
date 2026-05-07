"""
Entity Extraction Service
Extracts entities and relationships from text using LLM
"""
from typing import List, Dict, Any, Tuple
import json
import re
from dataclasses import dataclass
from backend.services.llm_service import get_llm_service
from backend.services.knowledge_graph.graph_service import Entity, Relationship

@dataclass
class ExtractedKnowledge:
    entities: List[Entity]
    relationships: List[Relationship]

class EntityExtractionService:
    def __init__(self, llm_service=None):
        self.llm_service = llm_service or get_llm_service()
        
    def extract_entities_and_relationships(self, text: str, domain: str = "general") -> ExtractedKnowledge:
        """Extract entities and relationships from text using LLM"""
        
        prompt = f"""
You are an expert knowledge graph builder for scientific research. 
Extract entities and relationships from the following text in the {domain} domain.

Guidelines:
1. Identify key scientific entities (concepts, methods, materials, organisms, chemicals, etc.)
2. Determine relationships between entities (uses, produces, affects, studies, etc.)
3. Be precise and specific with entity labels
4. Include relevant properties for each entity

Text to analyze:
{text}

Return ONLY a valid JSON object with this exact structure:
{{
  "entities": [
    {{"id": "unique_id_1", "label": "EntityType", "properties": {{"name": "Entity Name", "description": "Brief description"}}},
    ...
  ],
  "relationships": [
    {{"start_node": "entity_id_1", "end_node": "entity_id_2", "type": "RELATIONSHIP_TYPE", "properties": {{"description": "Relationship description"}}},
    ...
  ]
}}

Ensure all relationship start_node and end_node values correspond to entity ids.
"""

        try:
            response = self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4-turbo-preview",
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if not json_match:
                raise ValueError("No valid JSON found in response")
                
            result = json.loads(json_match.group())
            
            # Convert to data classes
            entities = [
                Entity(
                    id=e["id"],
                    label=e["label"],
                    properties=e.get("properties", {})
                )
                for e in result.get("entities", [])
            ]
            
            relationships = [
                Relationship(
                    start_node=r["start_node"],
                    end_node=r["end_node"],
                    type=r["type"],
                    properties=r.get("properties", {})
                )
                for r in result.get("relationships", [])
            ]
            
            return ExtractedKnowledge(entities=entities, relationships=relationships)
            
        except Exception as e:
            print(f"Error extracting knowledge: {e}")
            return ExtractedKnowledge(entities=[], relationships=[])
            
    def extract_from_document_chunks(self, chunks: List[str], domain: str = "general") -> ExtractedKnowledge:
        """Extract knowledge from multiple document chunks"""
        all_entities = []
        all_relationships = []
        seen_entity_ids = set()
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            extracted = self.extract_entities_and_relationships(chunk, domain)
            
            # Deduplicate entities by ID
            for entity in extracted.entities:
                if entity.id not in seen_entity_ids:
                    all_entities.append(entity)
                    seen_entity_ids.add(entity.id)
                    
            all_relationships.extend(extracted.relationships)
            
        return ExtractedKnowledge(entities=all_entities, relationships=all_relationships)

# Singleton instance
_extraction_service = None

def get_entity_extraction_service():
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = EntityExtractionService()
    return _extraction_service
