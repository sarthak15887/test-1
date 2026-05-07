"""
Unit tests for WebSocket manager.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.websocket_manager import ConnectionManager


class TestConnectionManager:
    @pytest.fixture
    def manager(self):
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_with_run_id(self, manager, mock_websocket):
        await manager.connect(mock_websocket, run_id="run123")
        
        mock_websocket.accept.assert_called_once()
        assert "run123" in manager.active_connections
        assert mock_websocket in manager.active_connections["run123"]

    @pytest.mark.asyncio
    async def test_connect_with_user_id(self, manager, mock_websocket):
        await manager.connect(mock_websocket, user_id="user456")
        
        mock_websocket.accept.assert_called_once()
        assert "user456" in manager.user_connections
        assert mock_websocket in manager.user_connections["user456"]

    @pytest.mark.asyncio
    async def test_connect_with_both_ids(self, manager, mock_websocket):
        await manager.connect(mock_websocket, run_id="run123", user_id="user456")
        
        assert "run123" in manager.active_connections
        assert "user456" in manager.user_connections

    @pytest.mark.asyncio
    async def test_disconnect_from_run(self, manager, mock_websocket):
        await manager.connect(mock_websocket, run_id="run123")
        manager.disconnect(mock_websocket, run_id="run123")
        
        assert "run123" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_from_user(self, manager, mock_websocket):
        await manager.connect(mock_websocket, user_id="user456")
        manager.disconnect(mock_websocket, user_id="user456")
        
        assert "user456" not in manager.user_connections

    @pytest.mark.asyncio
    async def test_send_personal_message(self, manager, mock_websocket):
        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, mock_websocket)
        
        mock_websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_run(self, manager, mock_websocket):
        # Connect multiple clients to same run
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await manager.connect(ws1, run_id="run123")
        await manager.connect(ws2, run_id="run123")
        
        message = {"type": "broadcast", "data": "test"}
        await manager.broadcast_to_run(message, "run123")
        
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, manager, mock_websocket):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await manager.connect(ws1, user_id="user456")
        await manager.connect(ws2, user_id="user456")
        
        message = {"type": "notification", "data": "alert"}
        await manager.broadcast_to_user(message, "user456")
        
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_handles_disconnected_clients(self, manager):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json = AsyncMock(side_effect=Exception("Connection lost"))
        
        await manager.connect(ws1, run_id="run123")
        await manager.connect(ws2, run_id="run123")
        
        message = {"type": "test"}
        await manager.broadcast_to_run(message, "run123")
        
        # ws1 should receive message
        ws1.send_json.assert_called_once()
        # ws2 should be removed from connections
        assert ws2 not in manager.active_connections.get("run123", [])

    @pytest.mark.asyncio
    async def test_send_agent_update(self, manager, mock_websocket):
        await manager.connect(mock_websocket, run_id="run123")
        
        await manager.send_agent_update(
            run_id="run123",
            agent_name="chief_scientist",
            status="running",
            data={"progress": 50}
        )
        
        assert mock_websocket.send_json.called
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "agent_update"
        assert call_args["agent_name"] == "chief_scientist"
        assert call_args["status"] == "running"
        assert call_args["data"]["progress"] == 50

    @pytest.mark.asyncio
    async def test_send_log(self, manager, mock_websocket):
        await manager.connect(mock_websocket, run_id="run123")
        
        await manager.send_log("run123", "INFO", "Test log message")
        
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "log"
        assert call_args["level"] == "INFO"
        assert call_args["message"] == "Test log message"

    @pytest.mark.asyncio
    async def test_broadcast_to_nonexistent_run(self, manager, mock_websocket):
        # Should not raise error
        message = {"type": "test"}
        await manager.broadcast_to_run(message, "nonexistent")
        
        # No calls should be made
        mock_websocket.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_connections_same_run(self, manager):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()
        
        await manager.connect(ws1, run_id="run123")
        await manager.connect(ws2, run_id="run123")
        await manager.connect(ws3, run_id="run123")
        
        assert len(manager.active_connections["run123"]) == 3
        
        manager.disconnect(ws2, run_id="run123")
        assert len(manager.active_connections["run123"]) == 2
        assert ws2 not in manager.active_connections["run123"]
