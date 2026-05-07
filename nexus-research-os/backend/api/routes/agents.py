"""
Agent API Routes
Endpoints for running agents, streaming results, and tracking progress
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from backend.api.websocket.manager import manager, AgentEventStreamer
from backend.services.agent_orchestrator import get_agent_orchestrator
from backend.models.database import get_db_session
from backend.models.agent_run import AgentRun, RunStatus
from backend.auth.dependencies import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

class AgentRunRequest(BaseModel):
    task: str
    agent_type: str = "research_assistant"
    domain: str = "general"
    parameters: Optional[Dict[str, Any]] = None
    
class AgentRunResponse(BaseModel):
    run_id: str
    status: str
    created_at: datetime
    
@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Start a new agent run"""
    run_id = str(uuid.uuid4())
    
    try:
        # Create database record
        db = next(get_db_session())
        agent_run = AgentRun(
            id=run_id,
            user_id=current_user.id,
            task=request.task,
            agent_type=request.agent_type,
            domain=request.domain,
            parameters=request.parameters or {},
            status=RunStatus.PENDING
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)
        db.close()
        
        # Start agent execution in background
        background_tasks.add_task(
            execute_agent_task,
            run_id=run_id,
            task=request.task,
            agent_type=request.agent_type,
            domain=request.domain,
            parameters=request.parameters or {},
            user_id=current_user.id
        )
        
        return AgentRunResponse(
            run_id=run_id,
            status=RunStatus.PENDING.value,
            created_at=agent_run.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

async def execute_agent_task(
    run_id: str,
    task: str,
    agent_type: str,
    domain: str,
    parameters: Dict[str, Any],
    user_id: str
):
    """Execute agent task in background"""
    db = next(get_db_session())
    streamer = AgentEventStreamer(run_id, user_id)
    
    try:
        # Update status to running
        agent_run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if not agent_run:
            return
        agent_run.status = RunStatus.RUNNING
        db.commit()
        
        await streamer.stream_event("status_update", {"status": "running"})
        
        # Get orchestrator and execute
        orchestrator = get_agent_orchestrator()
        
        # Execute with streaming
        result = await orchestrator.execute_with_streaming(
            task=task,
            agent_type=agent_type,
            domain=domain,
            parameters=parameters,
            streamer=streamer
        )
        
        # Update status to completed
        agent_run.status = RunStatus.COMPLETED
        agent_run.result = result
        agent_run.completed_at = datetime.utcnow()
        db.commit()
        
        await streamer.stream_complete()
        await streamer.stream_event("status_update", {"status": "completed"})
        
    except Exception as e:
        # Update status to failed
        agent_run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if agent_run:
            agent_run.status = RunStatus.FAILED
            agent_run.error_message = str(e)
            db.commit()
            
        await streamer.stream_error(str(e))
        await streamer.stream_event("status_update", {"status": "failed"})
        
    finally:
        db.close()

@router.get("/{run_id}")
async def get_agent_run(
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get status and results of an agent run"""
    db = next(get_db_session())
    try:
        agent_run = db.query(AgentRun).filter(
            AgentRun.id == run_id,
            AgentRun.user_id == current_user.id
        ).first()
        
        if not agent_run:
            raise HTTPException(status_code=404, detail="Agent run not found")
            
        return {
            "run_id": agent_run.id,
            "status": agent_run.status.value,
            "task": agent_run.task,
            "agent_type": agent_run.agent_type,
            "domain": agent_run.domain,
            "created_at": agent_run.created_at,
            "completed_at": agent_run.completed_at,
            "result": agent_run.result,
            "error_message": agent_run.error_message
        }
    finally:
        db.close()

@router.get("/")
async def list_agent_runs(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List agent runs for current user"""
    db = next(get_db_session())
    try:
        query = db.query(AgentRun).filter(AgentRun.user_id == current_user.id)
        
        if status:
            query = query.filter(AgentRun.status == status)
            
        runs = query.order_by(AgentRun.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "runs": [
                {
                    "run_id": run.id,
                    "status": run.status.value,
                    "task": run.task,
                    "agent_type": run.agent_type,
                    "created_at": run.created_at,
                    "completed_at": run.completed_at
                }
                for run in runs
            ],
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
    finally:
        db.close()

@router.websocket("/ws/{run_id}")
async def agent_websocket(
    websocket: WebSocket,
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time agent monitoring"""
    await manager.connect(websocket, current_user.id)
    manager.subscribe_to_agent(run_id, current_user.id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "run_id": run_id,
            "message": "Connected to agent stream"
        })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, current_user.id)
        manager.unsubscribe_from_agent(run_id, current_user.id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, current_user.id)
        manager.unsubscribe_from_agent(run_id, current_user.id)

@router.delete("/{run_id}")
async def cancel_agent_run(
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a running agent"""
    db = next(get_db_session())
    try:
        agent_run = db.query(AgentRun).filter(
            AgentRun.id == run_id,
            AgentRun.user_id == current_user.id
        ).first()
        
        if not agent_run:
            raise HTTPException(status_code=404, detail="Agent run not found")
            
        if agent_run.status not in [RunStatus.PENDING, RunStatus.RUNNING]:
            raise HTTPException(status_code=400, detail="Can only cancel pending or running agents")
            
        agent_run.status = RunStatus.CANCELLED
        db.commit()
        
        # Notify via WebSocket
        await manager.broadcast_agent_event(run_id, {
            "event_type": "cancelled",
            "message": "Agent run cancelled by user"
        })
        
        return {"message": "Agent run cancelled", "run_id": run_id}
    finally:
        db.close()
