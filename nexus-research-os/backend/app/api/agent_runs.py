"""
Agent Run API endpoints for starting, monitoring, and managing agent executions.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel

from app.core.security import get_current_user, TokenData
from app.services.agent_execution import agent_execution_service
from app.models.agent_run import AgentRun, RunStatus


router = APIRouter(prefix="/agent-runs", tags=["Agent Runs"])


class AgentRunRequest(BaseModel):
    project_id: str
    task_description: str
    config: Optional[dict] = None


class AgentRunResponse(BaseModel):
    run_id: str
    status: RunStatus
    message: str


@router.post("/", response_model=AgentRunResponse)
async def create_agent_run(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Start a new agent run with the specified task.
    Returns immediately with the run ID for tracking.
    """
    try:
        run = await agent_execution_service.start_agent_run(
            user_id=current_user.user_id,
            project_id=request.project_id,
            task_description=request.task_description,
            agent_config=request.config
        )
        
        return AgentRunResponse(
            run_id=run.id,
            status=run.status,
            message="Agent run started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{run_id}")
async def get_agent_run(
    run_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get the current status and details of an agent run."""
    run = agent_execution_service.get_run_status(run_id)
    
    if not run:
        # In production, fetch from database
        raise HTTPException(status_code=404, detail="Run not found or completed")
    
    return {
        "run_id": run.id,
        "status": run.status,
        "task_description": run.task_description,
        "steps": [step.dict() for step in run.steps],
        "result": run.result,
        "error_message": run.error_message,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
        "completed_at": run.completed_at
    }


@router.post("/{run_id}/cancel")
async def cancel_agent_run(
    run_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Cancel an active agent run."""
    success = agent_execution_service.cancel_run(run_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Run not found or already completed")
    
    return {"message": "Agent run cancelled successfully"}


@router.get("/")
async def list_agent_runs(
    project_id: Optional[str] = None,
    status: Optional[RunStatus] = None,
    limit: int = 20,
    current_user: TokenData = Depends(get_current_user)
):
    """List agent runs for the current user."""
    # In production, query from database with filters
    # This is a placeholder implementation
    return {
        "runs": [],
        "total": 0,
        "message": "Use database query in production"
    }
