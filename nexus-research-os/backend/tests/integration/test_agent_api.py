"""
Integration tests for Agent API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAgentRunsAPI:
    @pytest.fixture
    def auth_headers(self):
        # First, we need to create a test user and get a token
        # For integration tests, we'll use a mock approach
        
        # Create test user
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
        try:
            response = client.post("/api/v1/auth/register", json=user_data)
            if response.status_code == 400:
                # User might already exist, try logging in
                login_response = client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com",
                        "password": "TestPass123!"
                    }
                )
                return {"Authorization": f"Bearer {login_response.json()['access_token']}"}
            
            return {"Authorization": f"Bearer {response.json()['access_token']}"}
        except Exception:
            # Skip auth for now in integration tests
            return {}

    def test_create_agent_run_unauthorized(self):
        """Test that creating a run requires authentication."""
        run_data = {
            "project_id": "proj123",
            "task_description": "Analyze protein structures"
        }
        
        response = client.post("/api/v1/agent-runs/", json=run_data)
        assert response.status_code == 401

    def test_list_agent_runs_unauthorized(self):
        """Test that listing runs requires authentication."""
        response = client.get("/api/v1/agent-runs/")
        assert response.status_code == 401

    @pytest.mark.skip(reason="Requires full auth setup")
    def test_create_agent_run(self, auth_headers):
        """Test creating a new agent run."""
        run_data = {
            "project_id": "proj123",
            "task_description": "Analyze protein folding patterns",
            "config": {
                "max_iterations": 10,
                "agents": ["chief_scientist", "data_analyst"]
            }
        }
        
        response = client.post(
            "/api/v1/agent-runs/",
            json=run_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] in ["pending", "running"]
        assert data["message"] == "Agent run started successfully"

    @pytest.mark.skip(reason="Requires full auth setup")
    def test_get_agent_run(self, auth_headers):
        """Test getting agent run details."""
        # First create a run
        run_data = {
            "project_id": "proj123",
            "task_description": "Test task"
        }
        
        create_response = client.post(
            "/api/v1/agent-runs/",
            json=run_data,
            headers=auth_headers
        )
        
        run_id = create_response.json()["run_id"]
        
        # Get the run details
        get_response = client.get(
            f"/api/v1/agent-runs/{run_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["run_id"] == run_id
        assert "status" in data
        assert "task_description" in data

    @pytest.mark.skip(reason="Requires full auth setup")
    def test_cancel_agent_run(self, auth_headers):
        """Test cancelling an active agent run."""
        # Create a run
        run_data = {
            "project_id": "proj123",
            "task_description": "Long running task"
        }
        
        create_response = client.post(
            "/api/v1/agent-runs/",
            json=run_data,
            headers=auth_headers
        )
        
        run_id = create_response.json()["run_id"]
        
        # Cancel the run
        cancel_response = client.post(
            f"/api/v1/agent-runs/{run_id}/cancel",
            headers=auth_headers
        )
        
        assert cancel_response.status_code == 200
        assert "cancelled" in cancel_response.json()["message"].lower()

    @pytest.mark.skip(reason="Requires full auth setup")
    def test_list_agent_runs_with_filters(self, auth_headers):
        """Test listing runs with query parameters."""
        response = client.get(
            "/api/v1/agent-runs/?project_id=proj123&status=completed",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "runs" in data
        assert "total" in data

    def test_get_nonexistent_run_unauthorized(self):
        """Test getting a nonexistent run without auth."""
        response = client.get("/api/v1/agent-runs/nonexistent-id")
        assert response.status_code == 401

    @pytest.mark.skip(reason="Requires full auth setup")
    def test_get_nonexistent_run(self, auth_headers):
        """Test getting a nonexistent run."""
        response = client.get(
            "/api/v1/agent-runs/nonexistent-id",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestWebSocketEndpoint:
    @pytest.mark.skip(reason="Requires async test client setup")
    def test_websocket_connection(self):
        """Test WebSocket connection to agent run."""
        # This would require starlette's TestClient with WebSocket support
        pass

    @pytest.mark.skip(reason="Requires async test client setup")
    def test_websocket_auth_required(self):
        """Test that WebSocket requires authentication."""
        # Test unauthenticated WebSocket connection
        pass
