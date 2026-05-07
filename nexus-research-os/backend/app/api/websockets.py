"""
WebSocket routes for real-time agent monitoring and streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from app.websocket_manager import manager
from app.core.security import get_current_user_ws
from app.models.user import User
from loguru import logger

router = APIRouter()


@router.websocket("/ws/agent/{run_id}")
async def agent_websocket_endpoint(
    websocket: WebSocket,
    run_id: str,
    current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time agent run monitoring.
    Clients connect to this endpoint to receive live updates about agent execution.
    """
    await manager.connect(websocket, run_id=run_id, user_id=str(current_user.id))
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection_established",
            "run_id": run_id,
            "message": "Connected to agent run stream"
        }, websocket)
        
        # Keep connection alive and handle incoming messages (if any)
        while True:
            try:
                data = await websocket.receive_text()
                # Handle client messages (e.g., pause, resume, stop commands)
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
                elif message.get("type") == "stop":
                    # TODO: Implement stop logic via task queue
                    logger.info(f"Stop requested for run {run_id} by user {current_user.id}")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, run_id=run_id, user_id=str(current_user.id))
        logger.info(f"Client disconnected from run {run_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, run_id=run_id, user_id=str(current_user.id))


@router.websocket("/ws/user")
async def user_websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for user-specific notifications.
    Receives updates about all runs belonging to the user.
    """
    await manager.connect(websocket, user_id=str(current_user.id))
    
    try:
        await manager.send_personal_message({
            "type": "connection_established",
            "message": "Connected to user notification stream"
        }, websocket)
        
        while True:
            try:
                data = await websocket.receive_text()
                if json.loads(data).get("type") == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in user websocket: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=str(current_user.id))
        logger.info(f"User {current_user.id} disconnected from notification stream")
