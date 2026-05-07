"""
WebSocket Manager for real-time agent monitoring and streaming.
Handles connection lifecycle, broadcasting, and message routing.
"""
import asyncio
import json
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger


class ConnectionManager:
    def __init__(self):
        # Map of run_id -> list of active connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Map of user_id -> list of active connections (for personal notifications)
        self.user_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, run_id: Optional[str] = None, user_id: Optional[str] = None):
        await websocket.accept()
        
        if run_id:
            if run_id not in self.active_connections:
                self.active_connections[run_id] = []
            self.active_connections[run_id].append(websocket)
            logger.info(f"Client connected to run_id: {run_id}")
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
            logger.info(f"Client connected to user_id: {user_id}")

    def disconnect(self, websocket: WebSocket, run_id: Optional[str] = None, user_id: Optional[str] = None):
        if run_id and run_id in self.active_connections:
            if websocket in self.active_connections[run_id]:
                self.active_connections[run_id].remove(websocket)
                if not self.active_connections[run_id]:
                    del self.active_connections[run_id]
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
        
        logger.info("Client disconnected")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_run(self, message: dict, run_id: str):
        """Send message to all clients listening to a specific agent run."""
        if run_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[run_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to connection: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn, run_id=run_id)

    async def broadcast_to_user(self, message: dict, user_id: str):
        """Send message to all clients belonging to a specific user."""
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user connection: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn, user_id=user_id)

    async def send_agent_update(self, run_id: str, agent_name: str, status: str, data: Optional[dict] = None):
        """Standardized method to send agent state updates."""
        message = {
            "type": "agent_update",
            "run_id": run_id,
            "agent_name": agent_name,
            "status": status,
            "timestamp": asyncio.get_event_loop().time(),
            "data": data or {}
        }
        await self.broadcast_to_run(message, run_id)

    async def send_log(self, run_id: str, level: str, message: str):
        """Send log messages to the frontend."""
        payload = {
            "type": "log",
            "run_id": run_id,
            "level": level,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_run(payload, run_id)


manager = ConnectionManager()
