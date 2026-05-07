"""
WebSocket Manager for Real-time Agent Monitoring
Handles WebSocket connections and streaming of agent events
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # user_id -> [websocket]
        self.agent_subscriptions: Dict[str, set] = {}  # run_id -> {user_ids}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"New WebSocket connection for user {user_id}")
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
        
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections for a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    
    async def broadcast_agent_event(self, run_id: str, event: dict):
        """Broadcast agent event to all subscribed users"""
        if run_id in self.agent_subscriptions:
            for user_id in self.agent_subscriptions[run_id]:
                message = {
                    "type": "agent_event",
                    "run_id": run_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": event
                }
                await self.send_personal_message(message, user_id)
                
    def subscribe_to_agent(self, run_id: str, user_id: str):
        """Subscribe a user to agent run events"""
        if run_id not in self.agent_subscriptions:
            self.agent_subscriptions[run_id] = set()
        self.agent_subscriptions[run_id].add(user_id)
        logger.info(f"User {user_id} subscribed to agent run {run_id}")
        
    def unsubscribe_from_agent(self, run_id: str, user_id: str):
        """Unsubscribe a user from agent run events"""
        if run_id in self.agent_subscriptions:
            self.agent_subscriptions[run_id].discard(user_id)
            if not self.agent_subscriptions[run_id]:
                del self.agent_subscriptions[run_id]
        logger.info(f"User {user_id} unsubscribed from agent run {run_id}")
        
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)

# Global manager instance
manager = ConnectionManager()

class AgentEventStreamer:
    """Helper class to stream agent events via WebSocket"""
    
    def __init__(self, run_id: str, user_id: str):
        self.run_id = run_id
        self.user_id = user_id
        
    async def stream_event(self, event_type: str, data: Any):
        """Stream an agent event"""
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_agent_event(self.run_id, event)
        
    async def stream_thought(self, thought: str):
        await self.stream_event("thought", {"thought": thought})
        
    async def stream_action(self, action: str, params: dict):
        await self.stream_event("action", {"action": action, "params": params})
        
    async def stream_observation(self, observation: str):
        await self.stream_event("observation", {"observation": observation})
        
    async def stream_result(self, result: Any):
        await self.stream_event("result", {"result": result})
        
    async def stream_error(self, error: str):
        await self.stream_event("error", {"error": error})
        
    async def stream_complete(self):
        await self.stream_event("complete", {})

def get_connection_manager() -> ConnectionManager:
    return manager
