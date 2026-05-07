"""
Test configuration and fixtures.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
        "organization_id": "org123"
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Research Project",
        "description": "A test project for unit tests",
        "field": "biology"
    }


@pytest.fixture
def sample_agent_run_data():
    """Sample agent run data for testing."""
    return {
        "project_id": "proj123",
        "task_description": "Analyze protein structures",
        "config": {
            "max_iterations": 5,
            "agents": ["chief_scientist"]
        }
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "title": "Test Research Paper",
        "content": "This is a test document content.",
        "document_type": "paper",
        "metadata": {
            "authors": ["Test Author"],
            "year": 2024
        }
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock LLM response."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


@pytest.fixture
def sample_graph_data():
    """Sample knowledge graph data for testing."""
    return {
        "nodes": [
            {"id": "n1", "label": "Protein X", "type": "entity"},
            {"id": "n2", "label": "Binding", "type": "concept"},
            {"id": "n3", "label": "X-ray Crystallography", "type": "method"}
        ],
        "links": [
            {"source": "n1", "target": "n2", "relationship": "undergoes"},
            {"source": "n3", "target": "n1", "relationship": "analyzes"}
        ]
    }
